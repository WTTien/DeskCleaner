"""
Launch the UR5e desk cleaner in Gazebo Classic with MoveIt2, RViz, and all nodes.

Targets ROS2 Humble with Gazebo Classic (ur_simulation_gazebo).

Usage:
  ros2 launch desk_cleaner_bringup ur5e_gazebo.launch.py
  ros2 launch desk_cleaner_bringup ur5e_gazebo.launch.py image_file:=/path/to/desk.jpg

Prerequisites:
  sudo apt install ros-humble-ur-description ros-humble-ur-moveit-config \
      ros-humble-ur-simulation-gazebo ros-humble-robotiq-description \
      ros-humble-robotiq-controllers
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch.substitutions import Command,FindExecutable, PathJoinSubstitution




def generate_launch_description():
    bringup_dir = get_package_share_directory('desk_cleaner_bringup')
    # config_dir = os.path.join(bringup_dir, 'config')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    # urdf_file = os.path.join(bringup_dir, 'urdf', 'ur5e_desk_cleaner.urdf.xacro')

    # robot_description_content = ParameterValue(
    #     Command([
    #         PathJoinSubstitution([FindExecutable(name="xacro")]),
    #         " ",
    #         urdf_file,
    #         " name:=ur5e_desk_cleaner ur_type:=ur5e",
    #         " sim_gazebo:=true",
    #     ]),
    #     value_type=str,
    # )
    # robot_state_publisher_node = Node(
    #     package="robot_state_publisher",
    #     executable="robot_state_publisher",
    #     output="screen",
    #     parameters=[{
    #         "robot_description": robot_description_content,
    #     }],
    # )


    # -- Arguments --

    image_file_arg = DeclareLaunchArgument(
        'image_file', default_value='',
        description='Path to a desk photo for single-image mode',
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Launch RViz alongside Gazebo',
    )

    gui_arg = DeclareLaunchArgument('gui', default_value='true')
    spawn_x_arg = DeclareLaunchArgument('spawn_x', default_value='0.0')
    spawn_y_arg = DeclareLaunchArgument('spawn_y', default_value='0.0')
    spawn_z_arg = DeclareLaunchArgument('spawn_z', default_value='0.0')

    # -- Bringup Launch --
    ur5e_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('desk_cleaner_bringup'),
                'launch',
                'ur5e_bringup.launch.py'
            )
        ),
        launch_arguments={
            'use_rviz': LaunchConfiguration('use_rviz'),
            'image_file': LaunchConfiguration('image_file'),
            'gazebo_run': 'true',
        }.items(),
    )

    # -- Gazebo Classic simulation with desk world --

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(bringup_dir, 'worlds', 'desk.world'),
        }.items(),
    )

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('gui')),
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_robot',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'desk_cleaner_robot',
            '-x', LaunchConfiguration('spawn_x'),
            '-y', LaunchConfiguration('spawn_y'),
            '-z', LaunchConfiguration('spawn_z'),
        ],
        # arguments=[
        #     '-entity', 'desk_cleaner_robot',
        #     '-x', LaunchConfiguration('spawn_x'),
        #     '-y', LaunchConfiguration('spawn_y'),
        #     '-z', LaunchConfiguration('spawn_z'),
        # ],
        

    )

    # -- MoveIt2 with custom configuration (handling controllers and move_group) --
    # moveit_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(get_package_share_directory('desk_cleaner_moveit_config'), 'launch', 'move_group.launch.py')
    #     ),
    #     launch_arguments={'launch_rviz': 'false'}.items(),
    # )

    # -- RViz with desk cleaner config --

    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     output='screen',
    #     arguments=['-d', os.path.join(bringup_dir, 'rviz', 'desk_cleaner.rviz')],
    #     condition=IfCondition(LaunchConfiguration('use_rviz')),
    # )

    # -- Desk cleaner nodes --

    # arm_driver_node = Node(
    #     package='desk_cleaner_arm_driver',
    #     executable='arm_driver_node',
    #     name='arm_driver_node',
    #     output='screen',
    #     parameters=[
    #         os.path.join(config_dir, 'ur5e_arm.yaml'),
    #     ],
    # )

    # detector_node = Node(
    #     package='desk_cleaner_perception',
    #     executable='detector_node',
    #     name='detector_node',
    #     output='screen',
    #     parameters=[
    #         os.path.join(config_dir, 'perception.yaml'),
    #         {'image_file': LaunchConfiguration('image_file')},
    #     ],
    # )

    # planner_node = Node(
    #     package='desk_cleaner_planning',
    #     executable='planner_node',
    #     name='planner_node',
    #     output='screen',
    #     parameters=[
    #         os.path.join(config_dir, 'planner.yaml'),
    #     ],
    # )

    return LaunchDescription([
        image_file_arg,
        use_rviz_arg,
        gui_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        # gazebo_server,
        # gazebo_client,
        # robot_state_publisher_node,
        ur5e_bringup_launch,
        spawn_robot,
        # moveit_launch,
        # rviz_node,
        # planner_node,
    ])
