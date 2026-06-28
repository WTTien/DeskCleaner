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

from desk_cleaner_description.utils import get_robot_description

def generate_launch_description():
    moveit_dir = get_package_share_directory("desk_cleaner_moveit_config")
    
    def load_yaml(file_path):
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except EnvironmentError:
            return None

    srdf_file = os.path.join(moveit_dir, "config/so101", "so101_arm.srdf")

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

    kinematics = load_yaml(os.path.join(moveit_dir, "config/so101", "kinematics.yaml"))
    joint_limits = load_yaml(os.path.join(moveit_dir, "config/so101", "joint_limits.yaml"))
    # MoveIt move_group node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        remappings=[('/joint_states', '/follower/joint_states')],
        output="screen",
        parameters=[
            {
                "robot_description": robot_description_content,
                "robot_description_semantic": robot_description_semantic_content,
                "robot_description_kinematics": kinematics,
                "robot_description_planning": joint_limits,
                "use_sim_time": use_sim_time,
            },
            load_yaml(os.path.join(moveit_dir, "config/so101", "ompl_planning.yaml")),
            load_yaml(os.path.join(moveit_dir, "config/so101", "moveit_controllers.yaml")),
            load_yaml(os.path.join(moveit_dir, "config/so101", "planning_pipelines.yaml")),
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
