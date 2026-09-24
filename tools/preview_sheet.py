from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
source=Path(sys.argv[1]);destination=Path(sys.argv[2]);destination.parent.mkdir(parents=True,exist_ok=True)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,18);title=ImageFont.truetype(font_path,25)
canvas=Image.new('RGB',(1280,1430),'#101820');draw=ImageDraw.Draw(canvas)
draw.text((28,20),'SOURCE ART / MOBILE CANDIDATES',font=title,fill='#eff4f4')
draw.text((28,62),'Blender studio renders. Not Unreal Engine. Not gameplay. Not an FPS test.',font=font,fill='#b3c6cd')
for i,name in enumerate(['portable_generator','metal_tool_chest','sofa_02','fire_hydrant']):
 p=source/(name+'.png');assert p.exists(),p
 image=Image.open(p).convert('RGB').resize((620,620));x=10+(i%2)*640;y=108+(i//2)*660;canvas.paste(image,(x,y));draw.text((x+10,y+624),name,font=font,fill='#dae5e5')
canvas.save(destination,quality=90)
