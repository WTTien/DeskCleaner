cmake_minimum_required(VERSION 3.8)
project(desk_cleaner_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(xacro REQUIRED)
find_package(urdf REQUIRED)

install(
  DIRECTORY so_101 ur5e
  DESTINATION share/${PROJECT_NAME}
)

# Install the Python package so it can be imported by launch files and other
# Python code (exports the desk_cleaner_description module under site-packages).
ament_python_install_package(${PROJECT_NAME})

ament_package()
