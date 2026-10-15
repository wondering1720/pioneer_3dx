# Sistema operativo y ROS 1
# Basado en Ubuntu 20.04. Incluye ROS Noetic, Gazebo, RViz y rqt.
FROM osrf/ros:noetic-desktop-full

# Herramientas del sistema, red y utilidades USB
RUN apt-get update && apt-get install -y --no-install-recommends \
    usbutils \
    x11-apps \
    nano \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Paquetes oficiales para el robot Pioneer 3-DX (Driver p2os)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-p2os-driver \
    ros-noetic-p2os-urdf \
    ros-noetic-p2os-msgs \
    ros-noetic-p2os-launch \
    && rm -rf /var/lib/apt/lists/*

# Paquetes para visualización e interfaz de articulaciones (RViz / TF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-joint-state-publisher-gui \
    && rm -rf /var/lib/apt/lists/*

# Paquetes para el uso de joysticks (Controles Xbox/Gamesir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-noetic-usb-cam \    
    ros-noetic-joy \
    ros-noetic-teleop-twist-joy \
    ros-noetic-teleop-twist-keyboard \
    && rm -rf /var/lib/apt/lists/*
    
# Drivers de Kinect v1 (freenect) y procesamiento de nubes de puntos / imágenes
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreenect-bin \
    libfreenect-dev \
    ros-noetic-image-transport \
    ros-noetic-cv-bridge \
    && rm -rf /var/lib/apt/lists/*

# Dependencias gráficas para OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalación de librerías de Inteligencia Artificial / Visión (YOLO y PyTorch)
RUN pip3 install --no-cache-dir \
    ultralytics \
    opencv-python


# Configuraciones ligeras (Variables de entorno y Source)
RUN echo "source /opt/ros/noetic/setup.bash" >> /root/.bashrc
RUN echo "if [ -f /ros1_ws/devel/setup.bash ]; then source /ros1_ws/devel/setup.bash; fi" >> /root/.bashrc

# Directorio de trabajo
WORKDIR /ros1_ws

# Comando por defecto al iniciar (mantiene el contenedor vivo en modo interactivo)
CMD ["/bin/bash"]