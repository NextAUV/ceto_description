import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable


def generate_launch_description():

    pkg_ceto_description = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths --------------------------------------------------------------------
    sdf_file_path = os.path.join(pkg_ceto_description, 'description', 'sdf', 'model.sdf')
    urdf_file_path = os.path.join(pkg_ceto_description, 'description', 'urdf', 'bluerov2.urdf')
    rviz_config_path = os.path.join(pkg_ceto_description, 'config', 'default.rviz')
    
    # Add your world file
    world_file_path = os.path.join(pkg_ceto_description, 'models', 'sauvc_worlds', 'sauvc25.world')



    set_gz_resource_path = SetEnvironmentVariable(
        name='GAZEBO_RESOURCE_PATH',
        value=pkg_ceto_description
    )

    # Robot State Publisher -----------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': Command([
                FindExecutable(name='xacro'),' ',
                urdf_file_path
            ])}
        ]
    )

    # Joint State Publisher -----------------------------------------------------
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    # Gazebo Simulation ---------------------------------------------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        # Load world + pass SDF spawn file
        launch_arguments={
            'gz_args': f'-r -v 4 {world_file_path}'
        }.items(),
    )

    # RViz ----------------------------------------------------------------------
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        set_gz_resource_path,
        robot_state_publisher,
        joint_state_publisher,
        gazebo,
        rviz2
    ])
