import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import torch
from stage_train import StageTrainer

class Resume(unittest.TestCase):
    def test_interrupted_training_replays_optimizer_and_sample_order(self):
        torch.set_num_threads(1);torch.manual_seed(7)
        initial=torch.nn.Linear(2,1)
        x=np.arange(12,dtype=np.float32).reshape(6,2)/10;y=x.sum(1,keepdims=True)
        p=dict(batch_size=4,weight_decay=1e-5,grad_clip=1.)
        with tempfile.TemporaryDirectory() as tmp:
            complete=copy.deepcopy(initial);partial=copy.deepcopy(initial)
            StageTrainer(Path(tmp)/'complete','test')(complete,x,y,1.,30,.01,p,'cpu','stage')
            interrupted=StageTrainer(Path(tmp)/'partial','test')
            with patch('stage_train.write_json',side_effect=RuntimeError('simulated interruption')):
                with self.assertRaisesRegex(RuntimeError,'simulated interruption'):
                    interrupted(partial,x,y,1.,30,.01,p,'cpu','stage')
            # Restart with a newly initialized network, as a new Slurm process would.
            resumed=copy.deepcopy(initial)
            interrupted(resumed,x,y,1.,30,.01,p,'cpu','stage')
            for a,b in zip(complete.parameters(),resumed.parameters()):
                torch.testing.assert_close(a,b,rtol=0,atol=0)

if __name__=='__main__':unittest.main()
