import sys, types, time, os
sys.path.insert(0, '.')
# stub pdearena.utils (only Timer is used) to avoid pulling pytorch_lightning
fake = types.ModuleType('pdearena.utils')
class Timer:
    def __enter__(self): self._t = time.time(); return self
    def __exit__(self, *a): self.dt = time.time() - self._t
fake.Timer = Timer
pkg = types.ModuleType('pdearena'); pkg.utils = fake
sys.modules['pdearena'] = pkg
sys.modules['pdearena.utils'] = fake

from pdedatagen.pde import Maxwell3D
from pdedatagen.maxwell import generate_trajectories_maxwell

os.makedirs('out_maxwell', exist_ok=True)
pde = Maxwell3D(n=16, n_large=32, nt=4, skip_nt=20, sample_rate=15)
generate_trajectories_maxwell(pde, mode='train', num_samples=2,
                              dirname='out_maxwell', n_parallel=1, seed=42)
