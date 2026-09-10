from config import HIT_REWARD,MISS_REWARD,SCAN_COST
class FeedbackLearner:
 def __init__(self): self.hits=0; self.misses=0; self.total_reward=0
 def update(self,hit):
  r=(HIT_REWARD if hit else MISS_REWARD)-SCAN_COST; self.hits+=int(hit); self.misses+=int(not hit); self.total_reward+=r; return r
 def reset(self): self.__init__()
