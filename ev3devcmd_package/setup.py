from setuptools import setup
import os.path
import sys


setup(
      name="ev3devcmd",
      version="0.38",
      description="ev3devcmd library and cmdline utility",
      long_description="""
ev3devcmd library and cmdline utility

For more info: https://github.com/harcokuppens/thonny-ev3dev/wiki/ev3devcmd
""",
      url="https://github.com/harcokuppens/thonny-ev3dev/wiki/ev3devcmd",
      author="Harco Kuppens",
      author_email="h.kuppens@cs.ru.nl",
      license="MIT",
      classifiers=[
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: Freeware",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Education",
        "Topic :: Software Development",
      ],
      keywords="IDE education programming EV3 mindstorms lego",
      platforms=["Windows", "macOS", "Linux"],
      python_requires=">=3.6",
      install_requires=['ev3devlogging','paramiko==2.6.0','sftpclone==1.2.2'],
      py_modules=["ev3devcmd"],
      #hack to add resource dir to simple python module: using fake package
      packages=["ev3devcmd_res"],
      package_data={'ev3devcmd_res': ['./*']},
      scripts=['bin/ev3dev']
)
