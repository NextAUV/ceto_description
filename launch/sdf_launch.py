import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_ceto_description = get_package_share_directory('ceto_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths
    world_path = os.path.join(pkg_ceto_description, 'worlds', 'sauvc25.world')
    model_dir = os.path.join(pkg_ceto_description, 'models')
    model_sdf_path = os.path.join(model_dir, 'bluerov2', 'model.sdf')

    # Build new resource path(s)
    existing_gz_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    existing_ign_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')

    # Prepend our model directory
    new_gz_path = f"{model_dir}:{existing_gz_path}" if existing_gz_path else model_dir
    new_ign_path = f"{model_dir}:{existing_ign_path}" if existing_ign_path else model_dir

    # Export both variables so meshes in SDF resolve
    set_gz_resource = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=new_gz_path
    )

    set_ign_resource = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=new_ign_path
    )

    # Start Gazebo (gz sim)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f"-r -v 4 {world_path}"
        }.items(),
    )

    # Spawn BlueROV2 model
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

    return LaunchDescription([
        set_gz_resource,
        set_ign_resource,
        gazebo,
        spawn_bluerov2
    ])
