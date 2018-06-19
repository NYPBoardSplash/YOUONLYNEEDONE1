#import urllib
import urllib.request
import cv2
import numpy as np
import time

#import Flask here
from flask import Flask, jsonify
from flask import make_response
from flask import abort,request
import os
from subprocess import call, PIPE, Popen
import subprocess

app = Flask(__name__)

# Replace the URL with your own IPwebcam shot.jpg IP:port
#url='http://192.168.43.1:8080/shot.jpg'
#url='http://10.0.0.56:8080//shot.jpg'
#url='http://172.20.10.5:8080/shot.jpg'
url='http://172.20.10.7:8080/shot.jpg'

img_counter=0


#default route
@app.route("/")
def hello():
    return "Hello World!"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/redbasic")
def redbasic():
    global img_counter

    img_name = "frame_{}".format(img_counter)
    folder = "C:\\Users\\Daniel Chu\\Desktop\\opencv_chessboard_recognizer_v3\\"
    out_folder = folder + "\\out\\"
    in_img_file_name = out_folder + "cam_" + img_name + ".jpg"
    out_img_file_name = out_folder + "out_" + img_name + ".jpg"
    ucci_txt_file_name = out_folder + "ucci_" + img_name + ".txt"
    outmove_txt_file_name = out_folder + "move_" + img_name + ".txt"

    # Use urllib to get the image and convert into a cv2 usable format
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
    # put the image on screen
    #cv2.imshow('IPWebcam',img)
    #k = cv2.waitKey(1)
    cv2.imwrite(in_img_file_name, img)

    bestmove = ""

    try:
        print ("Opening recognizer...")
        subprocess.call([
            "D:\\Program Files (x86)\\Python3.6forWindow\\python.exe", 
            folder + "recognizeboard.py",
            "run",
            in_img_file_name,
            out_img_file_name,
            ucci_txt_file_name,
            "w",
            "easy"
            ])
       
        
        print ("Executing ELEEYE...")
        file_in = open(ucci_txt_file_name, "r")
        file_out = open(outmove_txt_file_name, "w+")
        subprocess.call(
            [folder + 'eleeye.exe'], stdout=file_out, stdin=file_in)
        file_out.close()
        file_in.close()
        
        print ("Extracting Best Move...")
        file_read = open(outmove_txt_file_name, "r")
        while True:
            s = file_read.readline()
            if s.find("bestmove") >= 0:
                sp = s.split(' ')
                bestmove = sp[1]
                print ("Best Move: " + sp[1])
                break
            if s == "":
                break
        file_read.close()
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to fetch task status updates."

    
    #print("{} written!".format(img_name))
    img_counter += 1   
    return bestmove


@app.route("/redadv")
def redadv():
    global img_counter

    img_name = "frame_{}".format(img_counter)
    folder = "C:\\Users\\Daniel Chu\\Desktop\\opencv_chessboard_recognizer_v3\\"
    out_folder = folder + "\\out\\"
    in_img_file_name = out_folder + "cam_" + img_name + ".jpg"
    out_img_file_name = out_folder + "out_" + img_name + ".jpg"
    ucci_txt_file_name = out_folder + "ucci_" + img_name + ".txt"
    outmove_txt_file_name = out_folder + "move_" + img_name + ".txt"

    # Use urllib to get the image and convert into a cv2 usable format
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
    # put the image on screen
    #cv2.imshow('IPWebcam',img)
    #k = cv2.waitKey(1)
    cv2.imwrite(in_img_file_name, img)

    bestmove = ""

    try:
        print ("Opening recognizer...")
        subprocess.call([
            "D:\\Program Files (x86)\\Python3.6forWindow\\python.exe", 
            folder + "recognizeboard.py",
            "run",
            in_img_file_name,
            out_img_file_name,
            ucci_txt_file_name,
            "w",
            "basic"
            ])
       
        
        print ("Executing ELEEYE...")
        file_in = open(ucci_txt_file_name, "r")
        file_out = open(outmove_txt_file_name, "w+")
        subprocess.call(
            [folder + 'eleeye.exe'], stdout=file_out, stdin=file_in)
        file_out.close()
        file_in.close()
        
        print ("Extracting Best Move...")
        file_read = open(outmove_txt_file_name, "r")
        while True:
            s = file_read.readline()
            if s.find("bestmove") >= 0:
                sp = s.split(' ')
                bestmove = sp[1]
                print ("Best Move: " + sp[1])
                break
            if s == "":
                break
        file_read.close()
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to fetch task status updates."

    
    #print("{} written!".format(img_name))
    img_counter += 1   
    return bestmove


@app.route("/blackbasic")
def blackbasic():
    global img_counter

    img_name = "frame_{}".format(img_counter)
    folder = "C:\\Users\\Daniel Chu\\Desktop\\opencv_chessboard_recognizer_v3\\"
    out_folder = folder + "\\out\\"
    in_img_file_name = out_folder + "cam_" + img_name + ".jpg"
    out_img_file_name = out_folder + "out_" + img_name + ".jpg"
    ucci_txt_file_name = out_folder + "ucci_" + img_name + ".txt"
    outmove_txt_file_name = out_folder + "move_" + img_name + ".txt"

    # Use urllib to get the image and convert into a cv2 usable format
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
    # put the image on screen
    #cv2.imshow('IPWebcam',img)
    #k = cv2.waitKey(1)
    cv2.imwrite(in_img_file_name, img)

    bestmove = ""

    try:
        print ("Opening recognizer...")
        subprocess.call([
            "D:\\Program Files (x86)\\Python3.6forWindow\\python.exe", 
            folder + "recognizeboard.py",
            "run",
            in_img_file_name,
            out_img_file_name,
            ucci_txt_file_name,
             "b",
             "adv"
            ])
       
        
        print ("Executing ELEEYE...")
        file_in = open(ucci_txt_file_name, "r")
        file_out = open(outmove_txt_file_name, "w+")
        subprocess.call(
            [folder + 'eleeye.exe'], stdout=file_out, stdin=file_in)
        file_out.close()
        file_in.close()
        
        print ("Extracting Best Move...")
        file_read = open(outmove_txt_file_name, "r")
        while True:
            s = file_read.readline()
            if s.find("bestmove") >= 0:
                sp = s.split(' ')
                bestmove = sp[1]
                print ("Best Move: " + sp[1])
                break
            if s == "":
                break
        file_read.close()
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to fetch task status updates."

    
    #print("{} written!".format(img_name))
    img_counter += 1   
    return bestmove


@app.route("/blackadv")
def blackadv():
    global img_counter

    img_name = "frame_{}".format(img_counter)
    folder = "C:\\Users\\Daniel Chu\\Desktop\\opencv_chessboard_recognizer_v3\\"
    out_folder = folder + "\\out\\"
    in_img_file_name = out_folder + "cam_" + img_name + ".jpg"
    out_img_file_name = out_folder + "out_" + img_name + ".jpg"
    ucci_txt_file_name = out_folder + "ucci_" + img_name + ".txt"
    outmove_txt_file_name = out_folder + "move_" + img_name + ".txt"

    # Use urllib to get the image and convert into a cv2 usable format
    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)
    # put the image on screen
    #cv2.imshow('IPWebcam',img)
    #k = cv2.waitKey(1)
    cv2.imwrite(in_img_file_name, img)

    bestmove = ""

    try:
        print ("Opening recognizer...")
        subprocess.call([
            "D:\\Program Files (x86)\\Python3.6forWindow\\python.exe", 
            folder + "recognizeboard.py",
            "run",
            in_img_file_name,
            out_img_file_name,
            ucci_txt_file_name,
             "b",
             "adv"
            ])
       
        
        print ("Executing ELEEYE...")
        file_in = open(ucci_txt_file_name, "r")
        file_out = open(outmove_txt_file_name, "w+")
        subprocess.call(
            [folder + 'eleeye.exe'], stdout=file_out, stdin=file_in)
        file_out.close()
        file_in.close()
        
        print ("Extracting Best Move...")
        file_read = open(outmove_txt_file_name, "r")
        while True:
            s = file_read.readline()
            if s.find("bestmove") >= 0:
                sp = s.split(' ')
                bestmove = sp[1]
                print ("Best Move: " + sp[1])
                break
            if s == "":
                break
        file_read.close()
    except subprocess.CalledProcessError as e:
        return "An error occurred while trying to fetch task status updates."

    
    #print("{} written!".format(img_name))
    img_counter += 1   
    return bestmove


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
