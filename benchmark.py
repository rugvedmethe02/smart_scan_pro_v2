import pandas as pd
from pdw_database import PDWDatabase
from activity_predictor import ActivityPredictor
from feedback_learner import FeedbackLearner
from metrics import Metrics
from smart_scheduler import SmartScheduler,SequentialScheduler,RandomScheduler
from config import DEFAULT_BENCHMARK_SCANS,DEFAULT_SEED
def run(name,db,n,seed):
 pred=ActivityPredictor(); fb=FeedbackLearner(); m=Metrics(); sch={'Sequential':SequentialScheduler(),'Random':RandomScheduler(seed),'Smart':SmartScheduler(seed)}[name]
 for t in range(n):
  p=pred.predict(); b,mode=sch.select_band(p); hit=db.scan_band(t,b); fb.update(hit); m.scan(hit); m.pred(p[b],hit)
  if name=='Smart': pred.update_feedback(b,hit)
 return {'Strategy':name,'Scans':m.scans,'Hits':m.hits,'Misses':m.misses,'Detection Rate (%)':round(m.detection*100,2),'Miss Rate (%)':round(m.miss*100,2),'Prediction Accuracy (%)':round(m.accuracy*100,2),'Scan Efficiency (%)':round(m.detection*100,2),'Average Reward':round(fb.total_reward/max(1,m.scans),4),'Scans / Hit':round(m.scans/m.hits,2) if m.hits else None}
def run_benchmark(scans=DEFAULT_BENCHMARK_SCANS,seed=DEFAULT_SEED):
 db=PDWDatabase(); df=pd.DataFrame([run(x,db,min(scans,len(db.data.time_slot.unique())),seed) for x in ('Sequential','Random','Smart')]); df.to_csv('data/benchmark_results.csv',index=False); return df
if __name__=='__main__': print(run_benchmark().to_string(index=False))
