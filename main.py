import cv2 as cv
import mediapipe as mp
import math
import random
import time
from google.protobuf.json_format import MessageToDict

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# define video path
video_path = 1
video = cv.VideoCapture(video_path)
# SETUP
# Hand 
ideightl = (1,1)
idfourl = (1,100)
idtwelvel = (1,1)
idzerol = (1,100)
idzeror = (1,1)
hand_angle = 0
reload = True
shoot = 0
# Game
monsters = []
monsters_speed = 3
spawn_rate = 3
score = 0
total_monster = 10
health = 3
# function
def circle_landmark(f,cx,cy):
    cv.circle(f,(cx,cy),20,(0,255,0),2)
def distance(point1,point2):
    return int(math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2))
def middle_point(point1,point2):
    return (mid(point1[0],point2[0]),mid(point1[1],point2[1]))
    # return (point1+point2)/2

def mid(x,y):
    return int((x+y)/2)

def calculate_angle(point1, point2):
    # neg deg
    if(point1[1] > point2[1]):
        tmp = point2
        point2 = point1
        point1 = tmp
    delta_x = point2[0] - point1[0]
    delta_y = point2[1] - point1[1]
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)
    return 180-int(angle_deg)
# GAME
def spawn_monster():
    return {
        'x' : 200,
        'y': random.randint(50, 550),
        'speed' : monsters_speed
    }
def render_monster(frame,monster):
    cv.circle(frame, (monster['x'], monster['y']), 60, (0, 0, 255), -1)
def move_monster(monster):
    monster['x'] -= monster['speed']

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    
    while health != 0:
        ret, frame = video.read()
        frame = cv.flip(frame,1)
        if not ret:
            print("End of video.")
            break
        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        # GAME
        if(len(monsters)<4):
            if random.randint(0, 100) < spawn_rate:
                monster = spawn_monster()
                monsters.append(monster)
                total_monster-=1
        for monster in monsters:
            if(monster['x'] < 800):
                monsters.remove(monster)
                health -=1 
            move_monster(monster)
            render_monster(frame,monster)
        #------
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:    
                # LEFT OR RIGHT
                for i in results.multi_handedness: 
                    # "Left" / "Right"
                    label = MessageToDict(i)['classification'][0]['label'] 
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        height, width, _ = frame.shape
                        cx, cy = int(landmark.x * width), int(landmark.y * height)
                        # for left hand side
                        if(label == "Left"):
                            if(idx == 4):
                                circle_landmark(frame,cx,cy)
                                ideightl = (cx,cy)
                            if(idx == 8):
                                circle_landmark(frame,cx,cy)
                                idfourl  = (cx,cy)
                            if(idx == 12):
                                idtwelvel = (cx,cy)
                            if(idx == 0):
                                idzerol = (cx,cy)
                        elif(label == "Right"):
                            if(idx == 0):
                                idzeror = (cx,cy)
                    if(idzerol[0] != idzeror[0] and idzerol[1] != idzeror[1]):
                        
                        hand_angle = calculate_angle(idzerol,idzeror)
                        distance_bow = distance(idzerol,idzeror)
                        hand_size = distance(idtwelvel,idzerol)
                        hand_cmd = int(distance(ideightl,idfourl)/hand_size*100)
                        if(reload == True and distance_bow < 300):
                            reload = False
                        if(reload == False and hand_cmd > 60 and distance_bow > 800):
                            reload = True
                            shoot+=1
                            hit_target = False
                            for monster in monsters:
                                angle_montohand = calculate_angle((monster['x'],monster['y']),idzeror)
                                if(abs(angle_montohand-hand_angle) < 10):
                                    monsters.remove(monster)
                                    score+=1
                                    hit_target = True
                            if(not hit_target):
                                health-=1
                        # print(hand_angle)
                        # print("BOW",distance_bow)
                        # print("Hnad",hand_size)
                        # print("shoot ",shoot)
                        # cv.putText(frame,f"Bow : {int(distance_bow)}",(100,100),cv.FONT_HERSHEY_COMPLEX,3,(0,255,255),10)
                        cv.line(frame,idzerol,idzeror,(0,0,255),15)
                        cv.line(frame,ideightl,idfourl,(255,0,255),15)

                        # print("CAL",int(distance_bow/hand_size*4)*100)
                        # cv.putText(frame,f"Shoot : {shoot}",(100,200),cv.FONT_HERSHEY_COMPLEX,3,(0,0,255),10)
                        # cv.putText(frame,f"Dis :{int(distance(ideightl,idfourl)/hand_size*100)}",middle_point(ideightl,idfourl),cv.FONT_HERSHEY_COMPLEX,5,(0,0,255),6)
                        # cv.putText(frame,f"Angle : {hand_angle}",(100,100),cv.FONT_HERSHEY_COMPLEX,2,(0,0,255),3)
                    cv.rectangle(frame, (20,20), (700, 240), (0, 0, 0), -1)
                    cv.putText(frame,f"Health : {health}",(100,100),cv.FONT_HERSHEY_COMPLEX,3,(0, 0, 255),10)
                    cv.putText(frame,f"Score  : {score}",(100,200),cv.FONT_HERSHEY_COMPLEX,3,(255, 255,255),10)
                    if(not reload):
                        cv.putText(frame,f"Ready",(100,400),cv.FONT_HERSHEY_COMPLEX,3,(0,0,0),10)
                    # cv.putText(frame,f"Score : {score}",(100,200),cv.FONT_HERSHEY_COMPLEX,3,(128, 0, 128),10)
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    # print("-------")
                    
        cv.imshow('MediaPipe Hands', frame)
        
        # How to exit lol
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    if(health == 0):
        ret, frame = video.read()
        frame = cv.flip(frame,1)
        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        cv.rectangle(frame, (0,0), (2000,2000), (0, 0, 0), -1)
        cv.putText(frame,f"Game Over",(200,300),cv.FONT_HERSHEY_COMPLEX,5,(0, 0, 255),10)
        cv.putText(frame,f"Score {score}",(200,700),cv.FONT_HERSHEY_COMPLEX,5,(255, 20,20),10)
        cv.imshow('MediaPipe Hands', frame)
        cv.waitKey(1)

time.sleep(3)
video.release()
cv.destroyAllWindows()
