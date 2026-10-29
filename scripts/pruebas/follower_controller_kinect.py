#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
import argparse
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

class KinectFollower:
    def __init__(self, topic_name):
        rospy.init_node('kinect_follower', anonymous=True)
        self.bridge = CvBridge()
        
        # Escucha el tópico dinámico (Kinect físico o simulado)
        self.image_sub = rospy.Subscriber(topic_name, Image, self.image_callback)
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.twist = Twist()
        
        self.kp = 0.003
        rospy.on_shutdown(self.stop_robot)
        rospy.loginfo(f"Iniciando seguidor Kinect. Escuchando video en: {topic_name}")

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
            # Seguimos el contorno más grande que veamos
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            
            # Solo ignorar basuritas o destellos de luz (área menor a 100 píxeles)
            if area > 100: 
                M = cv2.moments(c)
                if M['m00'] > 0:
                    cx = int(M['m10']/M['m00'])
                    error_x = cx - width/2
                    
                    # BUG CORREGIDO: Ahora el freno se activa al 20%, permitiendo que el robot avance
                    if area > (total_area * 0.20): 
                        self.twist.linear.x = 0.0
                        print("¡Pelota cerca! Frenando.")
                    else:
                        self.twist.linear.x = 0.2
                        print("Avanzando hacia el objetivo...")
                        
                    self.twist.angular.z = -float(error_x) * self.kp
                    ball_found = True
                    
                    cv2.circle(cv_image, (cx, int(M['m01']/M['m00'])), 10, (0,0,255), -1)

        if not ball_found:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.0

        self.cmd_pub.publish(self.twist)
        cv2.imshow("Camara Kinect", cv_image)
        cv2.waitKey(3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seguidor con Kinect")
    parser.add_argument('-m', '--mode', type=str, choices=['real', 'virtual'], default='real', 
                        help='Entorno: real (kinect físico) o virtual (gazebo)')
    
    args = parser.parse_args(rospy.myargv()[1:])
    
    if args.mode == 'real':
        # Tópico oficial cuando conectas un Kinect de Xbox por USB (paquete freenect)
        topic = "/camera/rgb/image_raw"
    else:
        # Tópico de tu Xacro en Gazebo
        topic = "/kinect/image_raw"

    try:
        KinectFollower(topic)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    cv2.destroyAllWindows()