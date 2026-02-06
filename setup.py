from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'dummy_spider'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', 'dummy_spider', 'launch'),glob('launch/*.py')),
        (os.path.join('share', 'dummy_spider', 'urdf'),glob('urdf/*.xacro')),
        (os.path.join('share', 'dummy_spider', 'config'),glob('config/*.yaml')),
        (os.path.join('share', 'dummy_spider', 'meshes'),glob('meshes/*.STL')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='siva',
    maintainer_email='saikumar14970@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'home_position = dummy_spider.home_position_node:main',
            'surround_check = dummy_spider.camera_movement_node:main',
            'forward_walk = dummy_spider.spider_forward_walk_node:main',
            'side_walk = dummy_spider.spider_side_walk_node:main',
            'spider_spin = dummy_spider.spider_spin_node:main',
            'spider_controller = dummy_spider.spider_controller_node:main',
            'virtual_joy = dummy_spider.virtual_joy_node:main',
            'maze_solver = dummy_spider.maze_solver_node:main',
        ],
    },
)
