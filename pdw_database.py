from pathlib import Path
import pandas as pd
from config import NUM_BANDS
class PDWDatabase:
 def __init__(self,path='data/synthetic_pdws.csv'):
  if not Path(path).exists(): raise FileNotFoundError('Run: python generate_database.py')
  self.data=pd.read_csv(path)
 def get_time_slot(self,t): return self.data[self.data.time_slot==t].copy()
 def get_band_activity(self,t):
  s=self.get_time_slot(t); a={b:0 for b in range(NUM_BANDS)}
  for b in s.band.unique(): a[int(b)]=1
  return a
 def scan_band(self,t,b): return bool(self.get_band_activity(t).get(int(b),0))
 def band_pulse_count(self,t):
  s=self.get_time_slot(t); out={b:0 for b in range(NUM_BANDS)}
  for b,c in s.band.value_counts().items(): out[int(b)]=int(c)
  return out
 def describe(self): return {'pdws':len(self.data),'emitters':self.data.emitter_id.nunique(),'time_slots':self.data.time_slot.nunique(),'bands':self.data.band.nunique()}
