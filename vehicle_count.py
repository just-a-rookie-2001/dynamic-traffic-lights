# Import system packages
from time import sleep
from datetime import timedelta, datetime
import sys, collections
# import third party packages
import numpy as np
import cv2
import serial




input_size = 320

# Detection confidence threshold
confThreshold =0.2
nmsThreshold= 0.2

font_color = (0, 0, 255)
font_size = 1
font_thickness = 4

# Store Coco Names in a list
classesFile = "coco.names"
classNames = open(classesFile).read().strip().split('\n')

# class index for our required detection classes
required_class_index = [2, 3, 5, 7]

## Model Files
modelConfiguration = 'yolov3-320.cfg'
modelWeigheights = 'yolov3-320.weights'

# configure the network model
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeigheights)

# Define random colour for each class
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(classNames), 3), dtype='uint8')


# Function for finding the detected objects from the network output
def postProcess(outputs,img):
    height, width = img.shape[:2]
    boxes = []
    detected_classNames = []
    classIds = []
    confidence_scores = []
    detection = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if classId in required_class_index:
                if confidence > confThreshold:
                    w,h = int(det[2]*width) , int(det[3]*height)
                    x,y = int((det[0]*width)-w/2) , int((det[1]*height)-h/2)
                    boxes.append([x,y,w,h])
                    classIds.append(classId)
                    confidence_scores.append(float(confidence))

    # Apply Non-Max Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidence_scores, confThreshold, nmsThreshold)
    # print(classIds)
    if len(indices)>0:
        for i in indices.flatten():
            x, y, w, h = boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]
            color = [int(c) for c in colors[classIds[i]]]
            name = classNames[classIds[i]]
            detected_classNames.append(name)
            # Draw classname and confidence score 
            cv2.putText(img,f'{name.upper()} {int(confidence_scores[i]*100)}%',
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            # Draw bounding rectangle
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
            detection.append([x, y, w, h, required_class_index.index(classIds[i])])

    return detected_classNames


def from_static_image():

    # Initialize the videocapture object
    cap = cv2.VideoCapture("/dev/video2")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    img = None
    current_time = datetime.now() + timedelta(seconds=2)
    while datetime.now() < current_time:
        success, img = cap.read()
        cv2.imshow("image", img)
        cv2.moveWindow("image", 0,0)
        if not success:
            sys.exit("Not able to capture Image")
        key = cv2.waitKey(1)
        if  key == ord('q'):
            exit()
        elif key == 32:
            break
    
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (input_size, input_size), [0, 0, 0], 1, crop=False)

    # Set the input of the network
    net.setInput(blob)
    layersNames = net.getLayerNames()
    outputNames = [(layersNames[i - 1]) for i in net.getUnconnectedOutLayers()]
    # Feed data to the network
    outputs = net.forward(outputNames)

    # Find the objects from the network output
    results = postProcess(outputs,img)

    # count the frequency of detected classes
    frequency = collections.Counter(results)

    # Draw counting texts in the frame
    cv2.putText(img, "Car:        "+str(frequency['car']), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img, "Motorbike:  "+str(frequency['motorbike']), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img, "Bus:        "+str(frequency['bus']), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img, "Truck:      "+str(frequency['truck']), (20, 160), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)

    cv2.imshow("image", img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

    total_objects = frequency['car'] + frequency['motorbike'] + frequency['bus'] + frequency['truck']
    return total_objects

if __name__ == '__main__':
    from_static_image()
    # link to arduino serial monitor
    ArduinoSerial=serial.Serial('/dev/ttyACM1',9600,timeout=1)
    ArduinoSerial.flush()
    while True:
        if ArduinoSerial.in_waiting > 0:
            line = ArduinoSerial.readline().decode('utf-8').rstrip()
            # if command by arduino to perform ML, then do so
            if line=="capture":
                total_objects = 0
                total_objects = from_static_image()
                print(total_objects, "vehicles detected")
                # replay back to arduino
                final_string = str(total_objects)+"\n"
                ArduinoSerial.write(final_string.encode('utf-8'))
                ArduinoSerial.flush()
        sleep(2)
