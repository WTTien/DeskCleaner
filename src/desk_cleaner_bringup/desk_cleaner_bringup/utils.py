import os

from ament_index_python.packages import get_package_share_directory
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution,
    PythonExpression,
)

from launch_ros.descriptions import ParameterValue


bringup_dir = get_package_share_directory('desk_cleaner_bringup')
urdf_file = os.path.join(bringup_dir, 'urdf', 'ur5e_desk_cleaner.urdf.xacro')

def get_robot_description(sim_gazebo=None):
    # return ParameterValue(
    #     Command([
    #         PathJoinSubstitution([FindExecutable(name='xacro')]),
    #         " ",
    #         urdf_file,
    #         " ",
    #         "name:=ur5e_desk_cleaner",
    #         " ",
    #         "ur_type:=ur5e",
    #         " ",
    #         "sim_gazebo:=",
    #         str(sim_gazebo),
    #     ]),
    #     value_type=str,
    # )
    xacro_cmd = [
        PathJoinSubstitution([FindExecutable(name='xacro')]),
        " ",
        urdf_file,
        " ",
        "name:=ur5e_desk_cleaner",
        " ",
        "ur_type:=ur5e",
    ]

    # Only add sim_gazebo if provided
    if sim_gazebo is not None:
        xacro_cmd += [
            " ",
            "sim_gazebo:=",
            sim_gazebo,
        ]
        xacro_cmd += [
            " ",
            "use_fake_hardware:=",
            PythonExpression(["'false' if '", sim_gazebo, "' == 'true' else 'true'"])
        ]

    return ParameterValue(
        Command(xacro_cmd),
        value_type=str,
    )