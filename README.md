# Desk Cleaner Robot

A ROS2 Humble workspace for a robotic arm that detects objects on a desk and cleans them into a bin. Designed to work without physical hardware first (mock arm driver) and be extended with a real arm later.

## Architecture

```
Camera/Photo ──> Perception (YOLOv8) ──> Planner ──> Arm Driver ──> Robot Arm
                 publishes detections     calls          pick/place    (mock or real)
                 with positions           PickPlace      service
                                          service
```

### Packages

| Package | Language | Purpose |
|---------|----------|---------|
| `desk_cleaner_interfaces` | CMake | Custom `.msg` and `.srv` definitions |
| `desk_cleaner_perception` | Python | YOLOv8 object detection node |
| `desk_cleaner_arm_driver` | C++ | Abstract arm interface + mock driver |
| `desk_cleaner_planning` | Python | Task planner with pluggable strategies |
| `desk_cleaner_bringup` | Python | Launch files and YAML configs |

### Topics and Services

| Name | Type | Description |
|------|------|-------------|
| `/desk_cleaner/detections` | `DetectedObjects` | Detected objects with positions |
| `/desk_cleaner/pick_place` | `PickPlace` (srv) | Request a pick-and-place operation |
| `/desk_cleaner/status` | `std_msgs/String` | Planner status updates |
| `/desk_cleaner/arm_markers` | `MarkerArray` | RViz visualization of arm actions |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera input (when using topic mode) |

## Prerequisites

- **ROS2 Humble** on Ubuntu 22.04
- Python 3.10+
- C++17 compiler

## Install Dependencies

### Humble (primary target)

```bash
# Core
sudo apt install ros-humble-cv-bridge ros-humble-vision-msgs

# Simulation (Gazebo Classic + RViz)
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros \
    ros-humble-rviz2 ros-humble-robot-state-publisher ros-humble-xacro

# MoveIt2
sudo apt install ros-humble-moveit ros-humble-moveit-ros-planning-interface

# UR5e + Robotiq 2F-85
sudo apt install ros-humble-ur-description ros-humble-ur-moveit-config \
    ros-humble-ur-robot-driver ros-humble-ur-simulation-gazebo \
    ros-humble-robotiq-description ros-humble-robotiq-controllers \
    ros-humble-controller-manager

# Python packages
pip install ultralytics opencv-python numpy
```

## Build

```bash
cd desk_cleaner_ws

# Source ROS2
source /opt/ros/humble/setup.bash

# Build all packages
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

## Usage

### Quick Test with a Desk Photo

Take a photo of your desk with your phone, transfer it to your computer, then:

```bash
ros2 launch desk_cleaner_bringup desk_cleaner.launch.py image_file:=/path/to/desk_photo.jpg
```

The detector will process the image, publish detections, and the planner will issue pick-place commands to the mock arm driver (which logs everything to the console).

### Live Camera Mode

With a USB webcam publishing to `/camera/image_raw`:

```bash
ros2 launch desk_cleaner_bringup desk_cleaner.launch.py
```

### Visualize in RViz

Launch RViz with pre-configured displays (arm markers, camera feed, TF, robot model):

```bash
ros2 launch desk_cleaner_bringup rviz.launch.py
```

### Simulation (Gazebo + RViz + Desk Cleaner)

Launch the full simulation environment with one command:

```bash
# Minimal: Gazebo desk world + RViz + desk cleaner nodes (mock arm)
ros2 launch desk_cleaner_bringup desk_cleaner_sim.launch.py

# With a robot URDF spawned on the desk
ros2 launch desk_cleaner_bringup desk_cleaner_sim.launch.py \
    robot_urdf:=/path/to/robot.urdf.xacro

# Using MoveIt to control the spawned robot
ros2 launch desk_cleaner_bringup desk_cleaner_sim.launch.py \
    robot_urdf:=/path/to/robot.urdf.xacro \
    driver_type:=moveit

# Gazebo desk world only (no desk cleaner nodes)
ros2 launch desk_cleaner_bringup gazebo_desk.launch.py
```

The Gazebo world includes:
- A 80x60cm desk at standard height (75cm)
- A bin/tray next to the desk (where objects get placed)
- An overhead camera publishing to `/camera/image_raw` (feeds into the detector node)

### UR5e + Robotiq 2F-85 (Default Arm)

**RViz + MoveIt2 (no Gazebo):**

```bash
ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py

# With a desk photo
ros2 launch desk_cleaner_bringup ur5e_bringup.launch.py \
    image_file:=/path/to/desk_photo.jpg
```

This launches the UR5e with fake hardware, MoveIt2 for motion planning, RViz for visualization, and all desk cleaner nodes. The arm is mounted on a pedestal at desk height with the Robotiq 2F-85 gripper attached.

**Full Gazebo Classic simulation:**

```bash
ros2 launch desk_cleaner_bringup ur5e_gazebo.launch.py
```

This uses `ur_simulation_gazebo` (Gazebo Classic) to spawn the UR5e with full physics, MoveIt2, and all desk cleaner nodes.

### MoveIt2 Mode (Real or Simulated Arm)

Launch with MoveIt2 controlling the arm. Requires a `<robot>_moveit_config` package for your arm:

```bash
# Option A: let the launch file start MoveIt for you
ros2 launch desk_cleaner_bringup desk_cleaner_moveit.launch.py \
    robot_moveit_config:=panda_moveit_config \
    image_file:=/path/to/desk_photo.jpg

# Option B: launch MoveIt separately, then start desk cleaner
ros2 launch panda_moveit_config move_group.launch.py
ros2 launch desk_cleaner_bringup desk_cleaner_moveit.launch.py \
    image_file:=/path/to/desk_photo.jpg
```

The MoveIt driver automatically adds a desk collision object to the planning scene for safety. Tune the dimensions in `config/arm.yaml` under `moveit.desk_*` parameters.

## Configuration

All parameters live in `src/desk_cleaner_bringup/config/`:

- **`perception.yaml`** -- YOLO model, confidence threshold, pixel-to-world mapping
- **`arm.yaml`** -- driver type, home pose, bin pose, joint limits
- **`planner.yaml`** -- cleaning strategy, priority classes, confidence floor

## Integrating a Real Arm

The arm driver uses a pluggable interface. To add your own arm:

### Step 1: Implement the Interface

Create a new C++ class that inherits from `ArmDriverInterface`:

```cpp
// src/desk_cleaner_arm_driver/include/desk_cleaner_arm_driver/my_arm_driver.hpp

#include "desk_cleaner_arm_driver/arm_driver_interface.hpp"

class MyArmDriver : public desk_cleaner_arm_driver::ArmDriverInterface {
public:
  explicit MyArmDriver(rclcpp::Node::SharedPtr node);

  ArmResult moveTo(const geometry_msgs::msg::Pose& target) override;
  ArmResult pick(const geometry_msgs::msg::Pose& target) override;
  ArmResult place(const geometry_msgs::msg::Pose& target) override;
  ArmResult home() override;
  std::string driverName() const override { return "MyArmDriver"; }
};
```

### Step 2: Register in the Factory

Edit `src/desk_cleaner_arm_driver/src/arm_driver_node.cpp` and add your driver to `createDriver()`:

```cpp
if (type == "my_arm") {
  return std::make_unique<MyArmDriver>(node);
}
```

### Step 3: Configure

Set the driver type in `config/arm.yaml`:

```yaml
arm_driver_node:
  ros__parameters:
    driver_type: "my_arm"
```

### MoveIt Integration

For MoveIt-based arms, your driver's `moveTo()` would use `MoveGroupInterface` to plan and execute. Add `moveit_ros_planning_interface` as a dependency in `package.xml` and `CMakeLists.txt`.

## Adding a Depth Camera

When upgrading from phone photos to an RGB-D camera (RealSense, OAK-D):

1. Replace the pixel-to-world heuristic in `detector_node.py` with proper depth-based 3D projection
2. Subscribe to the depth topic alongside the color topic
3. Use `image_geometry.PinholeCameraModel` for accurate pixel-to-3D conversion
4. Update `perception.yaml` with camera intrinsics or subscribe to `camera_info`

## Cleaning Strategies

The planner supports multiple strategies via the `CleaningStrategy` base class:

- **`clear_all`** (default): Pick every object and drop it in the bin, with optional priority ordering
- **`sort_by_category`**: Route different object classes to different target locations

Add your own by subclassing `CleaningStrategy` in `cleaning_strategy.py` and registering it in `STRATEGY_REGISTRY`.
