#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
import argparse
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

class MemoryCameraFollower:
    def __init__(self, topic_name):
        rospy.init_node('memory_camera_follower', anonymous=True)
        self.bridge = CvBridge()
        
        self.image_sub = rospy.Subscriber(topic_name, Image, self.image_callback)
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.twist = Twist()
        
        # --- NUEVAS VARIABLES DE CONTROL Y MEMORIA ---
        self.kp = 0.009 # Constante proporcional: aumenta este valor para giros más agresivos
        self.ultima_posicion_x = 0 # Guarda si la pelota estaba a la izquierda (-) o derecha (+)
        self.tiempo_ultimo_visto = 0.0 # Marca de tiempo de la última vez que vio la pelota
        self.tiempo_memoria = 3.0 # Segundos que pasará buscando la pelota antes de rendirse
        
        rospy.on_shutdown(self.stop_robot)
        rospy.loginfo(f"Iniciando seguidor con memoria. Escuchando: {topic_name}")

    def stop_robot(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        self.cmd_pub.publish(self.twist)

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        height, width, _ = cv_image.shape
        total_area = height * width 
        
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_green = np.array([35, 170, 110])
        upper_green = np.array([55, 255, 238])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        ball_found = False

        if len(contours) > 0:
            valid_contours = [c for c in contours if cv2.contourArea(c) < (total_area * 0.3)]

            if len(valid_contours) > 0:
                c = max(valid_contours, key=cv2.contourArea)
                area = cv2.contourArea(c)
                M = cv2.moments(c)
                
                if M['m00'] > 0:
                    cx = int(M['m10']/M['m00'])
                    error_x = cx - width/2
                    
                    # 1. ACTUALIZAR MEMORIA
                    self.ultima_posicion_x = error_x
                    self.tiempo_ultimo_visto = rospy.get_time()
                    
                    if area > (total_area * 0.20): 
                        self.twist.linear.x = 0.0
                    else:
                        self.twist.linear.x = 0.2
                        
                    # 2. APLICAR CONTROL PROPORCIONAL AL GIRO (Kp)
                    self.twist.angular.z = -float(error_x) * self.kp
                    ball_found = True
                    
                    cv2.circle(cv_image, (cx, int(M['m01']/M['m00'])), 10, (0,0,255), -1)

        # 3. LÓGICA DE BÚSQUEDA SI NO HAY PELOTA
        if not ball_found:
            # Solo buscar si ya la habíamos visto alguna vez
            if self.tiempo_ultimo_visto > 0:
                tiempo_perdido = rospy.get_time() - self.tiempo_ultimo_visto
                
                if tiempo_perdido < self.tiempo_memoria:
                    self.twist.linear.x = 0.0 # Frenar el avance
                    # Girar hacia la última dirección conocida
                    if self.ultima_posicion_x < 0:
                        self.twist.angular.z = 0.4 # Estaba a la izquierda
                    else:
                        self.twist.angular.z = -0.4 # Estaba a la derecha
                    cv2.putText(cv_image, "Buscando...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                else:
                    self.twist.linear.x = 0.0
                    self.twist.angular.z = 0.0
            else:
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.0

        self.cmd_pub.publish(self.twist)
        cv2.imshow("Camara Memoria", cv_image)
        cv2.waitKey(3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seguidor con memoria")
    parser.add_argument('-m', '--mode', type=str, choices=['real', 'virtual'], default='real')
    args = parser.parse_args(rospy.myargv()[1:])
    
    topic = "/usb_cam/image_raw" if args.mode == 'real' else "/sim_camera/image_raw"

    try:
        MemoryCameraFollower(topic)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    cv2.destroyAllWindows()