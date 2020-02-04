

# Developing thonny-ev3dev plugin

## setup plugin project with multiple dependencies (each a git project) 
 To develop the thonny-ev3dev plugin we need to have several dependent projects also setup.
 E.g. the thonny-ev3dev uses the ev3devcmd library to implement most of its functionality. 
 But it offcourse also requires the thonny package which implements the Thonny IDE for which 
 this project is a plugin. Often you want to develop in both the thonny-ev3dev plugin and its 
 and the ev3devcmd project it depends on.
 
 To allow developing in the thonny-ev3dev plugin and some of its dependent
 projects we setup the thonny-ev3dev project as the main project/module in 
 the Intellij IDEA IDE, and setup its dependendent projects as dependent modules.
 The IDEA IDE conveniently lets you define the dependent modules as 
 dependencies of the main module. For python projects this means that all the
 dependent modules are automatically placed on the python path of the main module.
 Meaning that the when the main module can uses code of one of the dependent modules.
 We can work in several projects in parallel and still let them cooperate in the main 
 project.
 
 
 Instructions to setup:

 * checkout from git the main project (thonny-ev3dev)
 
     - https://github.com/ev3dev-python-tools/thonny-ev3dev.git
 
 * within the main project make a subdir submodules/ <br>
   we choose to have the dependent projects as subdirs within the main project.
 * add submodules/ to .gitignore of the main project<br>
   - NOTE: submodules/  shouldn't be in project, and must be added to only here now because we want to work on 
     project's main modules and its sub modules at the same time in a single project!! 
     The main project, and the subprojects all have their own git project independent of each other.
                
 * within submodules/ checkout from git each sub project:
 
    - https://github.com/thonny/thonny.git (take some specific tagged version) 
    - https://github.com/ev3dev-python-tools/ev3devcmd.git
    - https://github.com/ev3dev-python-tools/ev3dev2simulator.git
    - https://github.com/ev3dev-python-tools/ev3devrpyc.git
    - https://github.com/ev3dev-python-tools/ev3devlogging.git
    
 * configure subprojects to be used by main project:
    - intellij IDEA IDE:
        + make from the main project an IDEA project where the main project itself is a module within the IDEA project<br>
          Note: if you create in IDEA a new project from "existing sources" or "version control", then it automatically makes
          a new project with the repository in a new module within that project. 
        + make for each submodules/X/ subproject an IDEA module within the IDEA project
        + in the IDEA project configure the main IDEA module such that all other modules in the submodules/
          directory are a dependency of the main IDEA module. Then when making 
          a run configuration for the main project we can say that it can  
             - add content roots to PYTHONPATH
             - add source roots to PYTHONPATH
          
          where 'roots' means all content/source roots of the main module and all of its dependencies (modules)!!
          
    - any IDE for python : 
       + we directly set the PYTHONPATH environment variable to make subprojects available to the main project
       + we add each submodules/X/ directory to the PYTHONPATH environment variable
       + then when you run main python script in main project it will find the other python modules  
  

We cloned each subproject ourselves, because that is easier and less confusing then using the submodules feature in
git itself. 

In an earlier version we used on macos softlinks to fix the python path in the main project to the subprojects,
however that was not portable to windows. Configuring the module dependencies in the IDEA IDE is most natural 
way to setup the project: just specify the dependencies, and technical details off python path is automatically set.

## virtualenv python

Within the IDE you are using we want to use a python SDK which is independent of the system's python installation.

We use "virtualenv" which is supported by the Intellij IDEA. Within the IDEA project we create an python SDK
with virtualenv in ~/.virtualenvs/ hidden directory in your home directory.  We don't add the virtualenv into
the project because it can become very large, and it can easy be replicated. By putting it in a special 
location we can exclude it also from being backed up. 

In the IDEA IDE we can use this virtual python environment as the used python SDK for the IDEA project.
Each module in the project can inherit the SDK from the project, so that they all used it. 

With using the "activate" script we can source this python version in an existing bash shell. Then using
the scripts in described in README_bash_scripts.txt we can setup this python environment with all 
the required python packages the project needs.

 