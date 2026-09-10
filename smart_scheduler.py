import random, numpy as np
from config import *
class SmartScheduler:
 def __init__(self,seed=42): self.rng=random.Random(seed); self.reset(seed)
 def reset(self,seed=42): self.rng.seed(seed); self.epsilon=INITIAL_EPSILON; self.count=np.zeros(NUM_BANDS,dtype=int)
 def select_band(self,p):
  if self.rng.random()<self.epsilon:
   u=np.flatnonzero(self.count==0); b=int(self.rng.choice(list(u))) if len(u) else int(np.argmax(1-np.abs(p-.5)*2)); mode='EXPLORE'
  else:
   b=int(np.argmax(p+0.08/np.sqrt(self.count+1))); mode='EXPLOIT'
  self.count[b]+=1; self.epsilon=max(MIN_EPSILON,self.epsilon*EPSILON_DECAY); return b,mode
class SequentialScheduler:
 def __init__(self): self.current=0
 def reset(self): self.current=0
 def select_band(self,p=None): b=self.current; self.current=(self.current+1)%NUM_BANDS; return b,'SEQUENTIAL'
class RandomScheduler:
 def __init__(self,seed=42): self.rng=random.Random(seed)
 def reset(self,seed=42): self.rng.seed(seed)
 def select_band(self,p=None): return self.rng.randrange(NUM_BANDS),'RANDOM'
