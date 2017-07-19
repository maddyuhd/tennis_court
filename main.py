import cv2
import glob
import os
import numpy as np

#input path
db_path ="/home/maddy/Work/InProgress/tennis_court/input/"
sensitivity = 75 # change it according to your need !


#helper function
def show(im,msg="press any key to continue"):
    cv2.namedWindow(msg, cv2.WINDOW_NORMAL)
    cv2.imshow(msg, im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def interpts(x1,y1,x2,y2, x3,y3,x4,y4):
	a1, b1 = y2 - y1, x1 - x2
	c1 = a1 * x1 + b1 * y1
	a2, b2 = y4 - y3, x3 - x4
	c2 = a2 * x3 + b2 * y3
	det = a1 * b2 - a2 * b1
	try:
		assert det
	except :
		return False
	# assert det, "lines are parallel"
	x ,y = (1. * (b2 * c1 - b1 * c2) / det, 1. * (a1 * c2 - a2 * c1) / det)
	if (0<= x <= w_proc and 0<= y <= h_proc):
		return x, y
	else:
		return False

def centerPts(x1,y1,x2,y2):
	liness = [(0,0,w_proc,0), (0,h_proc,w_proc,h_proc),(0,0,0,h_proc), (w_proc, 0,w_proc,h_proc)]
	res =[]

	for x3,y3,x4,y4 in liness:
		x = interpts(x1,y1,x2,y2, x3,y3,x4,y4)
		# print x
		if x != False:
			res.append(x)
		if len(res) == 2:
			# print "end"
			x1,y1 = res[0]
			x2,y2 = res[1]
			c_x = (x1 + x2) / 2.0
			c_y = (y1 + y2) / 2.0
			return c_x, c_y
	if len(res) != 2 :
		return (False,False)


#helper line class
class Line:

	def __init__(self, l):
		rho,theta = l[0]
		a = np.cos(theta)
		b = np.sin(theta)
		x0 = a*rho
		y0 = b*rho
		x1 = int(x0 + 1000*(-b))
		y1 = int(y0 + 1000*(a))
		x2 = int(x0 - 1000*(-b))
		y2 = int(y0 - 1000*(a))

		self.point = x1, y1, x2, y2
		self.center = centerPts(x1,y1,x2,y2)

def thr_while(image):
	
	# image = cv2.blur(image, (3, 3)) #if necessary
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #convert to hsv

	# define range of white color in HSV
	lower_white = np.array([0,0,255-sensitivity])
	upper_white = np.array([255,sensitivity,255])

	# Threshold the HSV image to get only white colors
	mask = cv2.inRange(hsv, lower_white, upper_white)
	return mask

def draw(img, obj, col):
	#base line, double sideline, single side line
	x1, y1, x2, y2 = obj.point
	x, y = obj.center
	cv2.line(img, (x1, y1), (x2, y2), col, 2)


def draw_line(img, arr, col, num = 1):
	for i in range(num):
		if i == 1:
			col =(0,255,0)
		draw(img, arr.pop(0), col)
		draw(img, arr.pop(len(arr) - 1), col)


if __name__ == "__main__":
	for img_path in glob.glob(db_path+"*.jpg"):
		image = cv2.imread(img_path)
		# image = cv2.blur(image, (2, 2))
		resize_image = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
		global h_proc, w_proc
		h_proc, w_proc, _ = resize_image.shape 

		mask = thr_while(resize_image)
		# show(mask,"thr_image")

		element = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
		skel = np.zeros(mask.shape,np.uint8)
		size = np.size(mask)

		done = False
		while( not done):
			eroded = cv2.erode(mask,element)
			temp = cv2.dilate(eroded,element)
			temp = cv2.subtract(mask,temp)
			skel = cv2.bitwise_or(skel,temp)
			mask = eroded.copy()

			zeros = size - cv2.countNonZero(mask)
			if zeros==size:
				done = True

		# show(skel,"skel")

		lines = cv2.HoughLines(skel, 1, 3*np.pi/180, 90)

		arr=[]
		if lines == None:
			print "no lines detected"
		elif len(lines) >= 6: 
			for l in lines:
				line_obj = Line(l)
				arr.append(line_obj)

			arr.sort(key=lambda l: (l.center[1]))
			draw_line(resize_image,arr,(0,0,255))
			arr.sort(key=lambda l: (l.center[0]))
			draw_line(resize_image,arr,(0,255,255), 2)
			name = os.path.split(img_path)[-1]
			cv2.imwrite("output/"+name, resize_image)
			# show(resize_image,"draw_image")
