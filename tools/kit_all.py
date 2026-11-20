from PIL import Image;import numpy as np,scipy.ndimage as nd,cv2
U='/mnt/user-data/uploads/'
OUT='site3/pecas/'
def cards(path,expect):
    src=np.asarray(Image.open(U+path).convert('RGB'))
    m=src.astype(int).sum(2)>70
    for it in (0,3,6,10):
        mm=nd.binary_erosion(m,iterations=it) if it else m
        lab,n=nd.label(mm);sl=nd.find_objects(lab)
        bs=[(max(0,s[0].start-it),s[0].stop+it,max(0,s[1].start-it),s[1].stop+it) for s in sl if (s[0].stop-s[0].start)>150 and (s[1].stop-s[1].start)>150]
        if len(bs)==expect:break
    bs=sorted(bs,key=lambda b:(round(b[0]/150),b[2]))
    assert len(bs)==expect,(path,len(bs),bs)
    out=[]
    for (y0,y1,x0,x1) in bs:
        t=src[y0:y1,x0:x1].copy()
        dark=t.astype(int).sum(2)<70
        lab2,_=nd.label(dark);edge=set(np.unique(np.concatenate([lab2[0],lab2[-1],lab2[:,0],lab2[:,-1]])))-{0}
        a=cv2.GaussianBlur((~np.isin(lab2,list(edge))).astype(np.float32),(0,0),.9)
        out.append((t,a))
    return out
def green_badge(t):
    H,W=t.shape[:2];hsv=cv2.cvtColor(t,cv2.COLOR_RGB2HSV).astype(np.float32);h=hsv[...,0];d=np.minimum(h,180-h)
    reg=np.zeros((H,W),bool);reg[int(H*.06):int(H*.26),int(W*.75):int(W*.92)]=True
    w=np.clip((9-d)/4,0,1)*np.clip((hsv[...,1]-110)/50,0,1)*reg
    g=hsv.copy();g[...,0]=62;g[...,2]*=.8
    gr=cv2.cvtColor(g.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)
    return (t*(1-w[...,None])+gr*w[...,None]).astype(np.uint8)
def save(t,a,name):
    H,W=a.shape;im=Image.fromarray(np.dstack([t,(a*255).astype(np.uint8)]))
    im=im.resize((360,int(360*H/W)),Image.LANCZOS);im.save(OUT+name+'.webp',quality=85,method=6);return im.size
def grid_cards(path,cols,rows,count):
    src=np.asarray(Image.open(U+path).convert('RGB'));out=[]
    for (y0,y1) in rows:
        for (x0,x1) in cols:
            if len(out)==count:break
            cell=src[y0:y1,x0:x1];m=cell.astype(int).sum(2)>70
            m=nd.binary_closing(m,iterations=4);m=nd.binary_fill_holes(m)
            lab,n=nd.label(m);big=lab==np.argmax(np.bincount(lab.ravel())[1:])+1
            ys,xs=np.where(big);t=cell[ys.min():ys.max()+1,xs.min():xs.max()+1].copy()
            a=cv2.GaussianBlur(big[ys.min():ys.max()+1,xs.min():xs.max()+1].astype(np.float32),(0,0),.9)
            out.append((t,a))
    return out
ranks={'5bc2bd7a':'de','7e68eb7f':'bra','02ea6af8':'us','68991e2d':'ar','d156b9ed':'fr','3a2740b8':'ru','a4fcd6a9':'it','ad87e0e0':'nl','37aeb8c7':'jp'}
def segs(v,thr):
    on=v>thr;out=[];i=0
    while i<len(on):
        if on[i]:
            j=i
            while j<len(on) and on[j]:j+=1
            if j-i>100:out.append((max(0,i-2),min(len(on),j+2)))
            i=j
        else:i+=1
    return out
def auto_grid(path,count):
    src=np.asarray(Image.open(U+path).convert('RGB'));m=src.astype(int).sum(2)>70
    cols=segs(m.sum(0),m.shape[0]*.04);rows=segs(m.sum(1),m.shape[1]*.04)
    pv=m.sum(1).astype(float)
    while len(cols)*len(rows)<count:
        i=max(range(len(rows)),key=lambda i:rows[i][1]-rows[i][0]);a,b=rows[i]
        lo,hi=a+int((b-a)*.3),a+int((b-a)*.7);cut=lo+int(np.argmin(pv[lo:hi]))
        rows[i:i+1]=[(a,cut),(cut,b)]
    assert len(cols)*len(rows)>=count,(path,cols,rows)
    return grid_cards(path,cols,rows,count)
for f,code in ranks.items():
    for k,(t,a) in zip(['2','3','4','5','6','7','8','9','10'],auto_grid(f+'-image.png',9)):
        if code!='us':t=green_badge(t)
        save(t,a,f'{code}_{k}')
order=['bra','us','ar','fr','de','ru','jp','cn','nl','it']
for f,k in (('2bc55964','B'),('bed16837','1')):
    for code,(t,a) in zip(order,auto_grid(f+'-image.png',10)):save(t,a,f'{code}_{k}')
fl=grid_cards('5d7b9be4-image.png',[(40,415),(415,770),(770,1122),(1122,1490)],[(0,335),(335,660),(660,1000)],11)
for code,(t,a) in zip(order,fl[:10]):save(t,a,f'{code}_F')
# verso: apagar a palavra VERSO da plaquinha
t,a=fl[10];t=t.copy();H,W=a.shape
box=np.zeros((H,W),bool);box[int(H*.80):int(H*.93),int(W*.2):int(W*.8)]=True
lum=t.astype(int).mean(2);txt=box&(lum<110);txt=nd.binary_dilation(txt,iterations=3)&box
light=t[box&~txt].reshape(-1,3).mean(0)
rs=np.random.RandomState(3);nz=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),2)*8
fill=np.clip(light[None,None,:]+nz[...,None],0,255);soft=cv2.GaussianBlur(txt.astype(np.float32),(0,0),1.5)[...,None]
t=(t*(1-soft)+fill*soft).astype(np.uint8)
print('verso',save(t,a,'verso'))
