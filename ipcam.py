#import urllib
import urllib.request
import cv2
import numpy as np
import time
# Replace the URL with your own IPwebcam shot.jpg IP:port
#url='http://192.168.43.1:8080/shot.jpg'
url='http://10.0.0.56:8080//shot.jpg'

img_counter = 0

while True:
# Use urllib to get the image and convert into a cv2 usable format
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
# put the image on screen
    cv2.imshow('IPWebcam',img)
    k = cv2.waitKey(1)
#To give the processor some less stress
    #time.sleep(0.1) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

   
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.jpg".format(img_counter)
        cv2.imwrite("C:/Users/Daniel Chu/Desktop/opencv_chessboard_recognizer_v3/c"+img_name, img)
        print("{} written!".format(img_name))
        img_counter += 1

