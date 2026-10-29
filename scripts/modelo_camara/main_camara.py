#!/usr/bin/env python3
import rospy
import cv2
import argparse
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

# Importamos nuestros propios módulos
from vision_module import VisionProcessor
from control_module import RobotController

class MainCameraNode:
    def __init__(self, topic_name):
        rospy.init_node('modular_camera_follower', anonymous=True)
        self.bridge = CvBridge()
        
        # Instanciamos los módulos
        self.vision = VisionProcessor()
        self.controller = RobotController(kp=0.009, tiempo_memoria=3.0)
        
        self.image_sub = rospy.Subscriber(topic_name, Image, self.image_callback)
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        
        rospy.on_shutdown(self.shutdown)
        rospy.loginfo(f"Nodo Modular iniciado. Escuchando: {topic_name}")

    def shutdown(self):
        stop_twist = self.controller.stop()
        self.cmd_pub.publish(stop_twist)
        cv2.destroyAllWindows()

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        # 1. Los OJOS analizan la imagen (Agregamos mascara_resultante)
        ball_found, error_x, area, total_area, frame_resultante, mascara_resultante = self.vision.process_image(cv_image)
        
        # 2. El CEREBRO calcula la velocidad
        twist_msg = self.controller.calculate_velocities(ball_found, error_x, area, total_area)
        
        # 3. Mandamos la orden a los motores
        self.cmd_pub.publish(twist_msg)
        
        # Imprimir en pantalla el estado actual del robot
        if not ball_found and self.controller.tiempo_ultimo_visto > 0:
            tiempo_perdido = rospy.get_time() - self.controller.tiempo_ultimo_visto
            
            if tiempo_perdido < self.controller.tiempo_memoria:
                cv2.putText(frame_resultante, "Buscando...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            elif tiempo_perdido < (self.controller.tiempo_memoria + self.controller.tiempo_regreso):
                cv2.putText(frame_resultante, "Regresando...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # ABRIR LAS DOS VENTANAS SIMULTÁNEAMENTE
        cv2.imshow("Camara Modular (Color)", frame_resultante)
        cv2.imshow("Camara Modular (Mascara)", mascara_resultante)
        cv2.waitKey(3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Seguidor modular")
    parser.add_argument('-m', '--mode', type=str, choices=['real', 'virtual'], default='real')
    args = parser.parse_args(rospy.myargv()[1:])
    
    topic = "/usb_cam/image_raw" if args.mode == 'real' else "/sim_camera/image_raw"

    try:
        MainCameraNode(topic)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass