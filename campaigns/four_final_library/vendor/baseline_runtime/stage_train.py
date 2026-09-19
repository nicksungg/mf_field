"""The existing AdamW/cosine recipe with resumable, per-stage checkpoints."""
import os
import re
import time
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from baseline_common import write_json


class StageTrainer:
    def __init__(self,folder,identity):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.identity=identity

    def __call__(self,model,X,Y,scaler,epochs,lr,p,device,tag=None,seed=None,aug=None):
        if not len(X) or epochs<=0:return
        name=tag or (f'aug_seed{seed}' if aug is not None else f'plain_seed{seed}')
        path=self.folder/(re.sub('[^a-zA-Z0-9_-]','_',name)+'.pt')
        key=dict(identity=self.identity,stage=name,epochs=int(epochs),lr=float(lr),
                 scaler=float(scaler),x_shape=list(X.shape),y_shape=list(Y.shape),settings=p,
                 permutation_seed=0 if seed is None else int(seed))
        opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=p['weight_decay'])
        sched=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=max(epochs,1),eta_min=1e-6)
        g=torch.Generator().manual_seed(key['permutation_seed'])
        start,spent=0,0.
        if path.exists():
            state=torch.load(path,map_location=device,weights_only=False)
            assert state['key']==key,'Checkpoint/data configuration mismatch'
            model.load_state_dict(state['model']);opt.load_state_dict(state['optimizer'])
            sched.load_state_dict(state['scheduler']);g.set_state(state['generator'].cpu())
            torch.set_rng_state(state['torch_rng'].cpu())
            if torch.cuda.is_available():torch.cuda.set_rng_state_all([a.cpu() for a in state['cuda_rng']])
            np.random.set_state(state['numpy_rng']);start=state['epoch'];spent=state['seconds']
            print('RESUME',name,start,'/',epochs,flush=True)
            del state
        if start==epochs:return
        xt=torch.from_numpy(X).float();yt=torch.from_numpy(Y).float()/scaler
        at=None if aug is None else torch.from_numpy(aug).float()
        bs=min(p['batch_size'],len(X));clock=time.time();saved=clock
        for ep in range(start,epochs):
            model.train();perm=torch.randperm(len(X),generator=g);total=0.;batches=0
            for i in range(0,len(X),bs):
                idx=perm[i:i+bs];xb=xt[idx].to(device);yb=yt[idx].to(device)
                opt.zero_grad(set_to_none=True)
                prediction=model(xb) if at is None else model(xb,at[idx].to(device))
                loss=F.mse_loss(prediction,yb)
                if not torch.isfinite(loss):raise RuntimeError(f'Nonfinite loss: {name} epoch {ep}')
                loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),p['grad_clip']);opt.step()
                total+=float(loss.detach());batches+=1
            sched.step()
            if (ep+1)%25==0 or time.time()-saved>=300 or ep+1==epochs:
                temp=path.with_name(path.name+f'.tmp.{os.getpid()}')
                torch.save(dict(key=key,epoch=ep+1,seconds=spent+time.time()-clock,
                    model=model.state_dict(),optimizer=opt.state_dict(),scheduler=sched.state_dict(),
                    generator=g.get_state(),torch_rng=torch.get_rng_state(),
                    cuda_rng=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
                    numpy_rng=np.random.get_state()),temp)
                os.replace(temp,path);saved=time.time()
                write_json(path.with_suffix('.json'),dict(stage=name,epoch=ep+1,epochs=epochs,
                    train_mse=total/batches,seconds=spent+time.time()-clock))
                print(name,ep+1,'/',epochs,'MSE',total/batches,flush=True)

    def augmented(self,model,X,aug,target,scaler,epochs,lr,p,device,seed):
        return self(model,X,target,scaler,epochs,lr,p,device,seed=seed,aug=aug)
