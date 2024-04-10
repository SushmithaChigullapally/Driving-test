# -*- coding: utf-8 -*-
"""Driving Test Tracker

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NBUBdZCkApbNGmFPE-u8C20UsJMD2mpW
"""



!nvidia-smi  #To check the status and information about Nvidia GPU's istalled on a system

import os
HOME=os.getcwd() #for current working directory
print(HOME)

SOURCE_VIDEO_PATH ='/content/drive/MyDrive/PS3-1/tracktest.mp4'

!pip install ultralytics==8.0.10  #for object detection and segmentation tasks
 from IPython import display  #for displaying various types of objects
 display.clear_output()
 import ultralytics
 ultralytics.checks()

from google.colab import drive
drive.mount('/content/drive')

!pip install supervision==0.1.0   #To load, split, merge, and save datasets
from IPython import display
display.clear_output()
import supervision
print("supervision.__version__:", supervision.__version__)

model1="yolov8x.pt"

from ultralytics import YOLO
model=YOLO(model1)
model.fuse()  #for model optimization

#!yolo task=detect mode=predict model=yolov8x.pt conf=0.25 source={SOURCE_VIDEO_PATH}

from supervision.video.dataclasses import VideoInfo
VideoInfo.from_video_path(SOURCE_VIDEO_PATH)

#dictionary mapping class id to class name.
CLASS_NAMES_DICT=model.model.names
print(model.model.names)

TARGET_VIDEO_PATH=f"{HOME}/lane_frame_detect.mp4"

from supervision.video.source import get_video_frames_generator
from supervision.notebook.utils import show_frame_in_notebook
from supervision.tools.detections import Detections, BoxAnnotator
from supervision.draw.color import ColorPalette
from supervision.video.sink import VideoSink
import math
from tqdm.notebook import tqdm
from scipy.spatial import distance as dist
import numpy as np
import sys
import cv2
l1=[]
generator=get_video_frames_generator(SOURCE_VIDEO_PATH)
video_info=VideoInfo.from_video_path(SOURCE_VIDEO_PATH)   #Its purpose is to create an instance of the VideoInfo class
max1=sys.maxsize
max2=sys.maxsize
with VideoSink(TARGET_VIDEO_PATH, video_info) as sink:  #VideoSink class is responsible for handling video output, such as writing frames to a video file.
    for frame in tqdm(generator, total=video_info.total_frames):
      results=model(frame)[0]
      detections=Detections(
          xyxy=results.boxes.xyxy.cpu().numpy(),
          confidence=results.boxes.conf.cpu().numpy(),
          class_id=results.boxes.cls.cpu().numpy().astype(int),
      )
      new_detections=[]
      for _,confidence,class_id,tracker_id in detections:
        # print(_,confidence,class_id,tracker_id)
        if(class_id==2 or class_id ==5 or class_id==7):
          l1=[]
          l1.append(_)
          new_detections.append(l1)
          break
      for i in new_detections:
        for j in i:
          # print(j)
          x1=int(j[0])
          y1=int(j[1])
          x3=int(j[2])
          y3=int(j[3])
          # print(x1,y1,x3,y3)
          roi_vertices = [
            ((int((x1+x3)/2)-500),y3+150),  # Bottom-left
            ((int((x1+x3)/2)-500),y1),  # Top-left
            (int((x1+x3)/2),y1),  # Top-right
            (int((x1+x3)/2),(y3+150)),  # Bottom-right
          ]
          roi_vertices1 = [
            ((int((x1+x3)/2)+500),y3+150),  # Bottom-right
            ((int((x1+x3)/2)+500),y1),  # Top-right
            (int((x1+x3)/2),y1),  # Top-left
            (int((x1+x3)/2),(y3+150)),  # Bottom-left
          ]
          # cv.circle(frame, (a, y3-70), 10, (255, 0, 255), -1)  # -1 means fill the circle
          # cv.rectangle(frame,((int((x1+x3)/2)-500),y1),(int((x1+x3)/2),(y3+150)), (255, 255, 0), 5)
          cv2.rectangle(frame,(x1,y1),(x3,y3), (0, 255, 0), 4)
          # Create an empty mask with the same dimensions as the image
          mask = np.zeros_like(frame)

          # Fill the ROI polygon with white color (255, 255, 255)
          cv2.fillPoly(mask, [np.array(roi_vertices)], (255, 255, 255))
          cv2.fillPoly(mask, [np.array(roi_vertices1)], (255, 255, 255))
          # Bitwise AND the original image and the mask to isolate the ROI
          roi_image = cv2.bitwise_and(frame, mask)
          roi_image1 = cv2.bitwise_and(frame, mask)
          gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
          gray1 = cv2.cvtColor(roi_image1, cv2.COLOR_BGR2GRAY)
          # Apply Gaussian blur to reduce noise and enhance edges
          blurred = cv2.GaussianBlur(gray, (7, 7), 0)
          blurred1 = cv2.GaussianBlur(gray1, (7, 7), 0)
          # Perform edge detection using Canny
          edges = cv2.Canny(blurred, 100, 150)
          edges1 = cv2.Canny(blurred1, 100, 150)
          # Find lines in the image using Hough Line Transform
          lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)
          lines1 = cv2.HoughLinesP(edges1, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)
          for line in lines:
            x, y, x2, y2 = line[0]
            if((x>(((x1+x3)/2)-500) and x<x1 and y<(y3+150) and y>y1) and (x2>(((x1+x3)/2)-500) and x2<x1 and y2<(y3+150) and y2>y1)):
              a1,b1=(x+x2)/2,(y+y2)/2
              a2,b2=(x1+x3)/2,(y1+y3)/2
              p1=(a1,b1)
              p2=(a2,b2)
              if(math.sqrt((a2-a1)**2+(b2-b1)**2)<325):
                print(math.sqrt((a2-a1)**2+(b2-b1)**2),"left")
                cv2.line(frame, (x, y), (x2, y2), (255, 0, 0), 5)
                sink.write_frame(frame)
          for line in lines1:
            x, y, x2, y2 = line[0]
            if((x<(((x1+x3)/2)+500) and x>x3 and y<(y3+150) and y>y3) and (x2<(((x1+x3)/2)+500) and x2>x3 and y2<(y3+150) and y2>y1)):
              a1,b1=(x+x2)/2,(y+y2)/2
              a2,b2=(x1+x3)/2,(y1+y3)/2
              p1=(a1,b1)
              p2=(a2,b2)
              if(math.sqrt((a2-a1)**2+(b2-b1)**2)<325):
                cv2.line(frame, (x, y), (x2, y2), (255, 0, 0), 5)
                sink.write_frame(frame)

