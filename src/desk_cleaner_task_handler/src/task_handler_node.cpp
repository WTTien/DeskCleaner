#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>

#include "desk_cleaner_task_handler/moveit_task_handler.hpp"
#include "desk_cleaner_interfaces/srv/move_to_cartesian.hpp"

using MoveToCartesian = desk_cleaner_interfaces::srv::MoveToCartesian;

/**
 * TaskHandlerNode: Exposes MoveIt2 trajectory execution as a ROS2 service.
 * 
 * Service: /desk_cleaner/move_to_cartesian
 *   Request: target_pose (geometry_msgs::msg::Pose with x, y, z, qx, qy, qz, qw)
 *   Response: success (bool), message (string)
 */
class TaskHandlerNode : public rclcpp::Node
{
public:
  TaskHandlerNode()
  : rclcpp::Node("task_handler_node")
  {
    // Create the service
    move_to_cartesian_srv_ = this->create_service<MoveToCartesian>(
      "/desk_cleaner/move_to_cartesian",
      [this](
        const std::shared_ptr<MoveToCartesian::Request> request,
        std::shared_ptr<MoveToCartesian::Response> response)
      {
        this->handleMoveToCartesian(request, response);
      });


    RCLCPP_INFO(this->get_logger(),
      "Service ready: /desk_cleaner/move_to_cartesian");
  }

  void initialize()
  {
    // Initialize the MoveIt task handler with a reference to this node
    task_handler_ = std::make_shared<desk_cleaner_task_handler::MoveItTaskHandler>(
      this->shared_from_this());
    
    RCLCPP_INFO(this->get_logger(), "TaskHandlerNode initialized.");
  }

private:
  std::shared_ptr<desk_cleaner_task_handler::MoveItTaskHandler> task_handler_;
  rclcpp::Service<MoveToCartesian>::SharedPtr move_to_cartesian_srv_;

  void handleMoveToCartesian(
    const std::shared_ptr<MoveToCartesian::Request> request,
    std::shared_ptr<MoveToCartesian::Response> response)
  {
    RCLCPP_INFO(this->get_logger(),
      "Received MoveToCartesian request: [%.3f, %.3f, %.3f]",
      request->target_pose.position.x,
      request->target_pose.position.y,
      request->target_pose.position.z);

    // Extract pose components
    const auto & pos = request->target_pose.position;
    const auto & ori = request->target_pose.orientation;

    // Call plan and execute
    bool success = task_handler_->moveToTarget(
      pos.x, pos.y, pos.z,
      ori.x, ori.y, ori.z, ori.w);

    response->success = success;
    if (success) {
      response->message = "Successfully planned and executed trajectory";
    } else {
      response->message = "Failed to plan or execute trajectory";
    }

    RCLCPP_INFO(this->get_logger(),
      "Response: success=%s, message='%s'",
      response->success ? "true" : "false",
      response->message.c_str());
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<TaskHandlerNode>();
  node->initialize();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
