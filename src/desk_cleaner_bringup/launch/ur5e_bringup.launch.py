"""
Launch the UR5e + Robotiq 2F-85 desk cleaner system with MoveIt2 and RViz.

Targets ROS2 Humble.

This brings up:
  1. Robot state publisher (custom URDF with pedestal + UR5e + Robotiq 2F-85)
  2. ros2_control with mock/fake hardware
  3. MoveIt2 move_group (from ur_moveit_config)
  4. RViz with desk cleaner config
  5. All desk cleaner nodes (perception, arm driver, planner)

Usage:
  ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py
  ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py image_file:=/path/to/desk.jpg
  ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py use_view_robot_rviz:=false

Prerequisites:
  sudo apt install ros-humble-ur-description ros-humble-ur-moveit-config \
      ros-humble-robotiq-description ros-humble-robotiq-controllers \
      ros-humble-ur-robot-driver ros-humble-controller-manager
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from desk_cleaner_bringup.utils import get_robot_description

def generate_launch_description():
    bringup_dir = get_package_share_directory('desk_cleaner_bringup')
    config_dir = os.path.join(bringup_dir, 'config')
    
    # -- Arguments --

    image_file_arg = DeclareLaunchArgument(
        'image_file', default_value='',
        description='Path to a desk photo for single-image mode',
    )

    use_view_robot_rviz_arg = DeclareLaunchArgument(
        'use_view_robot_rviz', default_value='true',
        description='Launch View Robot RViz',
    )

    gazebo_run_arg = DeclareLaunchArgument(
        'gazebo_run', default_value='false',
        description='Are we running Gazebo simulation?',
    )
    gazebo_run = LaunchConfiguration('gazebo_run')

    robot_description_content = get_robot_description(gazebo_run)

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
        }],
    )

    # # -- Joint state publishing (publishes all joint states for TF) --

    # joint_state_publisher = Node(
    #     package='joint_state_publisher',
    #     executable='joint_state_publisher',
    #     output='screen',
    #     parameters=[{
    #         'robot_description': robot_description_content,
    #     }],
    # )

    # May refer to Universal_Robots_ROS2_Driver ur_moveit_config package ur_moveit.launch.py
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('desk_cleaner_moveit_config'),
                'launch', 'move_group.launch.py'
            ])
        ),
        launch_arguments={
            'launch_moveit_rviz': 'true',
        }.items(),
    )

    # ROS2 Control Related Nodes
    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description_content},
            os.path.join(bringup_dir, "config", "ur5e_controllers.yaml")
        ],
        output="screen",
        condition=UnlessCondition(gazebo_run),  # ✅ SKIP when gazebo_run=true
    )


    # Spawner nodes to load and start the controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    robotiq_gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["robotiq_gripper_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    # -- View Robot RViz --

    view_robot_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(bringup_dir, 'rviz', 'desk_cleaner.rviz')],
        condition=IfCondition(LaunchConfiguration('use_view_robot_rviz')),
    )

    # -- Desk cleaner nodes --

    arm_driver_node = Node(
        package='desk_cleaner_arm_driver',
        executable='arm_driver_node',
        name='arm_driver_node',
        output='screen',
        parameters=[
            os.path.join(config_dir, 'ur5e_arm.yaml'),
        ],
    )

    detector_node = Node(
        package='desk_cleaner_perception',
        executable='detector_node',
        name='detector_node',
        output='screen',
        parameters=[
            os.path.join(config_dir, 'perception.yaml'),
            {'image_file': LaunchConfiguration('image_file')},
        ],
    )

    planner_node = Node(
        package='desk_cleaner_planning',
        executable='planner_node',
        name='planner_node',
        output='screen',
        parameters=[
            os.path.join(config_dir, 'planner.yaml'),
        ],
    )

    return LaunchDescription([
        image_file_arg,
        use_view_robot_rviz_arg,
        gazebo_run_arg,
        robot_state_publisher,
        # joint_state_publisher,
        moveit_launch,
        controller_manager_node,
        joint_state_broadcaster_spawner,
        joint_trajectory_controller_spawner,
        robotiq_gripper_controller_spawner,
        # view_robot_rviz_node,
        # arm_driver_node,
        # detector_node,
        # planner_node,
    ])
