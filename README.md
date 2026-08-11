# 🤖 Pioneer 3-DX - Grupo MOVIS

Repositorio oficial para la configuración, simulación y control del robot móvil **Pioneer 3-DX**. Este proyecto implementa **ROS 1 Noetic** y contenedores **Docker** para garantizar la portabilidad entre diferentes entornos (WSL2, Linux nativo).

## Características
- 🐳 **Entorno Dockerizado**: Configuración reproducible con `docker-compose` para evitar conflictos de dependencias.
- 🚀 **ROS Noetic**: Integración completa con el ecosistema de ROS 1 (Noetic Ninjemys) sobre Ubuntu 20.04.
- 🎮 **Teleoperación**: Soporte para control mediante joystick (Xbox/GameSir) usando `teleop_twist_joy`.
- 🧪 **Simulación**: Preparado para integración con Gazebo y RViz (vía WSLg en Windows).
- 🤖 **Drivers P2OS**: Implementación de los paquetes `p2os_driver` para comunicación serie/USB con el robot real.

## Requisitos Previos
Para ejecutar este proyecto necesitas:
- **Sistema Operativo**: Windows 10/11 con **WSL2** o Ubuntu 20.04 nativo.
- **Docker**: Docker Desktop instalado y configurado para usar el backend de WSL2.
- **GPU**: (Opcional) Drivers actualizados para aceleración gráfica en WSLg (RViz/Gazebo).

## Instalación y Configuración

```bash
cd ~/ros1_ws/src
git clone https://github.com/TU_USUARIO/pioneer_3dx.git
docker compose up -d --build #sobre la carpeta src
docker exec -it robot_ros1_pioneer bash

#dentro del contenedor
source /opt/ros/noetic/setup.bash
colcon build --symlink-install # en la carpeta ros1_ws
source install/setup.bash
```
