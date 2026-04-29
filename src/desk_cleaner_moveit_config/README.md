# Desk Cleaner MoveIt Configuration

Custom MoveIt2 configuration for the UR5e robotic arm with Robotiq 2F-85 gripper on a desk pedestal.

## Overview

This package provides:
- **SRDF (Semantic Robot Description Format)**: Defines planning groups, end effectors, and collision pairs
- **OMPL Planning Configuration**: Motion planning with various sampling-based algorithms
- **Controller Configurations**: Trajectory execution for arm and gripper
- **Launch Files**: Integration with ROS 2 MoveIt2

## Planning Groups

### `ur_manipulator`
- UR5e arm only (6 joints)
- Used for arm motion planning without gripper

### `robotiq_gripper`
- Robotiq 2F-85 gripper fingers (6 mimic joints)
- Left knuckle, right knuckle, and their dependent joints

### `ur_manipulator_with_gripper`
- Combined arm + gripper planning
- For simultaneous arm and gripper trajectory planning

## Named Poses

- **home**: Arm retracted, safe position
- **open**: Gripper fully open
- **closed**: Gripper fully closed

## Configuration Files

### `desk_cleaner.srdf.xacro`
Semantic description defining:
- Planning groups and end effectors
- Collision pairs (enabled/disabled)
- Named positions for each group
- Virtual base joint

### `ompl_planning.yaml`
Motion planning algorithms:
- RRTConnect (default for arm)
- RRT, EST, KPIECE, PRM, etc.
- Per-group planner configurations

### `controllers.yaml`
Controller definitions for:
- `ur_controllers`: UR5e joint trajectory execution
- `robotiq_gripper_controller`: Gripper joint trajectory execution

### `trajectory_execution.yaml`
Execution parameters and controller management

### `moveit_cpp.yaml`
MoveIt C++ library configuration

## Joint Names

### UR5e Arm Joints
- `shoulder_pan_joint`
- `shoulder_lift_joint`
- `elbow_joint`
- `wrist_1_joint`
- `wrist_2_joint`
- `wrist_3_joint`

### Robotiq Gripper Joints
- `robotiq_85_left_knuckle_joint` (primary, controllable)
- `robotiq_85_right_knuckle_joint` (primary, controllable)
- `robotiq_85_left_inner_knuckle_joint` (mimic of left knuckle)
- `robotiq_85_right_inner_knuckle_joint` (mimic of right knuckle)
- `robotiq_85_left_finger_tip_joint` (mimic of left knuckle)
- `robotiq_85_right_finger_tip_joint` (mimic of right knuckle)

## Building and Launching

### Build
```bash
cd ~/desk_cleaner_ws
colcon build --packages-select desk_cleaner_moveit_config
```

### Launch MoveIt
```bash
# From ur5e_bringup (which includes this config)
ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py

# Or launch MoveIt directly
ros2 launch desk_cleaner_moveit_config move_group.launch.py
```

### Launch without RViz
```bash
ros2 launch desk_cleaner_moveit_config move_group.launch.py launch_rviz:=false
```

## MoveIt Integration with Arm Driver

The arm driver (`desk_cleaner_arm_driver`) uses this configuration:

```yaml
moveit:
  planning_group: "ur_manipulator"  # Main planning group
  gripper_action: "/robotiq_gripper_controller/gripper_cmd"
  planning_time: 10.0
  max_velocity_scaling: 0.3
  max_acceleration_scaling: 0.3
```

### Supported Operations
- **moveTo()**: Move arm to target pose using RRTConnect planner
- **pick()**: Approach, open gripper, descend, grasp, retract
- **place()**: Approach, descend, release, retract
- **home()**: Move to safe home position

## Collision Management

The SRDF defines which link pairs should **not** be checked for collisions:
- Gripper internal links (mimic joints)
- Gripper fingers grasping each other
- Adapter to gripper connections
- Wrist to gripper mounting

This significantly improves planning performance.

## Gripper Control

Gripper positions (in radians):
- **Open**: 0.0 rad
- **Closed**: 0.8 rad (maximum grasp)

These are published to the `robotiq_gripper_controller` action server.

## Troubleshooting

### Joint not found errors
If you see "Joint 'X' not found in model":
1. Verify joint names match URDF
2. Check SRDF group definitions
3. Ensure URDF is properly compiled from xacro

### Planning failures
- Increase `planning_time` in arm configuration
- Check collision objects are not blocking path
- Verify planning group contains required joints

### Gripper not responding
- Check `gripper_action` topic name
- Verify `robotiq_gripper_controller` is active
- Ensure gripper mimic joints are in SRDF

## Dependencies

```bash
sudo apt install ros-humble-moveit ros-humble-moveit-resources-panda-description
```

## File Structure

```
desk_cleaner_moveit_config/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── desk_cleaner.srdf.xacro      # Semantic robot description
│   ├── ompl_planning.yaml            # Motion planning config
│   ├── controllers.yaml              # Controller definitions
│   ├── trajectory_execution.yaml     # Execution parameters
│   └── moveit_cpp.yaml               # MoveIt C++ config
├── launch/
│   └── move_group.launch.py          # Main launch file
└── README.md
```

## Author Notes

- Gripper uses mimic joints for finger coordination
- Only primary knuckle joints are controllable; others follow via URDF constraints
- Collision pairs optimized to balance safety and planning speed
- SRDF and URDF must match for MoveIt to work correctly
