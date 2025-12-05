cmake_minimum_required(VERSION 3.8)
project(ceto_description)

find_package(
  ament_cmake REQUIRED
  ament_cmake_python REQUIRED
  rclcpp REQUIRED
  rclpy REQUIRED
	ros_gz_sim REQUIRED
)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  models
  config
  description
  DESTINATION share/${PROJECT_NAME}
)

# ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/env-hooks/${PROJECT_NAME}.dsv.in")

ament_package()
