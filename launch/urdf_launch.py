#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_ceto_description = get_package_share_directory('ceto_description')

    # paths
    urdf_xacro = os.path.join(pkg_ceto_description, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(pkg_ceto_description, 'rviz', 'default.rviz')

    # produce robot_description by running xacro on your xacro file
    robot_description = ParameterValue(
        Command(['xacro', ' ', urdf_xacro]),
        value_type=str
    )

    # If you want rviz to use simulated time (e.g. if using /clock), set use_sim_time=True
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')


    # Start rviz2 to visualize the robot model and TF
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # joint_state_publisher: publishes joint states (non-simulated or from other sources)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # robot_state_publisher: publishes TF based on robot_description + joint states
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
        output='screen'
    )



    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (GZ) clock'),
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node
    ])