#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
import argparse
import sys
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

class NormalCameraFollower:
    def __init__(self, topic_name):
        rospy.init_node('normal_camera_follower', anonymous=True)
        self.bridge = CvBridge()
        
        # Escucha el tópico dinámico (usb_cam o sim_camera)
        self.image_sub = rospy.Subscriber(topic_name, Image, self.image_callback)
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.twist = Twist()
        
        rospy.on_shutdown(self.stop_robot)
        rospy.loginfo(f"Iniciando seguidor. Escuchando video en: {topic_name}")

    def stop_robot(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        self.cmd_pub.publish(self.twist)

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            return

        height, width, _ = cv_image.shape
        total_area = height * width 
        
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_green = np.array([50, 100, 100])
        upper_green = np.array([70, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        ball_found = False

        if len(contours) > 0:
            valid_contours = []
            for c in contours:
                area = cv2.contourArea(c)
                # REGLA 1: Ignorar ruido masivo (protección contra bugs de WSL2)
                if area < (total_area * 0.3):
                    valid_contours.append(c)

            if len(valid_contours) > 0:
                c = max(valid_contours, key=cv2.contourArea)
                area = cv2.contourArea(c)
                M = cv2.moments(c)
                
                if M['m00'] > 0:
                    cx = int(M['m10']/M['m00'])
                    error_x = cx - width/2
                    
                    # REGLA 2: Frenar por proximidad #######################################################################
                    if area > (total_area * 0.05): 
                        self.twist.linear.x = 0.0
                        print("¡Pelota cerca! Frenando.")
                    else:
                        self.twist.linear.x = 0.2
                        
                    self.twist.angular.z = -float(error_x) / 1000.0
                    ball_found = True
                    
                    cv2.circle(cv_image, (cx, int(M['m01']/M['m00'])), 10, (0,0,255), -1)

        if not ball_found:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0

        self.cmd_pub.publish(self.twist)
        cv2.imshow("Camara Normal", cv_image)
        cv2.waitKey(3)

if __name__ == '__main__':
    # Configurar lectura de modo
    parser = argparse.ArgumentParser(description="Seguidor con cámara normal")
    parser.add_argument('-m', '--mode', type=str, choices=['real', 'virtual'], default='real', 
                        help='Entorno: real (webcam usb) o virtual (gazebo)')
    
    args = parser.parse_args(rospy.myargv()[1:])
    
    if args.mode == 'real':
        topic = "/usb_cam/image_raw"
    else:
        topic = "/sim_camera/image_raw"

    try:
        NormalCameraFollower(topic)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    cv2.destroyAllWindows()