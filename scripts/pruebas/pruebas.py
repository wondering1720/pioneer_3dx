#!/usr/bin/env python3
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class VisorCamara:
    def __init__(self):
        # 1. Inicializar el nodo en ROS
        rospy.init_node('visor_pruebas', anonymous=True)
        self.bridge = CvBridge()
        
        # 2. Suscribirse directamente al tópico de usb_cam
        self.image_sub = rospy.Subscriber("/usb_cam/image_raw", Image, self.image_callback)
        
        # 3. Apagado seguro de ventanas
        rospy.on_shutdown(self.cerrar_ventanas)
        rospy.loginfo("Nodo de pruebas iniciado. Esperando video en: /usb_cam/image_raw")

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            
            # ---> AQUÍ ES DONDE AÑADIREMOS COSAS DESPUÉS <---
            
            cv2.imshow("Ventana de Pruebas", cv_image)
            cv2.waitKey(3) 
            
        except CvBridgeError as e:
            print(e)

    def cerrar_ventanas(self):
        cv2.destroyAllWindows()
        print("Cerrando el visor.")

if __name__ == '__main__':
    try:
        VisorCamara()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass