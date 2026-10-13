"""Authored leaf sprays for distant foliage cards, made from our original leaf assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance
import random,math
A=Path(__file__).resolve().parents[1]/'dist/assets'
for kind in ['green','ginkgo','maple']:
 rng=random.Random(771);out=Image.new('RGBA',(512,512));draw=ImageDraw.Draw(out)
 draw.line([(50,440),(255,255),(435,60)],fill=(80,64,34,255),width=4)
 source=Image.open(A/(kind+'-leaf.png')).convert('RGBA')
 for i in range(125):
  angle=rng.random()*math.tau;r=math.sqrt(rng.random());x=256+math.cos(angle)*r*200;y=256+math.sin(angle)*r*203
  if i<20:draw.line([(256,256),(x,y)],fill=(75,67,37,220),width=2)
  size=rng.randint(36,62);leaf=source.resize((size,size),Image.Resampling.LANCZOS).rotate(rng.uniform(0,360),Image.Resampling.BICUBIC,expand=True)
  leaf=ImageEnhance.Brightness(leaf).enhance(rng.uniform(.73,1.03));out.alpha_composite(leaf,(int(x-leaf.width/2),int(y-leaf.height/2)))
 out.save(A/(kind+'-spray.png'))
