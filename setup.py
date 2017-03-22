from setuptools import setup

setup(name='py_nic',
      version='1.0',
      description='Making Windows NIC adding/deleting IPv4 addresses easier.',
      author='Alex Dykstra',
      packages=['py_nic'],
      package_dir={'py_nic': 'py_nic'},
      requires=['netifaces'],
     )