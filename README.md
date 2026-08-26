# 🤖 Pioneer 3-DX - Grupo MOVIS

Repositorio para la configuración, simulación y control del robot móvil **Pioneer 3-DX**. Este proyecto implementa **ROS 1 Noetic** y contenedores **Docker** sobre **WSL2** para garantizar la portabilidad y aceleración por hardware. Espero que el repositorio pueda facilitar el uso del pioneer a mas personas que trabajen con el, además espero poder hacer una versión para linux despues.

## Características
- 🐳 **Entorno Dockerizado**: Configuración reproducible con `docker-compose` para evitar conflictos de dependencias.
- 🚀 **ROS Noetic**: Integración completa con el ecosistema de ROS 1 (Noetic Ninjemys) sobre Ubuntu 20.04.
- ⚡ **Aceleración GPU**: Soporte para modelos de visión (YOLO/PyTorch/OpenCV) usando la GPU dedicada vía NVIDIA Container Toolkit.
- 📹 **Soporte Kinect v1**: Redirección USB mediante `usbipd-win` para la captura de color y profundidad.
- 🎮 **Teleoperación**: Soporte para control mediante joystick (Xbox/GameSir) y teclado.
- 🤖 **Drivers P2OS**: Implementación de los paquetes `p2os_driver` para comunicación serie/USB con el robot real.

## Requisitos Previos (Windows)
1. **Windows 10/11 con WSL2** (Ubuntu instalado).
2. **NVIDIA Driver** (Game Ready o Studio) actualizado en Windows.
3. **Docker Desktop** instalado y configurado con la opción *Use the WSL 2 based engine* activada en ajustes.
4. **NVIDIA Container Toolkit** configurado en WSL2 (para aceleración por GPU).
5. **usbipd-win** instalado en Windows (para conectar la Kinect u otros dispositivos USB).

---

## Instalación y Configuración Inicial

### 1. Clonar el repositorio
Abre tu terminal de **WSL2** y clona el proyecto dentro de tu carpeta personal de Linux:

```bash
cd ~
git clone [https://github.com/wondering1720/pioneer_3dx.git](https://github.com/wondering1720/pioneer_3dx.git) ros1_ws
cd ~/ros1_ws

## Construir e iniciar el contenedor
docker compose up -d --build
docker exec -it robot_ros1_pioneer bash

# dentro del contenedor - Compilar el espacio de trabajo
catkin_make
source devel/setup.bash

# Verificación del entorno
nvidia-smi # Probar CUDA
roslaunch freenect_launch freenect.launch # en caso de conectar Kinect
```
