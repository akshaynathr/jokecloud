from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def img_fun(filename,text,size):
        img=Image.open(filename)
	w,h=img.size
	fontsize=1
	img_fraction=0.50
        draw=ImageDraw.Draw(img)
        font=ImageFont.truetype("Aaargh.ttf",h/2)
	while font.getsize(text)[0] < img_fraction*img.size[0]:
    # iterate until the text size is just larger than the criteria
            fontsize += 1
            font = ImageFont.truetype("Aaargh.ttf", fontsize)
	
        draw.text((0,0),text,(255,255,255),font=font)
        img.save("test1.png")
	del img

img_fun("assasincreed.png","ho",1000)
