import numpy as np
from pdw_database import PDWDatabase
from hdbscan_module import PDWDeinterleaver
from activity_predictor import ActivityPredictor
from smart_scheduler import SmartScheduler
from feedback_learner import FeedbackLearner
from metrics import Metrics
from config import NUM_TIME_SLOTS
class SmartScanEngine:
 def __init__(self,seed=42):
  self.seed=seed; self.db=PDWDatabase(); self.clusterer=PDWDeinterleaver(); self.predictor=ActivityPredictor(); self.scheduler=SmartScheduler(seed); self.feedback=FeedbackLearner(); self.metrics=Metrics(); self.reset_state()
 def reset_state(self):
  self.t=0; self.last_band=None; self.last_prob=0; self.last_mode='STANDBY'; self.last_result='READY'; self.last_reward=0; self.clusters=0; self.noise=0; self.log=[]; self.history=[]
 def reset(self): self.__init__(self.seed)
 def step(self):
  p=self.predictor.predict().copy(); b,mode=self.scheduler.select_band(p); hit=self.db.scan_band(self.t,b); r=self.feedback.update(hit); self.metrics.scan(hit); self.metrics.pred(p[b],hit); self.predictor.update_feedback(b,hit); _,self.clusters,self.noise=self.clusterer.cluster(self.db.get_time_slot(self.t)); self.last_band=b; self.last_prob=float(p[b]); self.last_mode=mode; self.last_result='HIT' if hit else 'MISS'; self.last_reward=r; self.history.append((self.t,b,p[b],int(hit),r)); self.log.insert(0,f'T{self.t:03d} | B{b+1} | {mode:<8} | {self.last_result:<4} | R {r:+.2f}'); self.log=self.log[:80]; self.t=(self.t+1)%NUM_TIME_SLOTS; return self.status()
 def status(self):
  p=self.predictor.predict(); return {'time':self.t,'p':p,'last_band':self.last_band,'last_prob':self.last_prob,'mode':self.last_mode,'result':self.last_result,'reward':self.last_reward,'clusters':self.clusters,'noise':self.noise,'pd':self.metrics.detection,'pfa':self.metrics.miss,'acc':self.metrics.accuracy,'eff':self.metrics.detection,'total_reward':self.feedback.total_reward,'avg_reward':self.feedback.total_reward/max(1,self.metrics.scans),'scans':self.metrics.scans,'hits':self.metrics.hits,'epsilon':self.scheduler.epsilon,'log':self.log,'activity':np.array([self.db.get_band_activity(self.t)[b] for b in range(8)]),'db':self.db.describe()}
