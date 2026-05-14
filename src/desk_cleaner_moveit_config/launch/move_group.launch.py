"""
Launch MoveIt2 move_group for UR5e + Robotiq 2F-85 desk cleaner.

This launch file:
  1. Loads the robot description (URDF + custom SRDF with gripper)
  2. Starts MoveIt move_group node
  3. Loads planning and execution configurations
  4. Optionally launches RViz for visualization

Usage:
  ros2 launch desk_cleaner_moveit_config move_group.launch.py
  ros2 launch desk_cleaner_moveit_config move_group.launch.py launch_moveit_rviz:=false
"""

import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue

from desk_cleaner_bringup.utils import get_robot_description

def generate_launch_description():
    moveit_dir = get_package_share_directory("desk_cleaner_moveit_config")
    
    def load_yaml(file_path):
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except EnvironmentError:
            return None

    srdf_file = os.path.join(moveit_dir, "config", "desk_cleaner.srdf.xacro")

    # Arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use simulation (Gazebo) clock if true",
    )
    use_sim_time = LaunchConfiguration("use_sim_time")

    launch_moveit_rviz_arg = DeclareLaunchArgument(
        "launch_moveit_rviz",
        default_value="true",
        description="Launch RViz for visualization",
    )

    debug_arg = DeclareLaunchArgument(
        "debug",
        default_value="false",
        description="Enable debug logging",
    )

    # Robot description (URDF)
    robot_description_content = get_robot_description()

    # Semantic robot description (SRDF)
    robot_description_semantic_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            srdf_file,
        ]),
        value_type=str,
    )

    kinematics = load_yaml(os.path.join(moveit_dir, "config", "kinematics.yaml"))
    joint_limits = load_yaml(os.path.join(moveit_dir, "config", "joint_limits.yaml"))
    # MoveIt move_group node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description_content,
                "robot_description_semantic": robot_description_semantic_content,
                "robot_description_kinematics": kinematics,
                "robot_description_planning": joint_limits,
                "use_sim_time": use_sim_time,
            },
            load_yaml(os.path.join(moveit_dir, "config", "ompl_planning.yaml")),
            load_yaml(os.path.join(moveit_dir, "config", "trajectory_execution.yaml")),
            load_yaml(os.path.join(moveit_dir, "config", "moveit_cpp.yaml")),
            load_yaml(os.path.join(moveit_dir, "config", "controllers.yaml")),
            load_yaml(os.path.join(moveit_dir, "config", "planning_pipelines.yaml")),
        ],
    )

    # MoveIt RViz node
    rviz_config_file = os.path.join(
        get_package_share_directory("desk_cleaner_bringup"),
        "rviz",
        "desk_cleaner.rviz",
    )

    moveit_rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        parameters=[
            {
                "robot_description": robot_description_content,
                "robot_description_semantic": robot_description_semantic_content,
                "robot_description_kinematics": kinematics,
                "use_sim_time": use_sim_time,
            },
        ],
        condition=IfCondition(LaunchConfiguration("launch_moveit_rviz")),
    )

    return LaunchDescription([
        use_sim_time_arg,
        launch_moveit_rviz_arg,
        debug_arg,
        move_group_node,
        moveit_rviz_node,
    ])
