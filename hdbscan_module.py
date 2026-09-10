from sklearn.preprocessing import StandardScaler
import hdbscan
from config import HDBSCAN_MIN_CLUSTER_SIZE,HDBSCAN_MIN_SAMPLES
class PDWDeinterleaver:
 def __init__(self): self.scaler=StandardScaler()
 def cluster(self,pdws):
  if len(pdws)<HDBSCAN_MIN_CLUSTER_SIZE: return pdws.assign(cluster=-1),0,len(pdws)
  x=self.scaler.fit_transform(pdws[['toa','centre_frequency','pulse_width','aoa','amplitude']]); x*= [1.2,1.4,.8,.8,.7]
  labels=hdbscan.HDBSCAN(min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE,min_samples=HDBSCAN_MIN_SAMPLES).fit_predict(x)
  out=pdws.copy(); out['cluster']=labels; valid={int(x) for x in labels if int(x)>=0}
  return out,len(valid),int((labels==-1).sum())
