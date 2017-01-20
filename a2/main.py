from PIL import Image
import numpy as np
import math
from scipy import signal

def boxfilter(n):
	assert n%2 is not 0, "Dimension must be odd"
	return np.full((n,n),1.0/(n*n), dtype = float)

def gauss2d(sigma=1):
	n = np.ceil(6*sigma)
	n = n+1 if n%2 == 0 else n
	i = np.arange(-np.floor(n/2),np.floor(n/2)+1,1) # generate the range
	print i

	pass

def gaussconvolve2d(array,sigma):
	pass
