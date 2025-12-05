import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ceto_description = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # world and model paths
    world_path = os.path.join(pkg_ceto_description, 'worlds', 'sauvc25.world')
    model_sdf_path = os.path.join(pkg_ceto_description, 'models', 'bluerov', 'model.sdf')

    # Ensure GZ_SIM_RESOURCE_PATH contains the package models directory (so meshes/textures resolve)
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        gz_resource_path = os.environ['GZ_SIM_RESOURCE_PATH']
        new_gz_resource_path = os.path.join(pkg_ceto_description, 'models') + ':' + gz_resource_path
    else:
        new_gz_resource_path = os.path.join(pkg_ceto_description, 'models')

    set_model_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=new_gz_resource_path
    )

    # Include the standard ros_gz_sim launcher (starts gzserver + gz GUI)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r -v 4 {world_path}'}.items(),
    )

    # Spawn the bluerov SDF file into the running world
    spawn_bluerov = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', model_sdf_path,
            '-name', 'bluerov',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.0',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_model_path,
        gazebo,
        spawn_bluerov
    ])

