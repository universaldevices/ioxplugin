from setuptools import setup, find_packages
ud_plugin_version="1.4.3"

setup(
    name='ioxplugin',
    version=ud_plugin_version,
    packages=find_packages(),
    description='IoX Plugin Helper Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Michel Kohanim',
    author_email='support@universal-devices.com',
    url='https://github.com/universaldevices/ioxplugin.git',
    install_requires=[
        'udi_interface>=3.0.57',  # Specify version ranges if needed
        'astor',
        'fastjsonschema'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    package_data={
        "ioxplugin": ["create_launch_env.sh"],
    },
    include_package_data=True
)
