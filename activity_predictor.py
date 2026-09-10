import numpy as np
from config import NUM_BANDS,PREDICTOR_DECAY
class ActivityPredictor:
 def __init__(self): self.alpha=np.ones(NUM_BANDS); self.beta=np.ones(NUM_BANDS)
 def predict(self): return self.alpha/(self.alpha+self.beta)
 def update_feedback(self,b,hit):
  self.alpha[b]*=PREDICTOR_DECAY; self.beta[b]*=PREDICTOR_DECAY
  (self.alpha if hit else self.beta)[b]+=1.0
 def reset(self): self.alpha.fill(1); self.beta.fill(1)
