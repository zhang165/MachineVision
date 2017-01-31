from PIL import Image, ImageDraw
import numpy as np
import math
from scipy import signal
import ncc

# define constants
pyramid_reduction = 0.75
template_width = 15
match_threshold = 0.65

# define functions
def makePyramid(image, minsize):
	[x,y] = image.size
	res = []
	while (x > minsize and y > minsize):
		image_next = image.resize((x,y), Image.BICUBIC)
		x = int(x*pyramid_reduction)
		y = int(y*pyramid_reduction)
		res.append(image_next)
	return res

def showPyramid(pyramid):
	[x,y] = pyramid[0].size
	
	length = 0	# find the length
	for i in range(len(pyramid)):
		length = length + pyramid[i].size[0]
	
	image = Image.new("L", (length,y), "white"); # generate white image

	offset = 0
	for i in range(len(pyramid)): # paste each image
		image.paste(pyramid[i],(offset,y-pyramid[i].size[1]))
		offset = offset + pyramid[i].size[0]
	image.show()
	return image

def resize(template, width=15):
	[x,y] = template.size
	ratio = (width/float(x))
	template = template.resize((width, int(y*ratio)), Image.BICUBIC) #resize image
	return template

def findTemplate(pyramid, template, threshold):
	[a,b] = template.size

	marked = pyramid[0].convert('RGB') # the marked image to return
	draw = ImageDraw.Draw(marked) 

	for i in range(len(pyramid)): # for every image
		[x,y] = pyramid[i].size
		corr = ncc.normxcorr2D(pyramid[i],template)	

		for j in range(len(corr)):
			for k in range(len(corr[j])):
				if(corr[j][k] > threshold):	# we've found a match
					ratio = 1/(pyramid_reduction**i)
					p = ratio*k -a/2 # find corner
					q = ratio*j -b/2
					draw.line((p,q,p+a,q),fill="red",width=2)
					draw.line((p,q,p,q+b),fill="red",width=2)
					draw.line((p+a,q,p+a,q+b),fill="red",width=2)
					draw.line((p,q+b,p+a,q+b),fill="red",width=2)
	del draw
	return marked



# Run our script	
im = Image.open('G:\UBC\CPSC425\\assignments\\a3\\faces\\judybats.jpg')
pyramid = makePyramid(im, 25) #create pyramid
#showPyramid(pyramid)

template = Image.open('G:\UBC\CPSC425\\assignments\\a3\\faces\\template.jpg')
template = resize(template, template_width) # resize template

marked = findTemplate(pyramid,template, match_threshold)
marked.show()