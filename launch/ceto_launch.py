import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.substitutions import FindExecutable

def generate_launch_description():

    pkg_ceto_description = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths
    sdf_file_path = os.path.join(pkg_ceto_description, 'description', 'sdf', 'model.sdf')
    urdf_file_path = os.path.join(pkg_ceto_description, 'description', 'urdf', 'bluerov2.urdf')
    rviz_config_path = os.path.join(pkg_ceto_description, 'config', 'default.rviz')

    # GZ_SIM_RESOURCE_PATH must point to the directory that *contains* all model folders
    # Example: /install/share (NOT /install/share/ceto_description)
    install_share_path = os.path.dirname(pkg_ceto_description)

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=install_share_path
    )

    # Robot Description (URDF) — for RViz visualization
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': Command([FindExecutable(name='xacro'),' ',urdf_file_path])}
        ]
    )

    # Optional: only needed if your URDF has moving joints
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}]
    )

    # Gazebo Sim – load SDF world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -v 4 {sdf_file_path}'
        }.items(),
    )

    # RViz2
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
