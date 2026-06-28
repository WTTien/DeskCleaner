import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from desk_cleaner_description.utils import get_robot_description

def generate_launch_description():
    bringup_dir = get_package_share_directory('desk_cleaner_bringup')
    config_dir = os.path.join(bringup_dir, 'config')
    
    # -- Arguments --

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true',
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

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
        namespace='follower',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time,
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
                'launch', 'move_group_so101.launch.py'
            ])
        ),
        launch_arguments={
            'launch_moveit_rviz': 'true',
            'use_sim_time': use_sim_time,
        }.items(),
    )

    # ROS2 Control Related Nodes
    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace="follower",
        parameters=[
            {"robot_description": robot_description_content},
            os.path.join(bringup_dir, "config", "so101_controllers.yaml"),
            {'use_sim_time': use_sim_time},
        ],
        output="screen",
        condition=UnlessCondition(gazebo_run),  # ✅ SKIP when gazebo_run=true
    )


    # Spawner nodes to load and start the controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace='follower',
        arguments=["joint_state_broadcaster"],
        parameters=[{'use_sim_time': use_sim_time}],
        output="screen",
    )

    arm_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace='follower',
        arguments=["arm_trajectory_controller"],
        parameters=[{'use_sim_time': use_sim_time}],
        output="screen",
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace='follower',
        arguments=["gripper_controller"],
        parameters=[{'use_sim_time': use_sim_time}],
        output="screen",
    )

    # -- View Robot RViz --

    view_robot_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(bringup_dir, 'rviz', 'desk_cleaner.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
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
            {'use_sim_time': use_sim_time},
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
            {'use_sim_time': use_sim_time},
        ],
    )

    planner_node = Node(
        package='desk_cleaner_planning',
        executable='planner_node',
        name='planner_node',
        output='screen',
        parameters=[
            os.path.join(config_dir, 'planner.yaml'),
            {'use_sim_time': use_sim_time},
        ],
    )

    def load_yaml(file_path):
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except EnvironmentError:
            return None
        
    moveit_dir = get_package_share_directory("desk_cleaner_moveit_config")
    srdf_file = os.path.join(moveit_dir, "config/so101", "so101_arm.srdf")
    robot_description_semantic_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            srdf_file,
        ]),
        value_type=str,
    )
    kinematics = load_yaml(os.path.join(moveit_dir, "config/so101", "kinematics.yaml"))

    task_handler_node = Node(
        package='desk_cleaner_task_handler',
        executable='task_handler_node',
        name='task_handler_node',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'robot_description_semantic': robot_description_semantic_content,
            'robot_description_kinematics': kinematics,
            'use_sim_time': use_sim_time,
        }],
        remappings=[
            ('/joint_states', '/follower/joint_states')
        ],  
    )

    return LaunchDescription([
        use_sim_time_arg,
        image_file_arg,
        use_view_robot_rviz_arg,
        gazebo_run_arg,
        robot_state_publisher,
        # joint_state_publisher,
        moveit_launch,
        controller_manager_node,
        joint_state_broadcaster_spawner,
        arm_trajectory_controller_spawner,
        gripper_controller_spawner,
        # view_robot_rviz_node,
        # arm_driver_node,
        # detector_node,
        # planner_node,
        task_handler_node,
    ])
