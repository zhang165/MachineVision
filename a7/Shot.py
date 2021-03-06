from PIL import Image, ImageDraw
import numpy as np
from scipy.cluster.vq import vq, kmeans
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt

# Computes the cost of given boundaries. Good boundaries have zero cost.
def get_boundaries_cost( boundaries, good_boundaries ):
    return np.sum( boundaries != good_boundaries );

# Finds the indices of color_histograms given a series of cluster centres.
def cluster2boundaries(histograms, centres):

    # Find the cluster assignment of each histogram
    distances = cdist( histograms, centres )
    idx       = np.argmin( distances, 1 )

    # Find the points where the index changes
    boundaries = np.zeros( len(idx)+1, dtype = np.bool )

    for i in range( len(idx)-1 ):
        boundaries[i+1] = idx[i] != idx[i+1];

    return boundaries

# Computes histograms from gray images
def compute_gray_histograms( grays, nbins ):
    gray_hs = np.zeros(( nframes, nbins ), dtype = np.uint16 );

    for i in range( len(grays) ):
        gray_im = grays[i]
        v1 = np.histogram(gray_im.flatten(),bins=nbins, range=(0,255))
        gray_hs[i] = v1[0]

    return gray_hs;


def compute_color_histograms( colors, nbins ):
    red_hs = np.zeros(( nframes, nbins ), dtype = np.uint16 ); # red histgrams
    green_hs = np.zeros(( nframes, nbins ), dtype = np.uint16 ); # green histograms
    blue_hs = np.zeros(( nframes, nbins ), dtype = np.uint16 ); # blue histograms

    for i in range( len(colors) ):
        red_im = colors[i,:,:,0] # save red image
        r1 = np.histogram(red_im.flatten(),bins=nbins, range=(0,255)) # flatten and histogram red

        green_im = colors[i,:,:,1] # save green image
        g1 = np.histogram(green_im.flatten(),bins=nbins, range=(0,255)) # flatten and histogram green

        blue_im = colors[i,:,:,2] # save blue image
        b1 = np.histogram(blue_im.flatten(),bins=nbins, range=(0,255)) # flatten and histogram blue

        red_hs[i] = r1[0]
        green_hs[i] = g1[0]
        blue_hs[i] = b1[0]

    return np.hstack((red_hs,green_hs,blue_hs)) # stack the histograms together

# for debugging
np.set_printoptions(threshold=np.nan)

# === Main code starts here ===
fname     = 'colours' # folder name 
nframes   = 151       # number of frames
im_height = 90        # image height 
im_width  = 120       # image width

# define the list of (manually determined) shot boundaries here
good_boundaries = [33,92,143]

# convert good_boundaries list to a binary array
gb_bool = np.zeros( nframes+1, dtype = np.bool )
gb_bool[ good_boundaries ] = True

# Create some space to load the images into memory
colors = np.zeros(( nframes, im_height, im_width, 3), dtype = np.uint8);
grays  = np.zeros(( nframes, im_height, im_width   ), dtype = np.uint8);

# Read the images and store them in color and grayscale formats
for i in range( nframes ):
    imname    = '%s/dwc%03d.png' % ( fname, i+1 )
    im        = Image.open( imname ).convert( 'RGB' )
    colors[i] = np.asarray(im, dtype = np.uint8)
    grays[i]  = np.asarray(im.convert( 'L' ))

# Initialize color histogram
nclusters   = 4;
nbins       = range(2,13)
gray_costs  = np.zeros( len(nbins) );
color_costs = np.zeros( len(nbins) );

# === GRAY HISTOGRAMS ===
for n in nbins:
    gray_histogram = compute_gray_histograms(grays, n).astype(float) # generate the gray histogram
    codebook, distortion = kmeans(gray_histogram, nclusters) # use pythons kmeans to get clusters
    boundaries = cluster2boundaries(gray_histogram, codebook.astype(float)) # compute the boundaries
    gray_costs[n-2] = get_boundaries_cost(boundaries, gb_bool) #save cost for given bin size
# === END GRAY HISTOGRAM CODE ===

plt.figure(1);
plt.xlabel('Number of bins')
plt.ylabel('Error in boundary detection')
plt.title('Boundary detection using gray histograms')
plt.plot(nbins, gray_costs)
plt.axis([2, 13, -1, 10])
plt.grid(True)
plt.show()

# === COLOR HISTOGRAMS ===
for n in nbins:
    color_histogram = compute_color_histograms(colors, n).astype(float) # generate the color histogram
    codebook, distortion = kmeans(color_histogram, nclusters) # use pythons kmeans to get clusters
    boundaries = cluster2boundaries(color_histogram, codebook.astype(float)) # compute the boundaries
    color_costs[n-2] = get_boundaries_cost(boundaries, gb_bool) #save cost for given bin size
# === END COLOR HISTOGRAM CODE ===

plt.figure(2);
plt.xlabel('Number of bins')
plt.ylabel('Error in boundary detection')
plt.title('Boundary detection using color histograms')
plt.plot(nbins, color_costs)
plt.axis([2, 13, -1, 10])
plt.grid(True)
plt.show()

fdiffs = np.zeros( nframes )
# === ABSOLUTE FRAME DIFFERENCES ===
for i in range( nframes ):
    if i==0: # skip first to avoid indexing issue
        continue
    fdiffs[i] = np.sum(abs(grays[i]-grays[i-1])) # calculate the sum of abs difference between successive frames

plt.figure(4)
plt.xlabel('Frame number')
plt.ylabel('Absolute frame difference')
plt.title('Absolute frame differences')
plt.plot(fdiffs)
plt.show()

sqdiffs = np.zeros( nframes )
# === SQUARED FRAME DIFFERENCES ===
for i in range( nframes ):
    if i==0: # skip first to avoid indexing issue
        continue
    sqdiffs[i] = (np.sum(abs(grays[i]-grays[i-1]))**2) # calculate the squared sum of abs difference between successive frames

plt.figure(5)
plt.xlabel('Frame number')
plt.ylabel('Squared frame difference')
plt.title('Squared frame differences')
plt.plot(sqdiffs)
plt.show()

avgdiffs = np.zeros( nframes )
# === AVERAGE GRAY DIFFERENCES ===
for i in range( nframes ):
    if i==0: # skip first to avoid indexing issue
        continue
    avgdiffs[i] = np.mean(grays[i])-np.mean(grays[i-1]) # calculate the mean of current and previous frames and take the difference

plt.figure(6)
plt.xlabel('Frame number')
plt.ylabel('Average gray frame difference')
plt.title('Average gray frame differences')
plt.plot(avgdiffs)
plt.show()

histdiffs = np.zeros( nframes )
prev_hist = compute_gray_histograms(grays[0], 10) # compute initial gray histogram
# === HISTOGRAM DIFFERENCES ===
for i in range( nframes ):
    if i==0: # skip first to avoid indexing issue
        continue
    curr_hist = compute_gray_histograms(grays[i], 10) # compute current gray histogram
    histdiffs[i] = np.linalg.norm(curr_hist-prev_hist) # find euclidean distance (l2-norm)
    prev_hist = curr_hist # save previous histogram as current 

plt.figure(7)
plt.xlabel('Frame number')
plt.ylabel('Histogram frame difference')
plt.title('Histogram frame differences')
plt.plot(histdiffs)
plt.show()