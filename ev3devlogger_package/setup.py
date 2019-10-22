from setuptools import setup
import os.path
import sys


setup(
      name="ev3devlogging",
      version="0.38",
      description="easy logging library for ev3dev",
      long_description="""
easy logging library for ev3dev

For more info: https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devlogging
""",
      url="https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devlogging",
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
      #install_requires=['logging'],  # logging in standard distribution
      py_modules=["ev3devlogging==0.38"]
)
