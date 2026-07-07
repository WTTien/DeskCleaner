"""
Launch the so101 desk cleaner in Gazebo Classic with MoveIt2, RViz, and all nodes.

Targets ROS2 Humble with Gazebo Classic (ur_simulation_gazebo).

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
    so101_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('desk_cleaner_bringup'),
                'launch',
                'so101_bringup.launch.py'
            )
        ),
        launch_arguments={
            'use_rviz': LaunchConfiguration('use_rviz'),
            'image_file': LaunchConfiguration('image_file'),
            'gazebo_run': 'true',
            'use_sim_time': 'true',
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
            '-topic', '/follower/robot_description',
            '-entity', 'desk_cleaner_robot',
            '-robot_namespace', 'follower',
            '-x', LaunchConfiguration('spawn_x'),
            '-y', LaunchConfiguration('spawn_y'),
            '-z', LaunchConfiguration('spawn_z'),
        ],
    )

    return LaunchDescription([
        image_file_arg,
        use_rviz_arg,
        gui_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        # gazebo_server,
        # gazebo_client,
        so101_bringup_launch,
        spawn_robot
    ])
