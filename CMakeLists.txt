cmake_minimum_required(VERSION 3.8)
project(ceto_description)

find_package(
  ament_cmake REQUIRED
  ament_cmake_python REQUIRED
  rclcpp REQUIRED
  rclpy REQUIRED
	ros_ign_gazebo REQUIRED
)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  models
  worlds
  config
  urdf
  rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
