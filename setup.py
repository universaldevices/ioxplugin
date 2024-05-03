from setuptools import setup, find_packages

setup(
    name='ioxplugin',
    version='0.1.0',
    packages=find_packages(),
    description='IoX Plugin Helper Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Michel Kohanim',
    author_email='support@universal-devices.com',
    url='https://github.com/universaldevices/ioxplugin.git',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
