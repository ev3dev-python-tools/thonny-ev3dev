

# Developing thonny-ev3dev plugin

## Setup plugin project with multiple context projects (each a git project) 
 To develop the thonny-ev3dev plugin we need to have several related projects also set up.
 For example, the thonny-ev3dev uses the ev3devcmd library to implement most of its functionality. 
 But it of course also requires the Thonny package which implements the Thonny IDE for which 
 this project is a plugin. In this case, the plugin depends on the IDE. 
 Thus for a plugin to work, we need several projects installed that
 are used in the context of the plugin, therefor we call these 'context projects'.
 When you are developing in a project, a change in the project can require also a change in
 a context project. Eg. you want to develop  the thonny-ev3dev plugin but it might require   
 you to also to develop the ev3devcmd project it depends on. 
 
 To allow developing in the thonny-ev3dev plugin and some of its context
 projects we set up the thonny-ev3dev project as the main project/module in 
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
 
 * within the main project make a subdir context/ <br>
   we choose to have the context projects as subdirs within the main project.
 * add context/ to .gitignore of the main project<br>
   - NOTE: context/  shouldn't be in project, and must be added to only here now because we want to work on 
     project's main modules and its context projects at the same time in a single project!! 
     The main project, and the context projects all have their own git project independent of each other.
                
 * within context/ checkout from git each context project:
 
    - https://github.com/thonny/thonny.git (take some specific tagged version) 
    - https://github.com/ev3dev-python-tools/ev3devcmd.git
    - https://github.com/ev3dev-python-tools/ev3dev2simulator.git
    - https://github.com/ev3dev-python-tools/ev3devrpyc.git
    - https://github.com/ev3dev-python-tools/ev3devlogging.git

   Note: we clone each subproject ourselves because that is easier and less confusing than using the submodules feature in
   git itself. 
    
 * configure context projects to be used by main project:
     1) all projects must be on same PYTHONPATH so that they are available to each other in the same python runtime.
     2) all projects dependencies must be installed

        
   there are several ways to do this, where the last method is preferred:
     
    - conventional way for any IDE for python: 
       + we directly set the PYTHONPATH environment variable to make subprojects available to the main project
       + hence, we add each context/X/ directory to the PYTHONPATH environment variable
       + then when you run main python script in main project it will find the other python modules
       + you need to install the project dependencies for each project manually with pip
       + note: sublinking is not a viable alternative because that is not portable to Windows.
   
    - intellij IDEA IDE:
        + make from the main project an IDEA project where the main project itself is a module within the IDEA project<br>
          Note: if you create in IDEA a new project from "existing sources" or "version control", then it automatically makes
          a new project with the repository in a new module within that project. 
        + make for each context/X/ context project an IDEA module within the IDEA project
        + in the IDEA project configure the main IDEA module such that all other modules in the context/
          directory are a dependency of the main IDEA module. Then when making 
          a run configuration for the main project we can say that it can  
             - add content roots to PYTHONPATH
             - add source roots to PYTHONPATH
          
          where 'roots' means all content/source roots of the main module and all of its dependencies modules!!
        + IDEA installs all dependencies for all projects automatically for you
        + In the IDEA IDE we can use a virtual python environment as the used python SDK for the IDEA project.
          Each module in the project can inherit the SDK from the project, so that they all used it. 
          
     
    - new modern way for all IDEs:  **editable install**
       + install each context project as an editable install
       + also install the main module as an editable install
       + then you can edit your could and its available on the PYTHONPATH by the editable install
       + ADVANTAGE above conventional method: because an editable install is also an install during the installs
         automatically its dependencies are installed
       + ADVANTAGE: this way is python's own way and is not dependent of any IDE
       + all modern IDE's support editable installs
       + note: when using the IDEA IDE do the editable install with the IDE and not with pip,
               because somehow editable installs done by pip are not picked up by the IDE. 
               Vs code however works fine with editable installs done by pip.

   

## use a virtual env 


In python we do not have project support which set ups a sandbox environment for you like in languages like Rust.
Instead you need to create this environment for your project self with an virtual env tool. ( eg. python3 -m venv ).

By using a virtual env we create a sandbox python environment which is independent of the system's python installation.
The virtual env isolates the project from the system python.

Eg. we can use "virtualenv" which is supported by the Intellij IDEA. Within the IDEA project we create an python SDK
with virtualenv in ~/.virtualenvs/ hidden directory in your home directory.  We don't add the virtualenv into
the project because it can become very large, and it can easy be replicated. By putting it in a special 
location we can exclude it also from being backed up. 

With using the "activate" script we can source this python version in an existing bash shell. Then using
the scripts described in README_bash_scripts.txt we can setup this python environment with all 
the required python packages the project needs.

 
