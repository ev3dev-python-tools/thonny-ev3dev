from setuptools import setup
import os.path
import sys

setupdir = os.path.dirname(__file__)



setup(
      name="thonny-ev3dev",
      version="1.0.2",
      description="A plug-in which adds EV3 support for Thonny",
      long_description="""
The thonny-ev3dev package is a plug-in which adds EV3 support for Thonny.

The thonny-ev3dev plugin makes it easier to program the EV3 programmable 
LEGO brick using the Thonny Python IDE for beginners.

Thonny-ev3dev allows you to run your EV3 program easily

- on the EV3 or
- on the PC in a simulator (default on PC)
- on the PC remotely steering the EV3

The thonny-ev3dev plugin comes with an ev3dev simulator.

For more info about the thonny-ev3dev plugin see: https://github.com/ev3dev-python-tools/thonny-ev3dev/wiki

For more info about Thonny: http://thonny.org
""",
      url="https://github.com/ev3dev-python-tools/thonny-ev3dev",
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
        "Topic :: Education",
        "Topic :: Software Development",
      ],
      keywords="IDE education programming EV3 mindstorms lego",
      platforms=["Windows", "macOS", "Linux"],
      python_requires=">=3.6",
      install_requires=['ev3devcmd==1.0.0','ev3dev2simulator'],
      packages=["thonnycontrib.ev3dev"],
      package_data={'thonnycontrib.ev3dev': ['res/*']}
)
