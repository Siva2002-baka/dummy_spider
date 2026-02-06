import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

class MazeManager(Node):
    def __init__(self):
        super().__init__('maze_manager')
        
        # Subscriptions
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # Publisher to your SpiderController
        self.cmd_pub = self.create_publisher(String, '/spider/command', 10)
        
        # Logic Variables
        self.front_dist = 2.0
        self.left_dist = 2.0
        self.right_dist = 2.0
        self.is_turning = False
        
        # Timer for decision making (running at 5Hz to avoid flooding commands)
        self.timer = self.create_timer(0.2, self.decide_move)
        self.get_logger().info("Maze Manager Started - Waiting for LiDAR...")

    def scan_callback(self, msg):
        # We assume 360 samples. Adjust indices if your LiDAR differs.
        # Gazebo Sim LiDAR usually starts 0 at the back or front.
        # Assuming index 180 is DEAD FRONT.
        self.front_dist = min(msg.ranges[160:200])
        self.right_dist = min(msg.ranges[40:100])
        self.left_dist = min(msg.ranges[260:320])

    def send_cmd(self, cmd_str):
        msg = String()
        msg.data = cmd_str
        self.cmd_pub.publish(msg)

    def decide_move(self):
        # 1. Check for obstacle in front
        if self.front_dist < 0.6:  # Threshold in meters
            self.get_logger().warn("Wall Detected! Choosing turn...")
            
            # Logic: Wall Follower (Prioritize Right)
            if self.left_dist > 1.2:
                self.get_logger().info("Turning Left")
                self.send_cmd("TURN_-90") # Based on your code logic
            else:
                self.get_logger().info("Turning Right")
                self.send_cmd("TURN_90")
                
        else:
            # 2. If path clear, go forward
            self.send_cmd("FORWARD")

def main(args=None):
    rclpy.init(args=args)
    node = MazeManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()