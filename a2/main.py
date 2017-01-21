from PIL import Image
import numpy as np
import math
from scipy import signal

def boxfilter(n):
	assert n%2 is not 0, "Dimension must be odd"
	return np.full((n,n),1.0/(n*n), dtype = float)

def gauss1d(sigma=1):
	# generate n, ensure n is odd
	n = np.ceil(6*sigma)
	n = n+1 if n%2 == 0 else n

	i = np.arange(-np.floor(n/2),np.floor(n/2)+1,1) # generate the range
	gauss = np.vectorize(lambda x: np.exp((-x**2)/(2*sigma**2))) # mapping function
	i = gauss(i) # apply the map
	return 1/sum(i)*i # return normalized

def gauss2d(sigma=1):
	i = gauss1d(sigma) # generate 1d guass
	i = i[np.newaxis] # generate 2d 
	i_t = np.transpose(i) # create transpose

	return signal.convolve2d(i, i_t) # convolve i with i'

def gaussconvolve2d(array,sigma):
	f = gauss2d(sigma) # generate 2d filter
	array = signal.convolve2d(array,f,'same') # convolve with 2d filter of same size
	return array

im = Image.open('C:\UBC\CPSC425\\a2\\teemo.png')
im = im.convert('L')
im.save('C:\UBC\CPSC425\\a2\\gray_teemo.png','PNG')

im_array = np.asarray(im)
im_array = gaussconvolve2d(im_array,3)
im2 = Image.fromarray(im_array.astype('uint8'))
im2.save('C:\UBC\CPSC425\\a2\\convolved_teemo.png','PNG')
