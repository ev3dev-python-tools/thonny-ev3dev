from setuptools import setup
import os.path
import sys

setupdir = os.path.dirname(__file__)

requirements = []
for line in open(os.path.join(setupdir, 'requirements.txt'), encoding="UTF-8"):
    if line.strip() and not line.startswith('#'):
        requirements.append(line)

setup(
      name="thonny-ev3dev",
      version="0.35",
      description="A plug-in which adds EV3 support for Thonny",
      long_description="""
The thonny-ev3dev package is a plug-in which adds EV3 support for Thonny.

To correctly use the thonny-ev3dev plugin you must not use 'import ev3dev.ev3 as
ev3' to import the ev3dev library, but instead you import it as:

    import ev3devcontext; ev3=ev3devcontext.getEV3API()

Then depending on the context(simulator,EV3,pc) the right library is loaded.   

For more info about the thonny-ev3dev plugin see: https://github.com/harcokuppens/thonny-ev3dev/wiki

For more info about Thonny: http://thonny.org
""",
      url="https://www.github.com/harcokuppens/thonny-ev3dev",
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
      install_requires=requirements,
      packages=["thonnycontrib.ev3dev"],
      package_data={'thonnycontrib.ev3dev': ['res/*']}
)
