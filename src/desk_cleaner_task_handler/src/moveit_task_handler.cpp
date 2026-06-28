#include "desk_cleaner_task_handler/moveit_task_handler.hpp"

#include <chrono>
#include <vector>

#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

using namespace std::chrono_literals;

namespace desk_cleaner_task_handler
{

MoveItTaskHandler::MoveItTaskHandler(const rclcpp::Node::SharedPtr & node)
: node_(node)
{
  RCLCPP_INFO(node_->get_logger(), "Initializing MoveItTaskHandler...");

  // Initialize MoveGroupInterface with hardcoded planning group
  move_group_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(
    node_, PLANNING_GROUP);

  // Configure planning parameters
  move_group_->setPlanningTime(PLANNING_TIME);
  move_group_->setMaxVelocityScalingFactor(MAX_VELOCITY_SCALING);
  move_group_->setMaxAccelerationScalingFactor(MAX_ACCELERATION_SCALING);
  move_group_->setNumPlanningAttempts(NUM_PLANNING_ATTEMPTS);

  // Initialize planning scene for collision checking
  planning_scene_ = std::make_shared<moveit::planning_interface::PlanningSceneInterface>();

  RCLCPP_INFO(node_->get_logger(),
    "MoveItTaskHandler initialized successfully!");
  RCLCPP_INFO(node_->get_logger(),
    "  - Planning Group: %s", PLANNING_GROUP);
  RCLCPP_INFO(node_->get_logger(),
    "  - Planning Time: %.1f seconds", PLANNING_TIME);
  RCLCPP_INFO(node_->get_logger(),
    "  - Max Velocity Scaling: %.1f", MAX_VELOCITY_SCALING);
  RCLCPP_INFO(node_->get_logger(),
    "  - Max Acceleration Scaling: %.1f", MAX_ACCELERATION_SCALING);
  RCLCPP_INFO(node_->get_logger(),
    "  - Reference Frame: %s", move_group_->getPlanningFrame().c_str());
  RCLCPP_INFO(node_->get_logger(),
    "  - End-Effector Link: %s", move_group_->getEndEffectorLink().c_str());
}

bool MoveItTaskHandler::moveToTarget(
  double x, double y, double z,
  double qx, double qy, double qz, double qw)
{
  geometry_msgs::msg::Pose target_pose;
  target_pose.position.x = x;
  target_pose.position.y = y;
  target_pose.position.z = z;
  target_pose.orientation.x = qx;
  target_pose.orientation.y = qy;
  target_pose.orientation.z = qz;
  target_pose.orientation.w = qw;

  return moveToTarget(target_pose);
}

bool MoveItTaskHandler::moveToTarget(const geometry_msgs::msg::Pose & target_pose)
{
  RCLCPP_INFO(node_->get_logger(),
    "Planning to target: [%.3f, %.3f, %.3f]",
    target_pose.position.x,
    target_pose.position.y,
    target_pose.position.z);

  return planAndExecute(target_pose);
}

geometry_msgs::msg::Pose MoveItTaskHandler::getCurrentPose()
{
  return move_group_->getCurrentPose().pose;
}

bool MoveItTaskHandler::planAndExecute(const geometry_msgs::msg::Pose & target)
{
  // Step 1: Set the target pose
   
  // ur5e
  // move_group_->setPoseTarget(target);
  // so101
  move_group_->setApproximateJointValueTarget(target);

  // Step 2: Plan the trajectory
  RCLCPP_INFO(node_->get_logger(), "Planning trajectory...");
  moveit::planning_interface::MoveGroupInterface::Plan plan;
  auto error = move_group_->plan(plan);

  if (error != moveit::core::MoveItErrorCode::SUCCESS) {
    RCLCPP_ERROR(node_->get_logger(),
      "Planning failed with error code: %d", error.val);
    return false;
  }

  RCLCPP_INFO(node_->get_logger(), "Planning successful!");
  logTrajectoryInfo(plan.trajectory_);

  // Step 3: Execute the trajectory
  RCLCPP_INFO(node_->get_logger(), "Executing trajectory...");
  error = move_group_->execute(plan);

  if (error != moveit::core::MoveItErrorCode::SUCCESS) {
    RCLCPP_ERROR(node_->get_logger(),
      "Execution failed with error code: %d", error.val);
    return false;
  }

  RCLCPP_INFO(node_->get_logger(), "Execution completed successfully!");
  return true;
}

void MoveItTaskHandler::logTrajectoryInfo(const moveit_msgs::msg::RobotTrajectory & trajectory)
{
  if (trajectory.joint_trajectory.points.empty()) {
    RCLCPP_WARN(node_->get_logger(), "Trajectory is empty!");
    return;
  }

  size_t num_points = trajectory.joint_trajectory.points.size();
  RCLCPP_INFO(node_->get_logger(),
    "Trajectory Info: %zu points", num_points);

  if (num_points > 0) {
    double duration = trajectory.joint_trajectory.points.back().time_from_start.sec +
                      trajectory.joint_trajectory.points.back().time_from_start.nanosec / 1e9;
    RCLCPP_INFO(node_->get_logger(),
      "  - Execution time: %.2f seconds", duration);
  }
}

}  // namespace desk_cleaner_task_handler
