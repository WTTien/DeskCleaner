cmake_minimum_required(VERSION 3.8)
project(desk_cleaner_task_handler)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(desk_cleaner_interfaces REQUIRED)

include_directories(include)

# Library for the MoveIt task handler
add_library(moveit_task_handler SHARED
  src/moveit_task_handler.cpp
)
ament_target_dependencies(moveit_task_handler
  rclcpp
  geometry_msgs
  tf2_geometry_msgs
  moveit_msgs
  moveit_ros_planning_interface
)
target_include_directories(moveit_task_handler PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# Executable node that exposes the handler as a service
add_executable(task_handler_node
  src/task_handler_node.cpp
)
target_link_libraries(task_handler_node moveit_task_handler)
ament_target_dependencies(task_handler_node
  rclcpp
  geometry_msgs
  moveit_msgs
  moveit_ros_planning_interface
  desk_cleaner_interfaces
)

install(TARGETS moveit_task_handler
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(TARGETS task_handler_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

ament_package()
