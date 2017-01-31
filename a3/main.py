from PIL import Image, ImageDraw
import numpy as np
import math
from scipy import signal
import ncc

# define constants
pyramid_reduction = 0.80
pyramid_min_size = 5
template_width = 20
match_threshold = 0.59
image_loc = 'faces\\family.jpg'
template_loc = 'faces\\template.jpg'

# define functions
def makePyramid(image, minsize):
	[x,y] = image.size
	res = []
	while (x > minsize and y > minsize): # resize and append new image
		image_next = image.resize((x,y), Image.BICUBIC)
		x = int(x*pyramid_reduction)
		y = int(y*pyramid_reduction)
		res.append(image_next)
	return res

def showPyramid(pyramid):
	[x,y] = pyramid[0].size
	length = 0	# calculate total length
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
	ratio = (width/float(x)) # calculate aspect ratio
	template = template.resize((width, int(y*ratio)), Image.BICUBIC) #resize image
	return template

def findTemplate(pyramid, template, threshold):
	[a,b] = template.size

	marked = pyramid[0].convert('RGB') # the marked image to return
	draw = ImageDraw.Draw(marked) 

	for i in range(len(pyramid)): # for every image
		[x,y] = pyramid[i].size
		corr = ncc.normxcorr2D(pyramid[i],template)	# generate corr array

		for j in range(len(corr)): # iterate to find positions 
			for k in range(len(corr[j])):
				if(corr[j][k] > threshold):	# we've found a match
					ratio = 1/(pyramid_reduction**i) # calculate ratios and offsets
					a_offset = ratio*a; 
					b_offset = ratio*b;
					p = ratio*k -a_offset/2 # find the center
					q = ratio*j -b_offset/2

					draw.line((p,q,p+a_offset,q),fill="red",width=2) #draw a box
					draw.line((p,q,p,q+b_offset),fill="red",width=2)
					draw.line((p+a_offset,q,p+a_offset,q+b_offset),fill="red",width=2)
					draw.line((p,q+b_offset,p+a_offset,q+b_offset),fill="red",width=2)
	del draw
	return marked


# Run our scripts
im = Image.open(image_loc)
pyramid = makePyramid(im, pyramid_min_size) #create pyramid
#showPyramid(pyramid)

template = Image.open(template_loc)
template = resize(template, template_width) # resize template

marked = findTemplate(pyramid,template, match_threshold)
marked.show()