#FaceTracking'
import cv2
import numpy as np

forward_backward_range = [6200, 6800]
pid = [0.4, 0.4, 0]
w, h = 360, 240
pError = 0

def findFace(img):
	faceCascade = cv2.CascadeClassifier("/ml_resources/haarcascade_frontalface_default.xml")
	imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(imgGray, 1.2, int(8))

	myFaceListC = []
	myFaceListArea = []

	for (x,y,w,h) in faces:
		cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
		cx = x + w/2
		cy = y + h/2
		area = w * h
		cv2.circle(img, (int(cx), int(cy)), 5, (0, 255, 0), cv2.FILLED)
		myFaceListC.append([cx, cy])
		myFaceListArea.append(area)

	if len(myFaceListC) != 0:
		i = myFaceListArea.index(max(myFaceListArea))
		return img, [myFaceListC[i], myFaceListArea[i]]
	else:
		return img, [[0, 0], 0]


def trackFace(me, info, w, pid, pError):

	area = info[1]
	x, y = info[0]

	#Find how far off from the center we are
	error = x - w//2
	yaw_speed = pid[0] * error + pid[1] * (error - pError)
	yaw_speed = int(np.clip(yaw_speed, -100, 100))

	forward_backward = 0
	if area > forward_backward_range[1]:
		forward_backward = -20
	elif area < forward_backward_range[0] and area != 0:
		forward_backward = 20

	if x == 0:
		yaw_speed = 0
		error = 0

	me.send_rc_control(0, forward_backward, 0, yaw_speed)
	return error

cap = cv2.VideoCapture(0)
while True:
	_, img = cap.read()
	img = cv2.resize(img, (w,h))
	img, info = findFace(img)
	pError = trackFace(me, info, w, pid, pError)
	print("Center ", info[0], "area ", info[1])
	cv2.imshow("Output", img)
	cv2.waitKey(1)

