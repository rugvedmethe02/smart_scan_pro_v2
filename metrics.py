class Metrics:
 def __init__(self): self.scans=self.hits=self.misses=self.pc=self.pt=0
 def scan(self,h): self.scans+=1; self.hits+=int(h); self.misses+=int(not h)
 def pred(self,p,a): self.pc+=int((p>=.5)==bool(a)); self.pt+=1
 @property
 def detection(self): return self.hits/self.scans if self.scans else 0
 @property
 def miss(self): return self.misses/self.scans if self.scans else 0
 @property
 def accuracy(self): return self.pc/self.pt if self.pt else 0
