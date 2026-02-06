import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    pkg_path = get_package_share_directory('dummy_spider')
    pkg_worlds = get_package_share_directory('my_gazebo_worlds')

    world_file = os.path.join(pkg_worlds, 'worlds', 'small_maze.sdf')
    xacro_file = os.path.join(pkg_path, 'urdf', 'spidermaze.xacro')

    robot_description = Command(['xacro ', xacro_file])

    # 1. Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # 2. Robot State Publisher - Start immediately so URDF is available
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}]
    )

    # 3. Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # 4. Static Transforms
    static_transform_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0', '--qx', '0', '--qy', '0', '--qz', '0', '--qw', '1', '--frame-id', 'odom', '--child-frame-id', 'base_footprint'],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # 5. Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'spider', '-x', '-4.0', '-y', '4.0', '-z', '0.2'],
        output='screen',
    )

    # 6. Controllers - USING YAML FILE DIRECTLY
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
        parameters=[os.path.join(pkg_path, 'config', 'ros2_controllers.yaml'), {'use_sim_time': use_sim_time}],
    )

    position_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['position_controller'],
        output='screen',
        parameters=[os.path.join(pkg_path, 'config', 'ros2_controllers.yaml'), {'use_sim_time': use_sim_time}],
    )

    # 7. SLAM Toolbox
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': PathJoinSubstitution([FindPackageShare('dummy_spider'), 'config', 'mapper_params_online_async.yaml']),
            'use_sim_time': use_sim_time,
        }.items()
    )

    # 8. Your custom nodes
    spider_body_node = Node(
        package='dummy_spider',
        executable='spider_controller',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    spider_brain_node = Node(
        package='dummy_spider',
        executable='maze_solver',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        use_sim_time_arg,
        
        # Group 1: Core infrastructure
        gz_sim,
        robot_state_publisher,
        bridge,
        static_transform_publisher,

        # Group 2: Robot spawning
        TimerAction(period=3.0, actions=[spawn_robot]),

        # Group 3: Controllers
        TimerAction(period=5.0, actions=[
            joint_state_broadcaster,
            position_controller
        ]),

        # Group 4: Intelligence
        TimerAction(period=8.0, actions=[
            slam_toolbox,
            spider_body_node,
            spider_brain_node
        ]),
    ])