from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import signal
import numpy.linalg as lin

# START OF FUNCTIONS CARRIED FORWARD FROM ASSIGNMENT 2

def boxfilter(n):
    assert n%2 is not 0, "Dimension must be odd"
    return np.full((n,n),1.0/(n*n), dtype = float)

def gauss1d(sigma):
    # generate n, ensure n is odd
    n = np.ceil(6*sigma)
    n = n+1 if n%2 == 0 else n

    i = np.arange(-np.floor(n/2),np.floor(n/2)+1,1) # generate the range
    gauss = np.vectorize(lambda x: np.exp((-x**2)/(2*sigma**2))) # mapping function
    i = gauss(i) # apply the map
    return 1/sum(i)*i # return normalized

def gauss2d(sigma):
    i = gauss1d(sigma) # generate 1d guass
    i = i[np.newaxis] # generate 2d 
    i_t = np.transpose(i) # create transpose

    return signal.convolve2d(i, i_t) # convolve i with i'

def gaussconvolve2d(image, sigma):
    f = gauss2d(sigma) # generate 2d filter
    return signal.convolve2d(image,f,'same') # convolve with 2d filter of same size

# END OF FUNCTIONS CARRIED FORWARD FROM ASSIGNMENT 2

# Define a function, boxconvolve2d, to convolve an image with a boxfilter of size n
# (used in Estimate_Derivatives below).

def boxconvolve2d(image, n):
    f = boxfilter(n) # generate boxfilter
    return signal.convolve2d(image,f,'same')

def Estimate_Derivatives(im1, im2, sigma=1.5, n=3): # Estimate spatial derivatives of im1 and temporal derivative from im1 to im2.
    im1_smoothed = gaussconvolve2d(im1,sigma) # Smooth im1 with a 2D Gaussian of the given sigma.
    Ix, Iy = np.gradient(im1_smoothed) # Use first central difference to estimate derivatives.
    It = boxconvolve2d(im2, n) - boxconvolve2d(im1, n) # Use point-wise difference between (boxfiltered) im2 and im1 to estimate temporal derivative
    return Ix, Iy, It

def Optical_Flow(im1, im2, x, y, window_size, sigma=1.5, n=3):
    assert((window_size % 2) == 1) , "Window size must be odd"
    # UNCOMMENT THE NEXT LINE WHEN YOU HAVE COMPLETED Estimate_Derivatives
    Ix, Iy, It = Estimate_Derivatives(im1, im2, sigma, n)
    half = np.floor(window_size/2)
    # select the three local windows of interest
    win_Ix = Ix[int(y-half-1):int(y+half), int(x-half-1):int(x+half)].T # select window Ix
    win_Iy = Iy[int(y-half-1):int(y+half), int(x-half-1):int(x+half)].T # select window Iy
    b = It[int(y-half-1):int(y+half), int(x-half-1):int(x+half)].T # select window b

    A = np.vstack((win_Ix.flatten(), win_Iy.flatten())).T # calculate A by vertically stacking win_Ix and win_Iy and transpose
    A_TA_inv = np.linalg.pinv(np.dot(A.T,A)) # calculate ATA^-1
    V = np.dot(A_TA_inv, np.dot(A.T,b.flatten())) # calculate V = ATA^-1 * ATb
    return V[1], V[0]

def AppendImages(im1, im2):
    """Create a new image that appends two images side-by-side.

    The arguments, im1 and im2, are PIL images of type RGB
    """
    im1cols, im1rows = im1.size
    im2cols, im2rows = im2.size
    im3 = Image.new('RGB', (im1cols+im2cols, max(im1rows,im2rows)))
    im3.paste(im1,(0,0))
    im3.paste(im2,(im1cols,0))
    return im3

def DisplayFlow(im1, im2, x, y, uarr, varr):
    """Display optical flow match on a new image with the two input frames placed side by side.

    Arguments:
     im1           1st image (in PIL 'RGB' format)
     im2           2nd image (in PIL 'RGB' format)
     x, y          point coordinates in 1st image
     u, v          list of optical flow values to 2nd image

    Displays and returns a newly created image (in PIL 'RGB' format)
    """
    im3 = AppendImages(im1,im2)
    offset = im1.size[0]
    draw = ImageDraw.Draw(im3)
    xinit = x+uarr[0]
    yinit = y+varr[0]
    for u,v,ind in zip(uarr[1:], varr[1:], range(1, len(uarr))):
		draw.line((offset+xinit, yinit, offset+xinit+u, yinit+v),fill="red",width=2)
		xinit += u
		yinit += v
    draw.line((x, y, offset+xinit, yinit), fill="yellow", width=2)
    im3.show()
    del draw
    return im3

def HitContinue(Prompt='Hit any key to continue'):
    raw_input(Prompt)

# uncomment the next two lines if the leftmost digit of your student number is 8
x=274
y=126

##############################################################################
#                            Global "magic numbers"                          #
##############################################################################

# window size (for estimation of optical flow)
window_size=21

# sigma of the 2D Gaussian (used in the estimation of Ix and Iy)
sigma=1.5

# size of the boxfilter (used in the estimation of It)
n = 3

##############################################################################
#             basic testing (optical flow from frame 7 to 8 only)            #
##############################################################################

# scale factor for display of optical flow (to make result more visible)
scale=10

PIL_im1 = Image.open('frame07.png')
PIL_im2 = Image.open('frame08.png')
im1 = np.asarray(PIL_im1)
im2 = np.asarray(PIL_im2)
dx, dy = Optical_Flow(im1, im2, x, y, window_size, sigma, n)
print 'Optical flow: [', dx, ',', dy, ']'
plt.imshow(im1, cmap='gray')
plt.hold(True)
plt.plot(x,y,'xr')
plt.plot(x+dx*scale,y+dy*scale, 'dy')
print 'Close figure window to continue...'
plt.show()
uarr = [dx]
varr = [dy]

##############################################################################
#                   run the remainder of the image sequence                  #
##############################################################################

# UNCOMMENT THE CODE THAT FOLLOWS (ONCE BASIC TESTING IS COMPLETE/DEBUGGED)

print 'frame 7 to 8'
DisplayFlow(PIL_im1, PIL_im2, x, y, uarr, varr)
HitContinue()

prev_im = im2
xcurr = x+dx
ycurr = y+dy
offset = PIL_im1.size[0]

for i in range(8, 14):
    im_i = 'frame%0.2d.png'%(i+1)
    print 'frame', i, 'to', (i+1)
    PIL_im_i = Image.open('%s'%im_i)
    numpy_im_i = np.asarray(PIL_im_i)
    dx, dy = Optical_Flow(prev_im, numpy_im_i, xcurr, ycurr, window_size, sigma, n)
    xcurr += dx
    ycurr += dy
    prev_im = numpy_im_i
    uarr.append(dx)
    varr.append(dy)
    # redraw the (growing) figure
    DisplayFlow(PIL_im1, PIL_im_i, x, y, uarr, varr)
    HitContinue()

##############################################################################
# Don't forget to include code to document the sequence of (x, y) positions  #
# of your feature in each frame successfully tracked.                        #
##############################################################################
