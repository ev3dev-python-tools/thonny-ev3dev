import sys
import types # Used to instantiate a Module object, unavailable as a builtin


# rpyc function to load module
# ----------------------------

import os
import rpyc
import socket

connection=None
debug=False
#debug=True

# a reasonable timeout of 3 seconds
# note we do only one attempt
rpyc_timeout=3
rpyc_attempts=1

def importModule(modulepath):
    global connection
    global rpyc_timeout,rpyc_attempts
    ev3ip=os.environ.get('EV3IP') or '192.168.0.1'

    try:
        # connect only the first time, then reuse connection:
        if connection == None:
           if debug:
               print("importModule connect: " + ev3ip)


           port = rpyc.classic.DEFAULT_SERVER_PORT
           stream=rpyc.SocketStream.connect(ev3ip,port,timeout=rpyc_timeout,attempts=rpyc_attempts)
           connection=rpyc.classic.connect_stream(stream)
           #connection = rpyc.classic.connect(ev3ip) # host name or IP address of the EV3
           if debug:
               print(connection)
           # note: attach connection variable as global variable in module so that doesn't get garbage collected
    except socket.timeout as ex:
        raise Exception("remote control connection to ip={ip} timed out".format(ip=ev3ip)) from None
    except ConnectionError as ex:
        raise Exception("connection error in remote control connection to ip={ip}".format(ip=ev3ip)) from None

    result = connection.modules[modulepath]      # import modulepath remotely
    return result

# slight modification of class factory in rpyc.core.netref  
# ---------------------------------------------------------

# Rpyc assumes that modules loaded with rpyc are not in sys.modules
# 
# With using our special import handler the rpyc proxy modules are added to sys.modules
# so that we can import them with the standard import syntax in python.
#
# When an rpyc proxy module is in sys.modules then object instanciation of a a
# class defined in an rpyc module gives an infinite recursive loop. => PROBLEM!!
# We can fix this by wrapping the  rpyc.core.netref.class_factory
# such that when this function is called all ev3dev modules are temporary
# removed from sys.modules, so that it can function normally.


import rpyc.core.netref     

rpyc.core.netref.orig_class_factory = rpyc.core.netref.class_factory

def ev3dev_class_factory(id_pack, methods):
    if debug:
       print("class_factory")
    name_pack = id_pack[0]
    if not name_pack.startswith("ev3dev"):
        return rpyc.core.netref.orig_class_factory(id_pack,methods)
  
    
    # get new list of modules without ev3dev or ev3dev2
    newmodules=sys.modules.copy()
    for key in sys.modules.keys():
        if key.startswith("ev3dev"):
            del(newmodules[key])
            
    origmodules=sys.modules        
    sys.modules=newmodules
    # call rpyc class factory without "ev3dev(2)" modules in sys.modules
    res= rpyc.core.netref.orig_class_factory(id_pack,methods)
    sys.modules=origmodules
    return res

rpyc.core.netref.class_factory=ev3dev_class_factory


#def old_ev3dev_class_factory(id_pack, methods):
#    """Creates a netref class proxying the given class
#
#    :param id_pack: the id pack used for proxy communication
#    :param methods: a list of ``(method name, docstring)`` tuples, of the methods that the class defines
#
#    :returns: a netref class
#    """
#    ns = {"__slots__": (), "__class__": None}
#    name_pack = id_pack[0]
#
#    if not name_pack.startswith("ev3dev2"):
#        return rpyc.core.netref.orig_class_factory(id_pack,methods)
#
#    for name, doc in methods:
#        name = str(name)  # IronPython issue #10
#        if name not in rpyc.core.netref.LOCAL_ATTRS:  # i.e. `name != __class__`
#            #print("make method: " + name)
#            ns[name] = rpyc.core.netref._make_method(name, doc)
#    return type(name_pack, (rpyc.core.netref.BaseNetref,), ns)





# special import handler to load ev3dev modules over rpyc
# -------------------------------------------------------

# src: https://blog.ffledgling.com/python-imports-i.html
#      Writing a Custom Importer in Python
# also see: https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/sys/imports.html#custom-importers


class TmpFinder(object):
    """ Class to find and load modules from rpyc """


    def find_module(self, fullname, path=None):


        if fullname.startswith("ev3dev"):
            # We're returning the loader object here, which in this case, just
            # happens to be the same as the finder object
            return self

        # Default return for a function is None of course, so we do nothing
        # special when we don't find the module

    def load_module(self, fullname):
        # Helpful print statement tells us when loader is used
        #print('load_module: ' + fullname)

        # If the module already exists in `sys.modules` we *must* use that
        # module, it's a mandatory part of the importer protcol
        if fullname in sys.modules:
            # Do nothing, just return None. This likely breaks the idempotency
            # of import statements, but again, in the interest of being brief,
            # we skip this part.
            return

        try:
            # The importer protocol requires the loader create a new module
            # object, set certain attributes on it, then add it to
            # `sys.modules` before executing the code inside the module (which
            # is when the "module" actually gets code inside it)


            m=importModule(fullname)
            if debug:
                print("importModule: " + fullname)
                print("module: "+ str(m))
                print("__loader__: "+ str(m.__loader__))
                print("__name__: "+ str(m.__name__))
                print("__path__: "+ str(getattr(m,"__path__","UNDEFINED")))
                print("__package__: "+ str(m.__package__))


            #m.__name__ = fullname       # not needed, name already correct
            #m.__package__ = "ev3dev2"   # not needed, package name already correct
            
            ##m.__path__ = "/dev/zero"  # BREAKS import
            ##m.__loader__ = self   # BREAKS second import

            sys.modules[fullname]=m
            #sys.modules.setdefault(fullname, m)
            return m

        except Exception as e:
            # If it fails, we need to reset sys.modules to it's old state. This
            # is good practice in general, but also a mandatory part of the
            # spec, likely to keep the import statement idempotent and free of
            # side-effects across imports.

            # Delete the entry we might've created; use LBYL to avoid nested
            # exception handling
            if sys.modules.get(fullname):
                del sys.modules[fullname]
            raise e


# activate our special importer 
sys.meta_path.insert(0,TmpFinder())
