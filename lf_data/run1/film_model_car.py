import torch
import torch.nn as nn


class FiLMModulation(nn.Module):
    """
    Maps the condition vector (geometric parameters) to FiLM
    scaling (gamma) and shifting (beta) parameters.
    """
    def __init__(self, cond_dim, hidden_dim=256, num_layers=4):
        super().__init__()
        self.cond_dim = cond_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_mod_params = 2 * hidden_dim * (num_layers - 1)
        self.fc = nn.Sequential(
            nn.Linear(cond_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, self.num_mod_params),
        )

    def forward(self, cond):
        out = self.fc(cond)
        chunk_size = self.hidden_dim * (self.num_layers - 1)
        gamma = out[:, :chunk_size]
        beta  = out[:, chunk_size:]
        return gamma, beta


class ModulatedMLP(nn.Module):
    """
    MLP mapping 2D surface coordinates -> surface pressure (scalar).
    FiLM modulation applied after each hidden layer, then extra
    non-modulated layers for expressiveness.
    """
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
        chunk = self.hidden_dim
        h = coords
        for i in range(self.num_layers - 1):
            h = self.layers[i](h)
            h = torch.relu(h)
            g_i = gamma[:, i * chunk:(i + 1) * chunk]
            b_i = beta[:,  i * chunk:(i + 1) * chunk]
            h = g_i * h + b_i

        for layer in self.extra:
            h = torch.relu(layer(h))

        return self.output_layer(h)


class FiLMNet(nn.Module):
    """
    FiLM-conditioned network for car surface pressure prediction.
      coords  : (B, 2)   – normalised 2D surface coordinates
      cond    : (B, 23)  – normalised geometric parameters
      output  : (B, 1)   – predicted surface pressure
    """
    def __init__(self, cond_dim=23, coord_dim=2, output_dim=1,
                 hidden_dim=256, num_layers=4, extra_layers=3):
        super().__init__()
        self.modulation_net = FiLMModulation(cond_dim, hidden_dim, num_layers)
        self.mlp = ModulatedMLP(coord_dim, output_dim, hidden_dim,
                                num_layers, extra_layers)

    def forward(self, coords, cond):
        gamma, beta = self.modulation_net(cond)
        return self.mlp(coords, gamma, beta)
