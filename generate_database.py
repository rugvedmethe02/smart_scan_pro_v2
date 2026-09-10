from pathlib import Path
import numpy as np, pandas as pd
from config import *

def state(e,t,rng):
    if e==0:return ((t//6)%2==0),1
    if e==1:return True,6
    if e==2:return True,[0,2,5,3,7,4][t%6]
    if e==3:return (t%18)<6,2
    if e==4:return True,int(rng.choice(np.arange(NUM_BANDS),p=[.04,.16,.25,.08,.12,.16,.15,.04]))
    return ((t%20)<10 or (t%7 in (0,1))), (4 if (t%20)<10 else 0)

def generate(seed=DEFAULT_SEED):
    rng=np.random.default_rng(seed); rows=[]; pid=0
    for t in range(NUM_TIME_SLOTS):
      for e in range(NUM_EMITTERS):
        active,b=state(e,t,rng)
        if not active: continue
        lo,hi=BAND_RANGES_MHZ[b]; n=int(rng.integers(4,13)); aoa0=(20+27*e)%170; amp0=42+6*e
        for _ in range(n):
          rows.append(dict(pdw_id=pid,time_slot=t,toa=t+float(rng.uniform(.02,.98)),centre_frequency=float(rng.uniform(lo+8,hi-8)),pulse_width=float(rng.uniform(.5,3.2)),aoa=float(np.clip(aoa0+rng.normal(0,2.5),0,180)),amplitude=float(np.clip(amp0+rng.normal(0,4),20,100)),emitter_id=e,band=b,active=1)); pid+=1
    df=pd.DataFrame(rows); Path('data').mkdir(exist_ok=True); df.to_csv('data/synthetic_pdws.csv',index=False); return df
if __name__=='__main__':
    d=generate(); print(f'Generated {len(d):,} PDWs | {d.emitter_id.nunique()} emitters | {d.time_slot.nunique()} time slots')
