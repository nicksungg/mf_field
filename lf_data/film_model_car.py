import torch
import torch.nn as nn

class FiLMModulation(nn.Module):
    def __init__(self, cond_dim, hidden_dim=256, num_layers=4):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_mod_params = 2 * hidden_dim * (num_layers - 1)
        
        # Using SiLU for smoother mappings in continuous spaces
        self.net = nn.Sequential(
            nn.Linear(cond_dim, 256),
            nn.SiLU(),
            nn.Linear(256, 256),
            nn.SiLU(),
        )
        self.out_layer = nn.Linear(256, self.num_mod_params)
        
        # Zero-init ensures gamma=0, beta=0 at the start of training
        nn.init.zeros_(self.out_layer.weight)
        nn.init.zeros_(self.out_layer.bias)

    def forward(self, cond):
        # cond: (B, 23)
        feat = self.net(cond)
        out = self.out_layer(feat) # (B, num_mod_params)
        
        chunk_size = self.hidden_dim * (self.num_layers - 1)
        gamma = out[:, :chunk_size]
        beta  = out[:, chunk_size:]
        return gamma, beta


class ModulatedMLP(nn.Module):
    def __init__(self, input_dim=2, output_dim=1, hidden_dim=256,
                 num_layers=4, extra_layers=3):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        for _ in range(num_layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))

        self.extra = nn.ModuleList()
        for _ in range(extra_layers):
            self.extra.append(nn.Linear(hidden_dim, hidden_dim))

        self.output_layer = nn.Linear(hidden_dim, output_dim)

    def forward(self, coords, gamma, beta):
        # coords: (B, N, 2)
        # gamma, beta: (B, chunk_size)
        
        chunk = self.hidden_dim
        h = coords
        
        for i in range(self.num_layers - 1):
            h = self.layers[i](h) # (B, N, hidden_dim)
            h = torch.relu(h)
            
            # Slice the parameters for this specific layer
            # and add an unsqueezed dimension for broadcasting over N points
            g_i = gamma[:, i * chunk : (i + 1) * chunk].unsqueeze(1) # (B, 1, hidden_dim)
            b_i = beta[:,  i * chunk : (i + 1) * chunk].unsqueeze(1) # (B, 1, hidden_dim)
            
            # Apply FiLM with identity mapping: (1 + gamma) * h + beta
            h = (1.0 + g_i) * h + b_i

        for layer in self.extra:
            h = torch.relu(layer(h))

        return self.output_layer(h) # (B, N, 1)


class FiLMNet(nn.Module):
    def __init__(self, cond_dim=23, coord_dim=2, output_dim=1,
                 hidden_dim=256, num_layers=4, extra_layers=3):
        super().__init__()
        self.modulation_net = FiLMModulation(cond_dim, hidden_dim, num_layers)
        self.mlp = ModulatedMLP(coord_dim, output_dim, hidden_dim,
                                num_layers, extra_layers)

    def forward(self, coords, cond):
        # coords: (B, N, 2), cond: (B, 23)
        gamma, beta = self.modulation_net(cond)
        return self.mlp(coords, gamma, beta)
