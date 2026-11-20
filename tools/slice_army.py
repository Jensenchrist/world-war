import sys
from PIL import Image;import numpy as np,scipy.ndimage as nd,cv2
path,code=sys.argv[1],sys.argv[2]
src=np.asarray(Image.open(path).convert('RGB'))
m=src.astype(int).sum(2)>70
lab,n=nd.label(m);sl=nd.find_objects(lab)
bs=sorted([(s[0].start,s[0].stop,s[1].start,s[1].stop) for s in sl if (s[0].stop-s[0].start)>200],key=lambda b:(b[0]//200,b[2]))
assert len(bs)==9,bs
keys=['2','3','4','5','6','7','8','9','10']
for k,(y0,y1,x0,x1) in zip(keys,bs):
    t=src[y0:y1,x0:x1].copy()
    dark=t.astype(int).sum(2)<70
    lab2,_=nd.label(dark);edge=set(np.unique(np.concatenate([lab2[0],lab2[-1],lab2[:,0],lab2[:,-1]])))-{0}
    a=cv2.GaussianBlur((~np.isin(lab2,list(edge))).astype(np.float32),(0,0),.9)
    hsv=cv2.cvtColor(t,cv2.COLOR_RGB2HSV).astype(np.float32);h=hsv[...,0];d=np.minimum(h,180-h)
    reg=np.zeros(a.shape,bool);H,W=a.shape;reg[:int(H*.32),int(W*.62):]=True
    w=np.clip((9-d)/4,0,1)*np.clip((hsv[...,1]-110)/50,0,1)*reg
    g=hsv.copy();g[...,0]=62;g[...,2]*=.8
    gr=cv2.cvtColor(g.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)
    t=(t*(1-w[...,None])+gr*w[...,None]).astype(np.uint8)
    im=Image.fromarray(np.dstack([t,(a*255).astype(np.uint8)]))
    im=im.resize((360,int(360*H/W)),Image.LANCZOS);im.save(f'site3/pecas/{code}_{k}.webp',quality=86,method=6)
c=Image.new('RGBA',(9*180,160),(25,35,25,255))
for i,k in enumerate(keys):c.alpha_composite(Image.open(f'site3/pecas/{code}_{k}.webp').resize((176,150)),(i*180,4))
c.save(f'/tmp/{code}.png');print('ok')
