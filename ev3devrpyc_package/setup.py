from setuptools import setup
import os.path
import sys


setup(
      name="ev3devrpyc",
      version="0.37",
      description="Transform ev3dev(2) api into a remoted proxied api using rpyc",
      long_description="""
Transform ev3dev(2) api into a remoted proxied api using rpyc.      
      
When importing this module it installs a special importer into the python import infrastructure which from then
proxies every ev3dev module when imported.     

For more info: https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devrpyc
""",
      url="https://www.github.com/harcokuppens/thonny-ev3dev/wiki/ev3devrpyc",
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
      python_requires=">=3.4",
      install_requires=['rpyc==4.1.2','python-ev3dev','python-ev3dev2'],
      py_modules=["ev3devrpyc"]
)
