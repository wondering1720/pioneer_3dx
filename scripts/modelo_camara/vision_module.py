import cv2
import numpy as np

class VisionProcessor:
    def __init__(self, lower_hsv=(30, 87, 110), upper_hsv=(55, 255, 255)):
        self.lower_hsv = np.array(lower_hsv)
        self.upper_hsv = np.array(upper_hsv)
        
        # EL CONTROLADOR DE FUERZA: Cambia este (5, 5) por (3, 3) para menos fuerza, o (9, 9) para más fuerza
        self.kernel = np.ones((5, 5), np.uint8)

    def process_image(self, cv_image):
        height, width, _ = cv_image.shape
        total_area = height * width
        
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)

        # CONTROLADOR DE PASADAS: Cambia iterations=1 por 2 o 3 para un efecto más intenso
        #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=3)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        ball_found = False
        error_x = 0
        area = 0

        if len(contours) > 0:
            valid_contours = [c for c in contours if 5 < cv2.contourArea(c) < (total_area * 0.3)]
            
            if len(valid_contours) > 0:
                c = max(valid_contours, key=cv2.contourArea)
                area = cv2.contourArea(c)
                M = cv2.moments(c)
                
                if M['m00'] > 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    error_x = cx - width/2
                    ball_found = True
                    
                    cv2.drawContours(cv_image, [c], -1, (0, 255, 0), 2)
                    cv2.circle(cv_image, (cx, cy), 5, (0, 0, 255), -1)
        
        # FÍJATE AQUÍ: Ahora devolvemos también la variable "mask" al final
        return ball_found, error_x, area, total_area, cv_image, mask