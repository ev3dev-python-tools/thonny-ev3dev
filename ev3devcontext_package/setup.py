from setuptools import setup
import os.path
import sys


setup(
      name="ev3devcontext",
      version="0.35",
      description="using the ev3devcontext library your EV3 program can run in different contexts without the need to change a single line of code",
      long_description="""
Using the ev3devcontext library your EV3 program can run in different contexts
without the need to change a single line of code.

For more info: https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devcontext
""",
      url="https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devcontext",
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
      python_requires=">=3.4",
      install_requires=['rpyc<4.0.0','python-ev3dev','python-ev3dev2'],
      py_modules=["ev3devcontext"]
)
