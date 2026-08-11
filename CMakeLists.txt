cmake_minimum_required(VERSION 3.0.2)
project(pioneer_3dx) # Debe coincidir con el nombre del paquete

find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)   