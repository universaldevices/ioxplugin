from setuptools import setup, find_packages

setup(
    name='ioxplugin',
    version='1.1.2',
    packages=find_packages(),
    description='IoX Plugin Helper Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Michel Kohanim',
    author_email='support@universal-devices.com',
    url='https://github.com/universaldevices/ioxplugin.git',
    install_requires=[
        'udi_interface>=3.0.57',  # Specify version ranges if needed
        'astor'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
