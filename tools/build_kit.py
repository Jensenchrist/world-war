import numpy as np, cv2, scipy.ndimage as nd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src=np.asarray(Image.open('/mnt/user-data/uploads/8c5bf543-image.png').convert('RGB'))
boxes=[(26,510,12,313),(26,510,319,616),(26,510,622,917),(26,510,923,1219),(26,510,1224,1523),
       (535,985,12,271),(535,984,277,524),(535,984,530,776),(535,984,783,1037),(535,984,1044,1281),(535,984,1286,1529)]
keys=['2','3','4','5','6','7','8','9','10','F','B']
W,H=300,500
def cut(b):
    y0,y1,x0,x1=b;t=src[max(0,y0-3):y1+3,max(0,x0-3):x1+3].copy()
    dark=t.astype(int).sum(2)<70
    lab,n=nd.label(dark);edge=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(edge))
    a=(~bg).astype(np.float32);a=cv2.GaussianBlur(a,(0,0),.9)
    ys,xs=np.where(a>.5);t=t[ys.min():ys.max()+1,xs.min():xs.max()+1];a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    im=np.dstack([t,(a*255).astype(np.uint8)])
    return np.asarray(Image.fromarray(im).resize((W,H),Image.LANCZOS))
cards={k:cut(b) for k,b in zip(keys,boxes)}
# --- placa de pergaminho limpa a partir da Bomba (remove granada e texto) ---
def clean_area(img,mask,sig=18):
    rgb=img[...,:3].astype(np.float32);ok=(~mask)&(img[...,3]>250)
    w=ok.astype(np.float32);num=cv2.GaussianBlur(rgb*w[...,None],(0,0),sig);den=cv2.GaussianBlur(w,(0,0),sig)[...,None]
    field=num/np.maximum(den,1e-3)
    rs=np.random.RandomState(5)
    n1=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),.8)*9
    n2=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),10)*60
    n3=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),3)*10
    tex=(n1+n2+n3)[...,None]*np.array([1,.9,.75],np.float32)
    fill=np.clip(field+tex,0,255)
    soft=cv2.GaussianBlur(mask.astype(np.float32),(0,0),3)[...,None]
    out=img.copy();out[...,:3]=(rgb*(1-soft)+fill*soft).astype(np.uint8);return out
bomb=cards['B']
obj=np.zeros((H,W),bool);obj[34:398,26:274]=True
blank=clean_area(bomb,obj,sig=40)
# texto da placa (y ~ 400-470) – cobrir com cor da placa
plate=np.zeros((H,W),bool);plate[402:470,40:262]=True
txt=np.zeros((H,W),bool);txt[388:470,48:254]=True
pr=blank[400:470,40:260,:3].reshape(-1,3).astype(int);light=pr[pr.mean(1)>np.percentile(pr.mean(1),55)].mean(0)
rs=np.random.RandomState(9);tx=cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),6)*14+cv2.GaussianBlur(rs.randn(H,W).astype(np.float32),(0,0),.8)*7
pf=np.clip(light[None,None,:]+tx[...,None],0,255)
soft=cv2.GaussianBlur(txt.astype(np.float32),(0,0),2.5)[...,None]
blank=blank.copy();blank[...,:3]=(blank[...,:3]*(1-soft)+pf*soft).astype(np.uint8)
Image.fromarray(blank).save('/tmp/blank.png')
F_big=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf',40)
F_sm=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf',13)
def plate_text(im,t1,t2):
    d=ImageDraw.Draw(im)
    for t,f,y in ((t1,F_big,404),(t2,F_sm,452)):
        w=d.textlength(t,font=f);d.text(((W-w)/2,y),t,font=f,fill=(32,22,12,255),anchor='lm' if False else None)
    return im
# --- verso ---
back=Image.fromarray(blank.copy())
bk=np.asarray(back).copy();pm=np.zeros((H,W),bool);pm[392:482,22:278]=True;bk=clean_area(bk,pm,sig=30)
back=Image.fromarray(bk);d=ImageDraw.Draw(back)
cx,cy=150,250
ink=(70,48,26,230)
d.ellipse((cx-70,cy-70,cx+70,cy+70),outline=ink,width=5);d.ellipse((cx-58,cy-58,cx+58,cy+58),outline=ink,width=2)
import math
pts=[(cx+52*math.cos(math.radians(-90+i*36))*(1 if i%2==0 else .42),cy+52*math.sin(math.radians(-90+i*36))*(1 if i%2==0 else .42)) for i in range(10)]
d.polygon(pts,fill=ink)
back=back.filter(ImageFilter.GaussianBlur(.4))
cards['back']=np.asarray(back)
# --- espião (provisório): silhueta dourada do token anterior, tom bronze ---
spy=np.asarray(Image.open('/mnt/user-data/uploads/d5c5f405-image.png').convert('RGBA')).astype(np.float32)
g=spy[...,1];inner_m=nd.binary_erosion(spy[...,3]>128,iterations=150);am=np.clip((g-70)/50,0,1)*(spy[...,3]/255)*inner_m
ys,xs=np.where(am>.3);crop=spy[ys.min():ys.max(),xs.min():xs.max()];am=am[ys.min():ys.max(),xs.min():xs.max()]
lum=crop[...,:3].mean(2,keepdims=True)/255
bronze=np.clip(np.concatenate([lum*120+20,lum*95+14,lum*62+8],2),0,255)
fig=Image.fromarray(np.dstack([bronze,am*255]).astype(np.uint8))
sc=min(210/fig.width,300/fig.height);fig=fig.resize((int(fig.width*sc),int(fig.height*sc)),Image.LANCZOS)
spyc=Image.fromarray(blank.copy())
sh=Image.new('RGBA',fig.size,(30,18,8,0));sh.putalpha(fig.getchannel('A').filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*.55)))
ox,oy=(W-fig.width)//2,388-fig.height
spyc.alpha_composite(sh,(ox+4,oy+6));spyc.alpha_composite(fig,(ox,oy))
plate_text(spyc,'ESPIÃO','(AGENTE SECRETO)')
# selo vermelho "1" copiado do soldado
sol=Image.fromarray(cards['2']);badge=np.asarray(sol.crop((222,6,290,78))).copy()
br=badge[...,:3].astype(int);cream=nd.binary_dilation(br[...,1]>95,iterations=2)
inner=np.zeros(cream.shape,bool);inner[8:-8,8:-8]=True
red=br[(~cream)&inner].mean(0)
badge[cream&inner,:3]=red.astype(np.uint8)
bI=Image.fromarray(badge);dd=ImageDraw.Draw(bI);fB=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf',40)
dd.text((34,38),'1',font=fB,fill=(236,214,170,255),anchor='mm')
spyc.alpha_composite(bI,(222,6))
cards['1']=np.asarray(spyc)
Image.fromarray(cards['F']).save('/tmp/flag_full.png')
# --- verde para o inimigo (só vermelhos fortes) ---
def green(img,flag=False):
    reg=np.zeros(img.shape[:2],bool);reg[:int(H*.2),int(W*.68):]=True
    if flag:reg[:int(H*.82),:]=True
    rgb=np.ascontiguousarray(img[...,:3]);hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV).astype(np.float32)
    h=hsv[...,0];d=np.minimum(h,180-h)
    w=np.clip((9-d)/4,0,1)*np.clip((hsv[...,1]-110)/50,0,1)*reg
    g=hsv.copy();g[...,0]=62;g[...,2]*=.8
    grgb=cv2.cvtColor(g.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)
    out=img.copy();out[...,:3]=(rgb*(1-w[...,None])+grgb*w[...,None]).astype(np.uint8);return out
import os;os.makedirs('out',exist_ok=True)
for k,im in cards.items():
    for side,x in (('r',im),('g',green(im,k=='F'))):
        Image.fromarray(x).resize((240,400),Image.LANCZOS).save(f'out/{side}_{k}.webp',quality=86,method=6)
cs=Image.new('RGBA',(13*124,2*206),(25,35,25,255))
for i,k in enumerate(['10','9','8','7','6','5','4','3','2','1','B','F','back']):
    for j,s in enumerate('rg'):cs.alpha_composite(Image.open(f'out/{s}_{k}.webp').resize((120,200)),(i*124+2,j*206+3))
cs.save('/tmp/contact.png')
