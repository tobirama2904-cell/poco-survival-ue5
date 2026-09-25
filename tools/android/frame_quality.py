"""Narrow regression alarms for black/strong-magenta frames, NOT art approval."""
from PIL import Image

def metrics(path):
 im=Image.open(path).convert('RGB');w,h=im.size
 im=im.crop((w//8,h//6,w*7//8,h*5//6)).resize((160,90));pixels=list(im.getdata());total=len(pixels)
 black=sum(max(r,g,b)<12 for r,g,b in pixels)/total
 magenta=sum(r>180 and b>150 and g<r*.82 and g<b*.92 for r,g,b in pixels)/total
 return {'black_fraction':round(black,4),'strong_magenta_fraction':round(magenta,4),'not_black':black<.98,'no_strong_magenta_regression':magenta<.18}
