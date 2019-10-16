from setuptools import setup,find_packages
import os.path
import sys


setup(
      name="ev3dev2simulator",
      version="0.37",
      description="ev3 simulator for ev3dev2 library",
      long_description="""
ev3 simulator for ev3dev2 library

For more info: https://github.com/harcokuppens/thonny-ev3dev/wiki/ev3dev2simulator
""",
      url="https://github.com/harcokuppens/thonny-ev3dev/wiki/ev3dev2simulator",
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
      install_requires=['arcade','pyobjc;sys.platform=="darwin"','pyyaml','pymunk','dataclasses'],
      packages=find_packages(),
      include_package_data=True,

      #packages=["ev3dev2simulator","ev3dev2"],
      #package_dir ={'ev3dev2simulator': 'ev3dev2simulator', 'ev3dev2':'ev3dev2simulator/ev3dev2api/ev3dev2'},
      scripts=['bin/ev3dev2simulator']
)
