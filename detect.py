from math import sqrt
import cv2
import time
import dlib

cars_cascade = cv2.CascadeClassifier('carsCascade.xml')
vc = cv2.VideoCapture('autostrada.mp4')
font = cv2.FONT_HERSHEY_SIMPLEX
garage = []

yoff = 150
xoff = 100
diff = 10
numCarsToTrack = 1;

def main():
    i = 0
    while(1):
        rval, frame = vc.read()
        detectionFragment = frame[xoff::,yoff::] #wyciety kawalek trawy
        cars = cars_cascade.detectMultiScale(detectionFragment, 1.1, 2)
        
        for (x,y,w,h) in cars[0:numCarsToTrack]:
                    
            #jest limit na samochody, bo algorytm dosyc kosztowny
            if numCarsToTrack - len(garage) > 0:
                canAdd = 1
            
                for car in garage:
                    car.updatePosition(frame)
                    
                    #nie chcemy przeciez zaznaczac tego samego samochodu kilkukrotnie
                    if (abs(car.x - (x+yoff)) < diff) and (abs(car.y - (y+xoff)) < diff):
                        canAdd = 0        
               
                if canAdd == 1:
                    garage.append(Car(x,y,h,w,frame))
                  
        for car in garage:
        
            #numFrames to liczba klatek przez ktore samochod ma byc zaznaczony, a ten y > 200 dlatego, ze tam sie gubi :x
            if car.numFrames < 0 or car.y > 200: 
                garage.remove(car)
                
            #predkosc liczona tylko raz, po przebyciu 10 klatek (wtedy ma ten atrybut speed)
            if len(car.positions) > 10 and not hasattr(car,'speed'):
                car.tellMeBitchWhatSpeedIs()
            elif len(car.positions) > 10:
                cv2.putText(frame,str(car.speed)+' km/h',(car.x+car.w,car.y),font,0.5,(255,255,255))
           
            #rysuje sledzione
            pos = car.getPosition(frame)
            cv2.rectangle(frame,pos[0],pos[1],(255,0,0),2)
            
            #wyswietl wariata
            if hasattr(car,'speed') and car.speed > 0 and numCarsToTrack == 1:
                showFragment(pos[0],pos[1],frame,100)
                
        #TODO: tego sledzonego mozna stad wywalic
        for (x,y,w,h) in cars:
            cv2.rectangle(frame,(x+yoff,y+xoff),(x+w+yoff,y+h+xoff),(0,0,255),2)      
        
        cv2.imshow("Result", frame)
        k = cv2.waitKey(5) & 0xFF
        if k == 27: #ESC
            break
        
    vc.release()
    cv2.destroyAllWindows()
    
    
class Car:
    def __init__(self,x,y,h,w,frame):
        self.numFrames = 80
        self.tracker = dlib.correlation_tracker()
        self.tracker.start_track(frame, dlib.rectangle(int(x+yoff), int(y+xoff), int(x+yoff+w), int(y+xoff+h)))
        self.positions = []
        self.x = 0
        self.y = 0
        
    def getPosition(self,frame):
        self.updatePosition(frame)
        self.positions.append([self.x,self.y])
        return (self.x,self.y),(self.x+self.w,self.y+self.h)
        
    def updatePosition(self,frame):
        self.numFrames = self.numFrames - 1
        self.tracker.update(frame)
        pos = self.tracker.get_position()
        self.x = int(pos.left())
        self.y = int(pos.top())
        self.h = int(pos.height())
        self.w = int(pos.width())
        
    def tellMeBitchWhatSpeedIs(self):
        x1 =self.positions[0][0]
        x2 = self.positions[len(self.positions)-1][0]
        y1 = self.positions[0][1]
        y2 = self.positions[len(self.positions)-1][1]
        self.speed = round(sqrt((y2-y1)**2 + (x2-x1)**2))*4  
    
def showFragment(leftUp,rightDown,frame,size):
    x = leftUp[0] #4 cwiartka
    y = leftUp[1]
    w = rightDown[0] - leftUp[0]
    h = rightDown[1] - leftUp[1]
    cutedFragment = frame[y:y+w,x:x+h]
    res = cv2.resize(cutedFragment,(size,size), interpolation = cv2.INTER_CUBIC)
    frame[0:size,0:size] = res
    
        
if __name__ == '__main__':
    main()
