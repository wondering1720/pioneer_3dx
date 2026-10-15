# 🤖 Pioneer 3-DX: Simulación y Visión Bioinspirada (ROS Noetic)

Este repositorio contiene la configuración y el código para simular y operar un robot móvil Pioneer 3-DX utilizando **ROS 1 Noetic**. El entorno está completamente dockerizado para garantizar su portabilidad y cuenta con integración de visión por computadora (OpenCV) para simulador (Kinect) y hardware real (Webcam).

## 📌 Características Principales
* **Entorno Reproducible:** Uso de Docker y `docker-compose` para aislar dependencias sin conflictos.
* **Modelo Personalizado (URDF/Xacro):** Modificación del chasis clásico del Pioneer 3-DX.
* **Visión por Computadora:** Nodos en Python con OpenCV para procesamiento de imágenes y seguimiento autónomo de objetivos (ej. seguimiento de color).
* **Soporte Multiplataforma e Híbrido:** Configurado para ejecutarse en Windows (vía WSL2) y Linux nativo. Soporta cámaras virtuales de Gazebo y webcams físicas de laptop simultáneamente.

---

## 🛠️ Requisitos Previos

El comportamiento del hardware físico varía drásticamente dependiendo de tu sistema operativo.

### Para usuarios de Windows (WSL2)
1. **Docker Desktop** con la integración WSL2 activada.
2. **usbipd-win**: Herramienta necesaria para redirigir dispositivos USB (Robot físico, Webcam, mandos) desde Windows hacia el subsistema Linux.
```powershell
   # Ejecutar en PowerShell como administrador para vincular un dispositivo
   usbipd list
   usbipd bind --busid BUSID --force
   usbipd attach --wsl --busid BUSID

```

3. **Servidor X11 (Opcional):** Si no usas las versiones más recientes de WSLg, requerirás un servidor X como VcXsrv para la renderización visual.

### Para usuarios de Linux (Ubuntu nativo)

1. **Docker Engine** y **Docker Compose**.
2. **NVIDIA Container Toolkit** (Si cuentas con GPU dedicada) para acelerar inferencias pesadas.

---

## 🚀 Instalación y Despliegue

1. **Clonar el repositorio:**
```bash
cd ~ 
git clone [https://github.com/wondering1720/pioneer_3dx.git](https://github.com/wondering1720/pioneer_3dx.git) ros1_ws
cd ~/ros1_ws

```


2. **Construir y levantar el contenedor:**
Este comando lee el `Dockerfile`, instala el núcleo de ROS Noetic, los drivers `p2os`, el paquete `usb_cam` y las dependencias de IA (OpenCV), todo tardara dependiendo de red.

```bash
cd ~/ros1_ws/src/pioneer_3dx
docker compose up -d --build

```


3. **Ingresar al entorno de trabajo:**

```bash
docker exec -it robot_ros1_pioneer bash

```



---

## 🎮 Uso del Sistema

Dentro de la terminal del contenedor, asegúrate de compilar el espacio de trabajo si agregaste nuevos paquetes:

```bash
source /opt/ros/noetic/setup.bash #carga ros, en dockerfile ya lo hace para cada terminal abierta
catkin_make # compila los paquetes
source devel/setup.bash # igual lo hace el dockerfile pero hazlo despues de catkin_make

```

### 1. Iniciar Gazebo y el Robot

Lanza el mundo vacío con el modelo personalizado del Pioneer (incluyendo la cámara):

```bash
roslaunch pioneer_3dx gazebo.launch # en ros es necesario roscore pero roslaunch ya lo llama

```
Mover el Robot Manualmente. Abre una **segunda terminal** en el contenedor y ejecuta el nodo de teleoperación por teclado:

```bash
rosrun teleop_twist_keyboard teleop_twist_keyboard.py

```

*(Usa las teclas `i, j, k, l, ,` para mover el robot).*


### 2. Entorno Real (Webcam de Laptop vía WSL2)

```bash
roscore

```

Para usar la cámara web de tu computadora sin saturar el ancho de banda de WSL2, lanza el nodo forzando la compresión de hardware (MJPEG) y bajando la resolución para evitar la pérdida de paquetes de video:

Este comando te dice las especificaciones de tu camara, la camara puede saturar el envio, dandote imagenes rotas, ayuda a saber las configuraciones para modificar el script siguiente


```bash
v4l2-ctl --list-formats-ext -d /dev/video0

# esta linea manda el video, usalo para usar la camara real, la camara tiene que ser pasada con usbipd
rosrun usb_cam usb_cam_node _video_device:=/dev/video0 _pixel_format:=mjpeg _image_width:=320 _image_height:=240 _framerate:=15

```

Para visualizar lo que captura la cámara sin activar los motores del robot, usa el script de pruebas parametrizado:

```bash
rosrun pioneer_3dx pruebas.py

```
Termina el scrip de prueba.py
Despues de saber los parametros necesarios puedes seguir
En otra terminal, ejecuta el controlador optimizado con filtros de área para la cámara física:

```bash
rosrun pioneer_3dx follower_controller_camara.py -m real

```

---

## 📂 Arquitectura de Archivos

* `urdf/pioneer_kinect.xacro`: Importa el modelo base y ensambla la cámara en la placa superior.
* `launch/gazebo.launch`: Orquesta el simulador, levanta el mundo vacío e inyecta el `robot_description`.
* `scripts/follower_controller_kinect.py`: Nodo de procesamiento para el simulador. Se suscribe a `/kinect/image_raw`.
* `scripts/follower_controller_camara.py`: Nodo de procesamiento para la cámara física. Se suscribe a `/usb_cam/image_raw` y filtra contornos masivos para ignorar errores de red en WSL2.
* `scripts/pruebas.py`: Visor parametrizado con `argparse` para depurar flujos de video limpio.

---

## ⚠️ Peculiaridades y Solución de Problemas (FAQ)

* **Pantalla verde o imagen distorsionada en WSL2:** Si la cámara web muestra bloques verdes sólidos o estática, el puente virtual de Windows está perdiendo paquetes por falta de ancho de banda. Soluciónalo forzando la compresión de hardware al encender la cámara con `_pixel_format:=mjpeg _image_width:=320 _image_height:=240 _framerate:=15`.
* **Entornos Virtuales de Python (`.env`):** **No se deben utilizar** dentro de este contenedor. Activar un entorno aísla a Python de las librerías globales, provocando errores de `No module named 'rospy'`.
* **Uso de Joysticks en Windows (WSL2):** Aunque `usbipd` logre pasar el control al contenedor, el kernel oficial de WSL2 carece de los módulos `joydev`. Para solucionarlo, usa Linux nativo o recompila el kernel de WSL.
* **Error de visualización en OpenCV:** Asegúrate de que el `Dockerfile` instale `opencv-python` y las dependencias gráficas (`libgl1`, `libglib2.0-0`), evitando la versión `headless`.

