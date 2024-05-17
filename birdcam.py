# A modified version of core-electronics.com.au Tim's object-ident-2.py python script
# from their project "Object and Animal Recognition With Raspberry Pi and OpenCV"
# https://core-electronics.com.au/guides/raspberry-pi/object-identify-raspberry-pi/
 
import cv2
import time
import requests
# import time # for image timestamp
from datetime import datetime
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
import os
import sys
from gpiozero import CPUTemperature

timer = 1  # counter to display message program is running  
counter = 1 # counter to show program still running
cput = CPUTemperature()
classNames = []
classFile = "/home/user/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/user/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/user/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

interval = 10


def envoyer_image(filename):
    url = "URL_DU_SITE"  # Remplacez par l'URL de votre API

    # Ouvrez l'image en mode binaire
    with open(filename, 'rb') as f:
        image_data = f.read()

    # Créez un dictionnaire pour le paramètre `files`
    file = {'file': image_data}

    # Envoyez la requête POST
    response = requests.post(url, files=file)

    # Vérifiez la réponse
    if response.status_code == 200:
        print("Image envoyée avec succès.")
    else:
        print("Erreur lors de l'envoi de l'image.")
        print(response)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):

# optional ... captures unannotated time-stamped scanning frame with suffix -1 when object detected
                    os.chdir("/home/user/Desktop/Object_Detection_Files/obj_log")
                    cv2.imwrite("Trigger_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3] +"_1.jpg",img)

#                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
#                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
#                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
#                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
#                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
# optional ... captures annotated time-stamped scanning frame with suffix -2 when object detected to assist investigation of false alarms
#                    os.chdir("/home/pi/Desktop/Object_Detection_Files/obj_log")
#                    cv2.imwrite("Trigger_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3] +"_2.jpg",img)
# ... save scanning frame to Lychee import folder
                    os.chdir("/home/user/Images")
                    image_name = "Trigger_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3] +".jpg"
                    cv2.imwrite(image_name,img)
                    path_to_image = "/home/user/Images/"+image_name
                    envoyer_image(path_to_image)
                    try:
                        os.remove(path_to_image) #TO remove image from local files
                        print(f"{image_name} a ete supprimer")
                    except:
                        print(f"{image_name} n`a pas pu etre supprimer. {path_to_image} n`existe pas.")

    return img,objectInfo



def captureImage():
    cap = cv2.VideoCapture(0)
    time.sleep(5)
    cap.set(3,1920)
    cap.set(4,1080)
    cap.set(10,125)
    scale = 35
    timer = 0
    counter = 0

    try:
        while True:
            
                
            success, image = cap.read()
            
            
            height, width, channels = image.shape
            centerX,centerY=int(height/2),int(width/2)
            radiusX,radiusY= int(scale*height/100),int(scale*width/100)
            
            minX,maxX=centerX-radiusX,centerX+radiusX
            minY,maxY=centerY-radiusY,centerY+radiusY

            cropped = image[minX:maxX, minY:maxY]
            resized_cropped = cv2.resize(cropped, (width, height)) 
            
            result, objectInfo = getObjects(resized_cropped,0.35, 0.5, objects=['bird'])

            timer += 1
            if timer == 25:
                counter += 1
                print(counter, " Scanning for birds...    CPU " + str(round(cput.temperature,1)) + " oC      to EXIT PROGRAM PRESS [Ctrl-C]")
                timer = 1

            if len(objectInfo) != 0:
                print("PHOTO TAKEN")
                print(f"Waiting for {interval} seconds")
                time.sleep(interval)
                cap.release()
                cv2.destroyAllWindows()
                quit()
                
                
    #           quit()  #  bird spotted ... quit python / opencv to take hires image burst series (need to release camera)
               # print("OISEAU DETECTE")
               # objectInfo = []
    #        optional - crashes program if there is no LCD screen/GUI connected to rpi
    #        cv2.imshow("Output",img) # uncomment this line to see object recognition output window if RPi connected to LCD screen/GUI

    # Exits program on [Ctrl-C] keypress
    except KeyboardInterrupt:
            print("\nUser Initiated Exit!")
            raise SystemExit(1)



    

if __name__ == "__main__":
    print(counter, " Scanning for birds...    CPU " + str(round(cput.temperature,1)) + " oC      to EXIT PROGRAM PRESS [Ctrl-C]")
   
    captureImage()
