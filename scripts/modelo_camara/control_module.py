import rospy
from geometry_msgs.msg import Twist

class RobotController:
    # Redujimos el tiempo a 2.5 segundos
    def __init__(self, kp=0.009, tiempo_memoria=2.5):
        self.kp = kp
        self.tiempo_memoria = tiempo_memoria
        self.tiempo_regreso = tiempo_memoria # Mismo tiempo para deshacer el movimiento
        self.ultima_posicion_x = 0
        self.tiempo_ultimo_visto = 0.0
        self.twist = Twist()

    def calculate_velocities(self, ball_found, error_x, area, total_area):
        if ball_found:
            self.ultima_posicion_x = error_x
            self.tiempo_ultimo_visto = rospy.get_time()
            
            if area > (total_area * 0.06):
                self.twist.linear.x = 0.0
            else:
                self.twist.linear.x = 0.2
            
            self.twist.angular.z = -float(error_x) * self.kp
            
        else:
            if self.tiempo_ultimo_visto > 0:
                tiempo_perdido = rospy.get_time() - self.tiempo_ultimo_visto
                
                # FASE 1: Búsqueda (0 a 2.5 segundos)
                if tiempo_perdido < self.tiempo_memoria:
                    self.twist.linear.x = 0.0
                    if self.ultima_posicion_x < 0:
                        self.twist.angular.z = 0.4
                    else:
                        self.twist.angular.z = -0.4
                        
                # FASE 2: Regreso a la posición original (2.5 a 5.0 segundos)
                elif tiempo_perdido < (self.tiempo_memoria + self.tiempo_regreso):
                    self.twist.linear.x = 0.0
                    # Giramos en sentido INVERSO a la búsqueda
                    if self.ultima_posicion_x < 0:
                        self.twist.angular.z = -0.4 
                    else:
                        self.twist.angular.z = 0.4
                        
                # FASE 3: Se rindió
                else:
                    self.stop()
            else:
                self.stop()
        
        return self.twist

    def stop(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        return self.twist