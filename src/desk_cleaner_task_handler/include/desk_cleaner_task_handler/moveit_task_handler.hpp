#ifndef DESK_CLEANER_TASK_HANDLER__MOVEIT_TASK_HANDLER_HPP_
#define DESK_CLEANER_TASK_HANDLER__MOVEIT_TASK_HANDLER_HPP_

#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>

namespace desk_cleaner_task_handler
{

/**
 * MoveItTaskHandler: A simplified interface for MoveIt2 task execution.
 * 
 * This class wraps MoveIt2's planning and execution capabilities.
 * It receives x-y-z coordinates and executes MoveIt2 trajectories with
 * no additional configuration needed beyond standard MoveIt2 setup.
 * 
 * Design: Uses composition instead of inheritance (receives a Node reference)
 * to avoid creating multiple nodes in the same executable.
 */
class MoveItTaskHandler
{
public:
  explicit MoveItTaskHandler(const rclcpp::Node::SharedPtr & node);

  /// Move the arm to a target pose (plan + execute)
  bool moveToTarget(
    double x, double y, double z,
    double qx = 0.0, double qy = 0.0, double qz = 0.0, double qw = 1.0);

  /// Move the arm to a geometry_msgs::msg::Pose target (plan + execute)
  bool moveToTarget(const geometry_msgs::msg::Pose & target_pose);

  /// Get the current end-effector pose
  geometry_msgs::msg::Pose getCurrentPose();

private:
  rclcpp::Node::SharedPtr node_;
  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_;
  std::shared_ptr<moveit::planning_interface::PlanningSceneInterface> planning_scene_;

  // Configuration constants (no parameter files needed)
  
  // so101
  static constexpr const char * PLANNING_GROUP = "manipulator";
  // ur5e
  // static constexpr const char * PLANNING_GROUP = "ur_manipulator";
  
  static constexpr double PLANNING_TIME = 5.0;
  static constexpr double MAX_VELOCITY_SCALING = 0.5;
  static constexpr double MAX_ACCELERATION_SCALING = 0.5;
  static constexpr int NUM_PLANNING_ATTEMPTS = 3;

  /// Plan and execute trajectory to target pose
  bool planAndExecute(const geometry_msgs::msg::Pose & target);

  /// Log trajectory information
  void logTrajectoryInfo(const moveit_msgs::msg::RobotTrajectory & trajectory);
};

}  // namespace desk_cleaner_task_handler

#endif  // DESK_CLEANER_TASK_HANDLER__MOVEIT_TASK_HANDLER_HPP_
