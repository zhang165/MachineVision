from PIL import Image, ImageDraw
from random import randint
import numpy as np
import csv
import math

def ReadKeys(image):
    im = Image.open(image+'.pgm').convert('RGB')
    keypoints = []
    descriptors = []
    first = True
    with open(image+'.key','rb') as f:
        reader = csv.reader(f, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC,skipinitialspace = True)
        descriptor = []
        for row in reader:
            if len(row) == 2:
                assert first, "Invalid keypoint file header."
                assert row[1] == 128, "Invalid keypoint descriptor length in header (should be 128)."
                count = row[0]
                first = False
            if len(row) == 4:
                keypoints.append(np.array(row))
            if len(row) == 20:
                descriptor += row
            if len(row) == 8:
                descriptor += row
                assert len(descriptor) == 128, "Keypoint descriptor length invalid (should be 128)."
                #normalize the key to unit length
                descriptor = np.array(descriptor)
                descriptor = descriptor / math.sqrt(np.sum(np.power(descriptor,2)))
                descriptors.append(descriptor)
                descriptor = []
    assert len(keypoints) == count, "Incorrect total number of keypoints read."
    print "Number of keypoints read:", int(count)
    return [im,keypoints,descriptors]

def AppendImages(im1, im2):
    im1cols, im1rows = im1.size
    im2cols, im2rows = im2.size
    im3 = Image.new('RGB', (im1cols+im2cols, max(im1rows,im2rows)))
    im3.paste(im1,(0,0))
    im3.paste(im2,(im1cols,0))
    return im3

def DisplayMatches(im1, im2, matched_pairs):
    im3 = AppendImages(im1,im2)
    offset = im1.size[0]
    draw = ImageDraw.Draw(im3)
    for match in matched_pairs:
        draw.line((match[0][1], match[0][0], offset+match[1][1], match[1][0]),fill="red",width=2)
    im3.show()
    im3.save("matchings_q4","JPEG")
    return im3

# consulted stackoverflow for finding angular distance
def angularDistance(o1, o2):
	phi = abs(o2 - o1) % (2*math.pi)
	dist = phi
	if(phi > math.pi): # it's wrapping around
		dist = 2*math.pi - phi
	return dist

def ransac(matched_pairs, keypoints1, keypoints2):
	repeat = 10 # do 10 repeats
	orientation_t = 50 # change in orientation must be within 50 degrees
	scale_t = 0.55 # scale must agree within 55%

	best_overall = [] # remember our best overall

	for i in range(repeat): 
		rand_m = matched_pairs[randint(0,len(matched_pairs)-1)] # pick a random pair
		scale = abs(rand_m[0][2] - rand_m[1][2]) # calculate difference in scale
		orientation = abs(rand_m[0][3] - rand_m[1][3]) # calculate difference in orientation
		
		best_curr = [] # remember our best current set

		for m1, m2 in matched_pairs: # now check every other matching pair 
			scale_temp = abs(m1[2] - m2[2]) # calculate our scale difference again
			orientation_temp = abs(m1[3] - m2[3]) # calculate orientation again

			# change of scale does not agree within plus or minus scale_t 
			if(scale_t * max(scale_temp, scale) > min(scale_temp, scale_t)):
				continue

			# change of orientation between the two keypoints of each match beyond orientation_t
			dist = angularDistance(orientation, orientation_temp)
			if (dist > math.radians(orientation_t)):
				continue

			# this current match is within our thresholds and we can add it
			best_curr.append([m1,m2])

		if(len(best_overall) < len(best_curr)): # if we've found a longer supporting set
			best_overall = best_curr

	return best_overall

def match(image1,image2):
    im1, keypoints1, descriptors1 = ReadKeys(image1)
    im2, keypoints2, descriptors2 = ReadKeys(image2)
    
    t = 0.68 # pick a threshold

    #Generate matches
    matched_pairs = [] # matching keypoints

    for i in range(len(descriptors1)):
    	matches = {} # remember our in a map
    	for j in range(len(descriptors2)):
    		matches[(math.acos(np.dot(descriptors1[i],descriptors2[j])))] = (i,j) # compute the angle between d1[i] d2[j] and map it to our two indices

    	sorted_m = sorted(matches) # sort map based on angle of keys

    	if(sorted_m[0]/sorted_m[1] < t): # the ratio of best to second best below threshold
    		i_match, j_match = matches[sorted_m[0]] # take the indices of the best match
    		matched_pairs.append([keypoints1[i_match],keypoints2[j_match]]) # append a new tuple to matched_pairs

    matched_pairs = ransac(matched_pairs, keypoints1, keypoints2) # call ransac 
    im3 = DisplayMatches(im1, im2, matched_pairs)
    return im3

#Test run...
match('library','library2')

