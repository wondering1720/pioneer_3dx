# Sistema operativo y ROS 1
# Basado en Ubuntu 20.04. Incluye ROS Noetic, Gazebo, RViz y rqt.
FROM osrf/ros:noetic-desktop-full

# Herramientas del sistema, red y utilidades USB
RUN apt-get update && apt-get install -y --no-install-recommends \
    usbutils \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Paquetes oficiales para el robot Pioneer 3-DX (Driver p2os)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-p2os-driver \
    ros-noetic-p2os-urdf \
    ros-noetic-p2os-msgs \
    ros-noetic-p2os-launch \
    && rm -rf /var/lib/apt/lists/*

# Paquetes para el uso de joysticks (Controles Xbox/Gamesir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-joy \
    ros-noetic-teleop-twist-joy \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*   

# Configuraciones ligeras (Variables de entorno y Source)
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc

# Directorio de trabajo
WORKDIR /ros1_ws

# Comando por defecto al iniciar (mantiene el contenedor vivo en modo interactivo)
CMD ["/bin/bash"]