"""Wealthy benefactor restoration: gilded joinery, stone carving, curated planting.
Executed by build_temple.py before material batching; all details are editable meshes.
"""
def line(k,points,r=.016,n=7):
 for a,b in zip(points,points[1:]):tube(k,a,b,r,n=n)
def ring(k,c,r,axis='y',thick=.025,n=32):
 pts=[]
 for i in range(n+1):
  a=i*math.tau/n
  pts.append((c[0]+r*math.cos(a),c[1],c[2]+r*math.sin(a)) if axis=='y' else (c[0]+r*math.cos(a),c[1]+r*math.sin(a),c[2]))
 line(k,pts,thick)
def crest(x,y,z,r=.2,k=gold):
 # Chrysanthemum mon: raised 16-petal metal ornament.
 for i in range(16):
  a=i*math.tau/16
  points=[]
  for j in range(13):
   t=j*math.tau/12;rr=r*(.48+.38*math.cos(t));aa=a+.13*math.sin(t)
   points.append((x+rr*math.cos(aa),y-.008*math.cos(t),z+rr*math.sin(aa)))
  line(k,points,.010,6)
 sphere(k,(x,y-.018,z),(r*.18,.035,r*.18),n=16,lat=8)
 ring(k,(x,y+.008,z),r*.98,thick=.012)
def scroll_panel(x,y,z,w,h,k=gold):
 # Flowing scroll carving in a dark inset, with framed relief and fine veins.
 box(wood,(x,y+.035,z),(w,.09,h))
 for dz in [-h*.5,h*.5]:box(k,(x,y-.025,z+dz),(w,.035,.018))
 for dx in [-w*.5,w*.5]:box(k,(x+dx,y-.025,z),(.019,.035,h))
 for side in [-1,1]:
  pts=[]
  for i in range(45):
   t=i/44;aa=t*math.pi*3.1;rr=h*.40*(1-t*.86)
   pts.append((x+side*(w*.25+rr*math.cos(aa)),y-.043,z+rr*math.sin(aa)))
  line(k,pts,.016)
  for i in range(5):
   xx=x+side*(.08+i*w*.075);zz=z+math.sin(i*.8)*h*.19
   line(k,[(xx,y-.044,zz),(xx+side*.075,y-.055,zz+.06),(xx+side*.12,y-.043,zz+.03)],.012)
 crest(x,y-.05,z,min(h*.32,w*.14),k)
# Second roof and lantern clerestory make the main hall a dignified two-tier silhouette.
box(wood,(0,7.1,6.65),(8.2,4.8,.7))
for y in [4.69,9.51]:
 for x in [-3.8,-2.85,-1.9,-.95,0,.95,1.9,2.85,3.8]:
  box(screen,(x,y,6.71),(.76,.025,.44))
  for dx in [-.31,0,.31]:box(wood,(x+dx,y-.022,6.71),(.045,.055,.48))
  box(gold,(x,y-.035,6.49),(.8,.03,.025))
roof(0,7.1,4.6,2.95,6.96,1.27)
# Layered cornices, gold foundation borders and carved veranda balustrades.
for z,w,d in [(.29,12.65,7.95),(.68,12.6,7.9),(.94,12.86,8.1)]:
 box(stone,(0,7.1,z),(w,d,.065))
for y in [3.075,11.12]:box(gold,(0,y,.78),(12.7,.032,.032))
for x in [-6.36,6.36]:box(gold,(x,7.1,.78),(.03,8,.032))
for x in [-5.6,-2.8,2.8,5.6]:
 for y in [3.85,10.35]:
  for z in [1.31,1.48,3.98,4.16]:tube(gold,(x,y,z),(x,y,z+.055),.174,n=24)
  for a in range(8):
   ang=a*math.tau/8;sphere(gold,(x+.165*math.cos(ang),y+.165*math.sin(ang),1.42),(.018,.018,.018),n=8,lat=5)
  crest(x,y-.17,3.75,.105)
# Continuous carved beam frieze under the main roof.
for x in [-4.6,-1.4,1.4,4.6]:scroll_panel(x,3.69,4.34,2.20,.28)
for x in [-5.9,-4.6,-3.3,-2,-.7,.7,2,3.3,4.6,5.9]:
 box(gold,(x,2.91,4.53),(.14,.18,.055))
# Fine kumiko star-pattern joinery over the sliding lattice panels.
for x in [-4.35,-2.88,2.88,4.35]:
 scroll_panel(x,4.83,1.7,1.20,.79)
 for dx in [-.52,.52]:box(gold,(x+dx,4.79,2.56),(.018,.025,2.65))
 for row in range(5):
  for col in range(4):
   xx=x-.48+col*.32;zz=2.42+row*.29
   for a in range(6):
    t=a*math.tau/6;t2=(a+1)*math.tau/6
    p=(xx+.135*math.cos(t),4.80,zz+.135*math.sin(t));q=(xx+.135*math.cos(t2),4.80,zz+.135*math.sin(t2))
    tube(gold,p,q,.0055,n=5);tube(wood,(xx,4.80,zz),p,.009,n=5)
# Central ceremonial porch with a flowing karahafu-inspired gable.
for x in [-2.65,2.65]:
 tube(red,(x,2.35,.83),(x,2.35,4.42),.145,n=24)
 for z in [1.0,1.2,4.15,4.32]:tube(gold,(x,2.35,z),(x,2.35,z+.055),.16,n=24)
 bracket(x,2.35,4.13)
box(wood,(0,2.35,4.40),(5.7,.30,.27))
for i in range(64):
 x=-2.94+i*5.88/64;xx=x+5.88/64
 def gz(q):return 4.70+.83*math.exp(-(q/1.39)**2)+.21*(abs(q)/2.94)**8
 for j in range(8):
  y=1.79+j*.205;yy=y+.217
  face(tile,[(x,y,gz(x)),(xx,y,gz(xx)),(xx,yy,gz(xx)+.05),(x,yy,gz(x)+.05)])
 tube(gold,(x,1.76,gz(x)),(xx,1.76,gz(xx)),.052,n=10)
 tube(gold,(x,1.77,gz(x)-.16),(xx,1.77,gz(xx)-.16),.027,n=8)
 box(wood,((x+xx)/2,1.86,(gz(x)+4.44)/2),(.09,.14,gz(x)-4.44))
crest(0,1.72,5.01,.27)
for x in [-1.2,1.2]:scroll_panel(x,2.17,4.41,1.95,.28)
# Covered veranda rails around the outer sides, leaving the middle approach clear.
for side in [-1,1]:
 x=side*6.12
 for y in [4,5.1,6.2,7.3,8.4,9.5,10.6]:
  box(wood,(x,y,1.50),(.11,.11,.91));sphere(gold,(x,y,1.98),(.082,.082,.055),n=12,lat=6)
 for z in [1.24,1.82]:tube(wood,(x,4,z),(x,10.6,z),.048,n=8)
 for y in [4+i*.22 for i in range(31)]:box(wood,(x,y,1.50),(.045,.045,.54))
 # Bridge handrail gilded inlays and cross-braced lattice panels.
 for j in range(14):
  y=-12.3+j*.94;y2=y+.94
  tube(gold,(side*1.28,y,bz(y)+.89),(side*1.28,y2,bz(y2)+.89),.012,n=6)
  for k in range(2):
   a=y+k*.47;b=a+.47
   tube(wood,(side*1.28,a,bz(a)+.37),(side*1.28,b,bz(b)+.82),.020,n=6)
   tube(wood,(side*1.28,a,bz(a)+.82),(side*1.28,b,bz(b)+.37),.020,n=6)
# Interior coffered ceiling and raised wall panels remain visible through the entry.
for x in [-4.5,-3,-1.5,0,1.5,3,4.5]:
 box(wood,(x,7.7,4.14),(.11,5.05,.12))
 for y in [5.5,6.5,7.5,8.5,9.5]:
  box(wood,(x,y,4.2),(1.45,.07,.11))
  box(gold,(x,y,4.126),(.12,.14,.022))
for x in [-4.3,-2.7,2.7,4.3]:
 scroll_panel(x,10.25,2.72,1.24,2.46)
# Gilded aureole and decorative altar relief.
ring(gold,(0,8.98,3.04),.98,thick=.045,n=64)
ring(gold,(0,9.0,3.04),1.09,thick=.016,n=64)
for i in range(36):
 a=i*math.tau/36
 line(gold,[(math.cos(a)*1.1,9,3.04+math.sin(a)*1.1),(math.cos(a+.027)*1.23,9,3.04+math.sin(a+.027)*1.23),(math.cos(a+.045)*1.1,9,3.04+math.sin(a+.045)*1.1)],.014)
scroll_panel(0,7.90,1.44,3.12,.55)
# Sculpted komainu guardians, front paws, claws, folded haunches and curled manes.
def guardian(x,y):
 box(stone,(x,y,.66),(1.25,1.4,.38));box(carving,(x,y,.88),(1.36,1.51,.09))
 scroll_panel(x,y-.758,.68,1.15,.24,carving)
 sphere(carving,(x,y+.13,1.32),(.35,.44,.47),n=24,lat=16)
 sphere(carving,(x,y-.04,1.60),(.28,.29,.46),n=24,lat=16)
 for side in [-1,1]:
  sphere(carving,(x+side*.27,y+.31,1.11),(.21,.30,.22),n=20,lat=12)
  tube(carving,(x+side*.23,y-.27,1.46),(x+side*.23,y-.40,.99),.11,.095,n=16)
  sphere(carving,(x+side*.23,y-.49,1.00),(.135,.21,.085),n=16,lat=8)
  for toe in [-1,0,1]:sphere(carving,(x+side*.23+toe*.062,y-.65,.994),(.035,.058,.033),n=10,lat=6)
 sphere(carving,(x,y-.13,1.99),(.34,.29,.32),n=24,lat=16)
 sphere(carving,(x,y-.395,1.88),(.24,.16,.12),n=20,lat=12)
 sphere(dark,(x,y-.538,1.94),(.07,.032,.047),n=12,lat=8)
 for side in [-1,1]:
  sphere(carving,(x+side*.23,y-.06,2.22),(.10,.12,.18),n=16,lat=10)
  sphere(dark,(x+side*.145,y-.390,2.048),(.047,.026,.028),n=12,lat=8)
  line(carving,[(x+side*.08,y-.409,2.092),(x+side*.16,y-.410,2.105),(x+side*.22,y-.36,2.08)],.036)
 for row in range(3):
  for i in range(12):
   a=i*math.tau/12;r=.32+row*.015;z=1.69+row*.18
   c=(x+r*math.cos(a),y+.035+r*math.sin(a),z)
   sphere(carving,c,(.085,.087,.082),n=12,lat=8)
   ring(carving,(c[0],c[1]-.060,c[2]),.048,thick=.012,n=12)
 line(carving,[(x,y+.42,1.23),(x+.2,y+.60,1.4),(x+.26,y+.54,1.72),(x+.1,y+.48,1.83),(x+.04,y+.53,1.67)],.087,n=12)
 for k in range(5):line(carving,[(x-.22+k*.11,y-.19,1.5),(x-.18+k*.09,y-.27,1.39),(x-.12+k*.06,y-.26,1.29)],.017)
for x in [-3.6,3.6]:guardian(x,2.25)
# Stone pagodas and a water-basin ensemble as quiet landscape focal points.
def pagoda(x,y):
 box(stone,(x,y,.29),(1.65,1.65,.3))
 z=.5
 for level in range(5):
  w=.80-level*.095
  box(carving,(x,y,z+.16),(w*1.05,w*1.05,.34))
  for side in [-1,1]:box(dark,(x+side*w*.53,y,z+.18),(.01,.16,.20))
  for j in range(4):
   r=w*(1.45-j*.23);box(carving,(x,y,z+.38+j*.075),(r*2,r*2,.085))
  z+=.68
 tube(gold,(x,y,z),(x,y,z+.65),.035,n=12)
 for j in range(5):sphere(gold,(x,y,z+j*.105),(.10-j*.014,.10-j*.014,.025),n=16,lat=6)
for x,y in [(-11.4,8.5),(11.6,10)]:pagoda(x,y)
# Formal raked gravel beds, with stone edging and wave-like grooves.
for x,y,w,d in [(-8.4,10.5,3.7,3.2),(8.4,10.7,3.9,3.2),(-6,-14.0,4.5,1.8),(6,-14.0,4.5,1.8)]:
 box(carving,(x,y,.20),(w,d,.15))
 for side in [-1,1]:
  box(stone,(x+side*w*.5,y,.27),(.10,d,.15));box(stone,(x,y+side*d*.5,.27),(w,.10,.15))
 for row in range(int(d/.09)-1):
  yy=y-d*.5+.12+row*.09
  points=[(x-w*.46+i*w*.92/25,yy+.025*math.sin(i*.4),.28) for i in range(26)]
  line(stone,points,.009,n=4)
# Cloud-pruned pines: visible branching, flattened needle sprays, irregular masses.
def pine(x,y,h):
 line(bark,[(x,y,.18),(x+.1,y,h*.34),(x-.12,y+.08,h*.69),(x+.18,y,h)],.115,n=12)
 for level in range(6):
  z=.8+level*h*.14;ang=level*2.35;reach=(1-level*.10)*1.45
  c=(x+math.cos(ang)*reach,y+math.sin(ang)*reach,z+.23)
  line(bark,[(x,y,z-.15),(x+math.cos(ang)*reach*.5,y+math.sin(ang)*reach*.5,z),c],.058,n=9)
  for j in range(820):
   a=random.random()*math.tau;r=math.sqrt(random.random());px=c[0]+math.cos(a)*r*.91;py=c[1]+math.sin(a)*r*.71;pz=c[2]+random.uniform(-.11,.16)*(1-r*.6)
   for k in range(3):
    aa=a+k*2.1;ll=random.uniform(.09,.18)
    face(pinegreen,[(px-.006,py,pz),(px+.006,py,pz),(px+math.cos(aa)*ll,py+math.sin(aa)*ll,pz+.06)])
for x,y,h in [(-7.4,.55,3.6),(7.4,.55,3.5),(-12.9,-6,3.1),(12.6,-5.8,3.8),(-5.4,-13.5,2.6),(6,-13.7,2.8)]:pine(x,y,h)
# Bamboo grove behind each side pavilion; joint rings and narrow pointed leaves.
for cx,cy in [(-12.8,11.5),(13.7,12.0)]:
 for j in range(17):
  x=cx+random.uniform(-1,1);y=cy+random.uniform(-.8,.8);h=random.uniform(3.8,6.5);lean=random.uniform(-.32,.32)
  for i in range(int(h/.38)):
   z=.2+i*.38;xx=x+lean*z/h
   tube(bamboo,(xx,y,z),(xx+lean*.38/h,y,z+.38),.039,.037,n=10)
   tube(pinegreen,(xx,y,z),(xx,y,z+.025),.043,n=10)
   if z<1.6 or i%2:continue
   a=random.random()*math.tau;tip=(xx+math.cos(a)*.55,y+math.sin(a)*.55,z+.2)
   tube(bamboo,(xx,y,z),tip,.011,.004,n=6)
   for k in range(7):
    t=k/7;px=xx+(tip[0]-xx)*t;py=y+(tip[1]-y)*t;pz=z+.2*t
    aa=a+(-1 if k%2 else 1)*.7;ll=random.uniform(.16,.30)
    face(shrubgreen,[(px,py,pz),(px+math.cos(aa+.14)*ll*.52,py+math.sin(aa+.14)*ll*.52,pz+.05),(px+math.cos(aa)*ll,py+math.sin(aa)*ll,pz-.04),(px+math.cos(aa-.14)*ll*.52,py+math.sin(aa-.14)*ll*.52,pz+.035)])
# Camellias and low azalea cushions: individual waxy leaves, subtle flowers.
def shrub(x,y,rx,ry,h,flowers=False):
 for j in range(950):
  a=random.random()*math.tau;ph=random.uniform(.12,math.pi*.49);r=random.uniform(.86,1.05)
  px=x+math.cos(a)*math.sin(ph)*rx*r;py=y+math.sin(a)*math.sin(ph)*ry*r;pz=.23+math.cos(ph)*h*r
  aa=random.random()*math.tau;s=random.uniform(.06,.11);dx=math.cos(aa)*s;dy=math.sin(aa)*s
  face(shrubgreen,[(px-dx,py-dy,pz),(px-dy*.45,py+dx*.45,pz+.025),(px+dx,py+dy,pz+.015),(px+dy*.45,py-dx*.45,pz)])
  if flowers and j%210==0:
   for k in range(5):
    a=k*math.tau/5;sphere(flower,(px+math.cos(a)*.035,py+math.sin(a)*.035,pz+.03),(.035,.035,.018),n=8,lat=5)
for x,y,rx,ry,h in [(-10,1.4,1.1,.8,.65),(10.8,1.2,.9,.8,.75),(-11.7,-1.9,1.2,.7,.85),(11.8,-1.8,1,.85,.75),(-12.4,-8,.7,1,.55),(12.3,-8.3,1,.7,.65),(-8.4,-11.8,1.1,.65,.7),(8.4,-11.7,1.1,.6,.65),(-6.8,11.8,.8,.6,.6),(6.8,11.8,.9,.6,.6),(-14,4.6,1.1,.8,.7),(14,4.8,1,.8,.7)]:
 shrub(x,y,rx,ry,h,True)
# Natural sculptural stones and moss-covered mounds in the rear planting beds.
for side in [-1,1]:
 for x,y,sc in [(8.8,11.7,(.6,.5,1.2)),(9.6,11.8,(.5,.6,.6)),(7.8,12,(.8,.6,.45))]:rock((side*x,y,.6),sc)
print('Restoration: tiered gilded roofs, kumiko, stone guardians, 5-tier pagodas, six pines, bamboo and camellias.',flush=True)
