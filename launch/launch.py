import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # --- 1. CONFIGURATION & PATHS ---
    pkg_ceto = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Simulation Paths
    world_path = os.path.join(pkg_ceto, 'worlds', 'sauvc25.world')
    model_dir = os.path.join(pkg_ceto, 'models')
    model_sdf_path = os.path.join(model_dir, 'bluerov2', 'model.sdf')
    bridge_config_path = os.path.join(pkg_ceto, 'config', 'bridge.yaml')

    # URDF/RViz Paths
    urdf_xacro = os.path.join(pkg_ceto, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(pkg_ceto, 'rviz', 'default.rviz')

    # Launch Configuration
    use_sim_time = LaunchConfiguration('use_sim_time')

    # --- 2. ENVIRONMENT VARIABLES (For Gazebo Meshes) ---
    existing_gz_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    existing_ign_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')
    
    # Prepend our model directory to the resource path
    new_gz_path = f"{model_dir}:{existing_gz_path}" if existing_gz_path else model_dir
    new_ign_path = f"{model_dir}:{existing_ign_path}" if existing_ign_path else model_dir

    set_gz_resource = SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=new_gz_path)
    set_ign_resource = SetEnvironmentVariable(name='IGN_GAZEBO_RESOURCE_PATH', value=new_ign_path)

    # --- 3. ROBOT DESCRIPTION (URDF) ---
    robot_description = ParameterValue(
        Command(['xacro ', urdf_xacro]),
        value_type=str
    )

    # --- 4. NODES ---

    # A. Gazebo Simulator
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f"-r -v 4 {world_path}"}.items(),
    )

    # B. Spawn Robot (Gazebo)
    spawn_bluerov2 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', model_sdf_path,
            '-name', 'bluerov2',
            '-x', '0.0', '-y', '0.0', '-z', '0.0',
            '-R', '0.0', '-P', '0.0', '-Y', '0.0'
        ],
        output='screen'
    )

    # C. ROS-Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': bridge_config_path,
            'qos_overrides./tf_static.publisher.reliability': 'reliable',
        }],
        output='screen'
    )

    # D. Robot State Publisher (Processes URDF -> TF)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )

    # E. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # F. TF GLUE (The Sync Fix)
    # Connects Gazebo's "bluerov2" frame to ROS's "base_link" frame
    tf_glue = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='gz_to_ros_tf_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'bluerov2', 'base_link'],
        output='screen'
    )

    # --- 5. RETURN LAUNCH DESCRIPTION ---
    return LaunchDescription([
        # Arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true', # Default to true for simulation
            description='Use simulation clock if true'
        ),
        
        # Environment
        set_gz_resource,
        set_ign_resource,

        # Nodes
        gazebo,
        spawn_bluerov2,
        bridge,
        robot_state_publisher,
        tf_glue,
        rviz_node
    ])