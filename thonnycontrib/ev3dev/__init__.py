import ast
import collections
import os
import signal
import subprocess
import threading
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback
from tkinter import ttk
from tkinter.messagebox import showerror

import sys

import ev3devcmd
from thonny import get_runner, tktextext
from thonny import get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.misc_utils import running_on_mac_os, running_on_windows
from thonny.ui_utils import SubprocessDialog, center_window
from thonny.ui_utils import create_string_var,create_int_var
from thonny.ui_utils import CommonDialog


# improved  SubprocessDialog  windows for thonny-ev3dev plugin
#--------------------------------------------------------------


def get_main_background():
    main_background_option = get_workbench().get_option("theme.main_background")
    if main_background_option is not None:
        return main_background_option
    else:
        theme = ttk.Style().theme_use()

        if theme == "Enhanced Clam":
            return "#dcdad5"
        elif theme == "aqua":
            return "systemSheetBackground"
        else:
            return "SystemButtonFace"

# # improved  SubprocessDialog from thonny/ui_utils.py
# # 1. fix printing error code in _start_listening
# # 2. removed confirmation messagebox for canceling in _close
class MySubprocessDialog(tk.Toplevel):
    """Shows incrementally the output of given subprocess.
    Allows cancelling"""

    def __init__(self, master, proc, title, long_description=None, autoclose=True):
        self._proc = proc
        self.stdout = ""
        self.stderr = ""
        self._stdout_thread = None
        self._stderr_thread = None
        self.returncode = None
        self.cancelled = False
        self._autoclose = autoclose
        self._event_queue = collections.deque()

        tk.Toplevel.__init__(self, master)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid(sticky="nsew")

        text_font=tk.font.nametofont("TkFixedFont").copy()
        #text_font["size"] = int(text_font["size"] * 0.9)
        text_font["family"] = "Courier" if running_on_mac_os() else "Courier New"
        text_frame = tktextext.TextFrame(main_frame, read_only=True, horizontal_scrollbar=False,
                                         #vertical_scrollbar=False,
                                         background=get_main_background(),
                                         font=text_font,
                                         wrap="word")
        text_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=15, pady=15)
        self.text = text_frame.text
        self.text["width"] = 85
        self.text["height"] = 15
        if long_description is not None:
            self.text.direct_insert("1.0", long_description + "\n\n")

        self.button = ttk.Button(main_frame, text="Cancel", command=self._close)
        self.button.grid(row=1, column=0, pady=(0,15))

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)


        self.title(title)
        if running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set() # to make it active and modal
        self.text.focus_set()


        self.bind('<Escape>', self._close_if_done, True) # escape-close only if process has completed
        self.protocol("WM_DELETE_WINDOW", self._close)
        center_window(self, master)

        self._start_listening()

    def _start_listening(self):

        def listen_stream(stream_name):
            stream = getattr(self._proc, stream_name)
            while True:
                data = stream.readline()
                self._event_queue.append((stream_name, data))
                setattr(self, stream_name, getattr(self, stream_name) + data)
                if data == '':
                    break

            self.returncode = self._proc.wait()

        self._stdout_thread = threading.Thread(target=listen_stream, args=["stdout"])
        self._stdout_thread.start()
        if self._proc.stderr is not None:
            self._stderr_thread = threading.Thread(target=listen_stream, args=["stderr"])
            self._stderr_thread.start()

        def poll_output_events():
            while len(self._event_queue) > 0:
                stream_name, data = self._event_queue.popleft()
                self.text.direct_insert("end", data, tags=(stream_name, ))
                self.text.see("end")

            self.returncode = self._proc.poll()
            if self.returncode == None:
                self.after(200, poll_output_events)
            else:
                self.button["text"] = "OK"
                self.button.focus_set()
                if self.returncode != 0:
                    self.text.direct_insert("end", "\n\nReturn code: " + str(self.returncode)  , ("stderr", ))
                elif self._autoclose:
                    self._close()

        poll_output_events()


    def _close_if_done(self, event):
        if self._proc.poll() is not None:
            self._close(event)

    def _close(self, event=None):
        if self._proc.poll() is None:
            # try gently first
            try:
                if running_on_windows():
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                else:
                    os.kill(self._proc.pid, signal.SIGINT)

                self._proc.wait(2)
            except subprocess.TimeoutExpired:
                if self._proc.poll() is None:
                    # now let's be more concrete
                    self._proc.kill()


            self.cancelled = True
            # Wait for threads to finish
            self._stdout_thread.join(2)
            if self._stderr_thread is not None:
                self._stderr_thread.join(2)

            # fetch output about cancelling
            while len(self._event_queue) > 0:
                stream_name, data = self._event_queue.popleft()
                self.text.direct_insert("end", data, tags=(stream_name, ))
            self.text.direct_insert("end", "\n\nPROCESS CANCELLED")
            self.text.see("end")

            self.destroy()

        else:
            self.destroy()



# Configuratie page "EV3" in thonny options (preferences window for macos)
#-------------------------------------------------------------------------


class Ev3ConfigurationPage(ConfigurationPage):
    """
     configure connection settings
      * ip address
      * username
      * password

     configure advanced options
      * whether to show Start/Stop buttons on toolbar  (needs restart)
      * rpyc timeout

    """

    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        # HACK: take geometry from options window and increase its width with 5 em for extra ev3 tab
        #       and 10 em for extra heigt for ev3 tab
        optionsWindow=self.master.master
        optionsWindow.update() # to update geometry in optionsWindow
        geometry=optionsWindow.winfo_geometry()
        # print("geometry:",geometry) # needs above update call otherwise geometry: 1x1+0+0
        width=optionsWindow.winfo_width()
        height=optionsWindow.winfo_height()
        # print("width:",width)
        # print("height:",height)
        from  thonny.ui_utils import ems_to_pixels
        width=width+ems_to_pixels(5)
        height=height+ems_to_pixels(10)
        optionsWindow.geometry("%dx%d" % (width, height))

        # get options from workbench
        workbench=get_workbench()
        for name in ('ip','username','password','rpyc_timeout',"playfield"):
            self.__dict__[name]=create_string_var(workbench.get_option("ev3."+name))

        for name in ('show_start_stop_buttons','show_fullscreen','show_maximized','show_on_second_monitor'):
            self.__dict__[name]=create_string_var(workbench.get_option("ev3."+name))
        #self.show_start_stop_buttons=create_int_var(workbench.get_option("ev3.show_start_stop_buttons"))

        ttk.Label(self, text="EV3 connection settings").pack(side=tk.TOP, padx=5, pady=(5,30))

        self.makeentry( "IP address:", self.ip, width=10)
        self.makeentry( "User name:", self.username, width=10)
        self.makeentry( "Password:", self.password, width=10)

        #print("show_start_stop_buttons: ", self.show_start_stop_buttons.get())
        #print("password: ", self.password.get())

        ttk.Label(self, text="EV3 Simulator options").pack(side=tk.TOP, padx=5, pady=(20,20))

        self.makeselect( "Playfield", self.playfield , ["small","large"])
        self.makecheckbox( "Show simulator fullscreen", self.show_fullscreen)
        self.makecheckbox( "Show simulator maximized", self.show_maximized)
        self.makecheckbox( " Show simulator window on second monitor", self.show_on_second_monitor)

        ttk.Label(self, text="EV3 Advanced options").pack(side=tk.TOP, padx=5, pady=(20,20))

        self.makecheckbox( "Show start/stop buttons on toolbar. (needs restart)", self.show_start_stop_buttons)
        self.makeentry( "Rpyc Timeout(secs):", self.rpyc_timeout, width=10)




    def makecheckbox(self,caption, variable, **options):
        row = ttk.Frame(self)

        entry = ttk.Checkbutton(row,text=caption,variable=variable, **options)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        entry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        return entry

    def makeentry(self,caption, variable, **options):
        row = ttk.Frame(self)
        label=ttk.Label(row, width=15, text=caption, anchor='w')
        entry = ttk.Entry(row,textvariable=variable, **options)

        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return entry

    def makeselect(self,caption, variable,values, **options):
        row = ttk.Frame(self)
        label=ttk.Label(row, width=15, text=caption, anchor='w')

        entry = ttk.Combobox(row,textvariable= variable,state="readonly",values=values)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return entry

    def apply(self):
        workbench=get_workbench()
        for name in ('ip','username','password','rpyc_timeout','show_start_stop_buttons','show_fullscreen','show_maximized','show_on_second_monitor','playfield'):
            variable=self.__dict__[name]
            if variable.modified:
                value = variable.get()
                workbench.set_option("ev3."+name, value)




# helper functions for credentials
#----------------------------------

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def get_credentials():

    credentials = {
        'address': get_workbench().get_option("ev3.ip"),
        'username': get_workbench().get_option("ev3.username"),
        'password': get_workbench().get_option("ev3.password")
    }
    return  AttrDict(credentials)

# helper function for ev3dev cmd
#----------------------------------

def get_base_ev3dev_cmd():


    basecmd = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd']

    credentials =  get_credentials()
    return basecmd + [ "-a", credentials.address, "-u", credentials.username, "-p", credentials.password]




# commands
#----------------------------------

ev3dev_version="2.0.0beta5"

def open_ev3dev2_help():
    import webbrowser
    webbrowser.open_new_tab('https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/' + ev3dev_version)


def open_ev3dev2_api():
    import webbrowser
    webbrowser.open_new_tab('https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/' + ev3dev_version + "/spec.html")



def run_simulator():
    show_fullscreen=get_workbench().get_option("ev3.show_fullscreen")
    show_maximized=get_workbench().get_option("ev3.show_maximized")
    show_on_second_monitor=get_workbench().get_option("ev3.show_on_second_monitor")
    playfield=get_workbench().get_option("ev3.playfield")


    # run a new simulator, where we kill the previous running if existing just to enforce a single instance
    # TODO: instead of killing run a server on the simulator to which we can connect to make
    #       an already running instance the foreground window(active)
    #        -> see thonny as example

    # if called on windows, then the exec is "python" but "thonny.exe"
    # replace this then with "pythonw.exe"  because we don't want a console window on windows
    executable=sys.executable.replace("thonny.exe", "pythonw.exe")
    list = [executable, '-m', 'ev3dev2simulator']

    if show_on_second_monitor == True:
        list.append('-2')
        # on windows the second screen can only be use at start when using fullscreen
        if sys.platform.lower().startswith('win'):
            show_maximized=False
            show_fullscreen=True
    if show_fullscreen == True:
        list.append('-f')
    if show_maximized == True:
        list.append('-m')


    list= list + ["-t",playfield ]
    proc = subprocess.Popen(list)
    env = os.environ.copy()
    proc = subprocess.Popen(list, env=env)




def upload(file=None):
    """Uploads given .py file to EV3."""


    if file == None:
        return
    list = get_base_ev3dev_cmd() + [ '--sleep-after', '2', 'upload','--force', file]


    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Uploading program to EV3", autoclose=True)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()



def upload_current_script():
    """upload current python script to EV3"""
    if not currentscript_available():  return
    current_editor = get_workbench().get_editor_notebook().get_current_editor()
    code = current_editor.get_text_widget().get("1.0", "end")
    try:
        filename= current_editor.get_filename()
        if (not filename) or (not filename.endswith(".py")):
            return

        ast.parse(code)

        if not code.startswith('#!'):
            if tkMessageBox.askokcancel("Shebang", "To make a python file on the EV3 executable Thonny prepends the shebang line:\n\n      !#/usr/bin/env python3\n"):
                current_editor.get_text_widget().direct_insert("1.0", "#!/usr/bin/env python3\n")
            else:
               return

        # automatically save file (without confirm dialog, nor dialog for asking filename )
        # save_file does return None, if script is not saved and user closed file saving window, otherwise return file name.
        py_file = current_editor.save_file(False)
        if py_file is None:
            return

        upload(py_file)

    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)




def stop_ev3_program_motors_sound__bg__rpyc_only():
    # Used for enhancing stop button in thonny!
    # The extra stop over rpyc is done in a background thread (use API interface of ev3devcmd)

    # when rpyc_only then use a timeout of 3 seconds; we have time, because no ssh fallback done!
    credentials = {
        'address': get_workbench().get_option("ev3.ip"),
        'username': get_workbench().get_option("ev3.username"),
        'password': get_workbench().get_option("ev3.password"),
        'rpyc_only': True,
        'rpyc_timeout': 3 # see commment above
    }
    stop_args=  AttrDict(credentials)

    t = threading.Thread(target=ev3devcmd.stop, args=[stop_args])
    t.start()


def stop_ev3_program_motors_sound():
    # menu command to stop everything on an EV3 using the cmdline interface of ev3devcmd.
    # First try rpyc, but if that fails because no rpyc server is running,
    # then try using the slower ssh protocol. An ssh server is always running.

    # rpyc timeout is small by default, so that for EV3 where no rpyc server is running we quickly can continue with
    # stopping over ssh instead!
    # However you can change rpyc timeout, and give it along to the stop command!
    # E.g.  you may make it bigger when you are communicating rpyc over bluetooth instead of usb!!
    #       Note: stop button (Stop/Restart backend) in thonny has fixed timeout of 3 seconds,
    #             because that doesn't has ssh fallthrough and is run in background
    #       Note: ev3devrpy module in program making connection  also uses fixed timeout of 3 seconds (same reason)
    #
    #      Thus timeout only applies for
    #                  Menu:  "Device" -> "Stop programs/motor/sound on EV3"
    #      which has ssh fallthrough if rpyc connection fails ( in case no rpyc server on EV3)
    #
    list = get_base_ev3dev_cmd() + ['--sleep-after', '2','stop','--rpyc-timeout',get_workbench().get_option("ev3.rpyc_timeout")]

    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Stop/kill all programs and motors/sound on EV3", autoclose=True)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()


def start(file=None):
    """ Starts given .py file on the EV3.
        Note: thonny-ev3dev plugin assumes file in user's (thonny)  homedir on ev3
    """

    if file == None:
        return
    # take basename to find it in on the ev3 on the user's homedir!
    file = os.path.basename(file)
    list = get_base_ev3dev_cmd() + ['--sleep-after', '4','start', file]


    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Start program on EV3", autoclose=True)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()




def start_current_script_on_ev3():
    """upload current python script to EV3"""
    if not currentscript_available():  return
    current_editor = get_workbench().get_editor_notebook().get_current_editor()
    code = current_editor.get_text_widget().get("1.0", "end")
    try:
        ast.parse(code)
        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
        py_file = current_editor.save_file(False)
        if py_file is None:
            return
        start(py_file)
    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)


def download_log(currentfile=None):
    """downloads log of given .py file from EV3."""

    if currentfile == None:
        return

    # add ".err.log" if file doesn't end with it!
    if not currentfile.endswith(".err.log"):
        currentfile=currentfile + ".err.log"
    
    list = get_base_ev3dev_cmd() + ['download','--force']
    list.append(currentfile)

    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Downloading log of program from EV3", autoclose=True)
    dlg.wait_window()
    if dlg.returncode == 0:
        from pathlib import Path
        home = str(Path.home())
        open_file(currentfile,home,True)
    else:
        # on failure set focus back on original file
        get_workbench().get_editor_notebook().get_current_editor().focus_force()




def open_file(srcpath,basedir=None,force_reload=False):
    if basedir:
        srcpath=os.path.join(basedir,srcpath)

    workbench=get_workbench()

    editor_notebook=workbench.get_editor_notebook()

    editor = editor_notebook.get_editor(srcpath, False)

    if editor:
        # already open
        if force_reload:
            # force reloading source in editor  => overwrites current changes!!
            editor._load_file(srcpath)
            editor.get_text_widget().edit_modified(False)
    else:
        # open new file
        editor=editor_notebook.get_editor(srcpath, True)

    # select the tab in notebook
    editor_notebook.select(editor)
    # and focus this tab
    editor.focus_set()





def download_log_of_current_script():
    """download log of current python script from EV3"""

    try:
        if not currentscript_available():  return
        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
        current_editor = get_workbench().get_editor_notebook().get_current_editor()
        src_file = current_editor.get_filename(False)
        if src_file is None:
            return
        download_log(src_file)
    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)


def mirror_scriptdir_on_ev3():
    """mirror the directory of the current script to the EV3's home directory"""
    if not currentscript_available():  return
    current_editor = get_workbench().get_editor_notebook().get_current_editor()
    filename= current_editor.get_filename()
    srcdir= os.path.dirname(filename)

    list = get_base_ev3dev_cmd() + ['mirror', srcdir]

    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Mirror directory of current script to homedir on EV3", autoclose=False)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()


def cleanup_files_on_ev3():
    """cleanup files in homedir on EV3."""

    list = get_base_ev3dev_cmd() + ['--sleep-after', '2','cleanup']

    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Delete files in homedir on EV3", autoclose=False)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()



def list_files_on_ev3():
    """cleanup files in homedir on EV3."""

    list = get_base_ev3dev_cmd() + ['list']

    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "List files in homedir on EV3", autoclose=False)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()

def install_rpyc_server():
    """Install rpyc server on the EV3. The server is immediately started after installation."""
    list = get_base_ev3dev_cmd() + ['--sleep-after', '2','install_rpyc_server']

    env = os.environ.copy()

    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)


    dlg = MySubprocessDialog(get_workbench(), proc, "Install rpyc server on the EV3. The server is immediately started after installation.", autoclose=False)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()

def install_logging():
    """Install ev3devlogging package to the EV3."""
    list = get_base_ev3dev_cmd() + ['install_logging']

    env = os.environ.copy()

    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)


    dlg = MySubprocessDialog(get_workbench(), proc, "Install ev3devlogging package to the EV3", autoclose=False)
    dlg.wait_window()
    get_workbench().get_editor_notebook().get_current_editor().focus_force()


def cmd_interrupt_reset():
    if get_runner().get_state() == "waiting_toplevel_command":
        get_workbench().get_view("ShellView").submit_command("%Reset\n")
    else:
        get_runner().interrupt_backend()






# helper functions for load_plugin()
#------------------------------------

def command_enabled():
    return  get_runner().get_state() == "waiting_toplevel_command"

def currentscript_and_command_enabled():
    editor=get_workbench().get_editor_notebook().get_current_editor()
    return ( editor is not None
            and get_runner().get_state() == "waiting_toplevel_command"
            and editor.get_filename()
            and editor.get_filename().endswith(".py")
            )

def currentscript_available():
    editor=get_workbench().get_editor_notebook().get_current_editor()
    return ( editor is not None
             and editor.get_filename()
             and editor.get_filename().endswith(".py")
             )


class AboutPluginDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master)

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title("About Ev3dev plugin")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # bg_frame = ttk.Frame(self) # gives proper color in aqua
        # bg_frame.grid()

        import tkinter.font
        import thonnycontrib.ev3dev.version
        import webbrowser
        heading_font = tkinter.font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(
            main_frame, text="Plugin thonny-ev3dev " + thonnycontrib.ev3dev.version.__version__, font=heading_font
        )
        heading_label.grid()

        url = "https://github.com/ev3dev-python-tools/thonny-ev3dev/wiki"
        url_font = tkinter.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(
            main_frame, text=url, style="Url.TLabel", cursor="hand2", font=url_font
        )
        url_label.grid()
        url_label.bind("<Button-1>", lambda _: webbrowser.open(url))

        credits_label = ttk.Label(
            main_frame,
            text="\nMade in\n"
                + "Radboud University \n"
                +" Nijmegen, Netherlands",
            style="Url.TLabel",
            cursor="hand2",
            font=url_font,
            justify="center",
        )
        credits_label.grid()
        credits_label.bind(
            "<Button-1>",
            lambda _: webbrowser.open("https://github.com/ev3dev-python-tools/thonny-ev3dev/wiki/Credits"),
        )

        import datetime
        license_font = tkinter.font.nametofont("TkDefaultFont").copy()
        license_font.configure(size=7)
        license_label = ttk.Label(
            main_frame,
            text="Copyright (©) "
                 + str(datetime.datetime.now().year)
                 + " Harco Kuppens\n"
                 + "This program comes with\n"
                 + "ABSOLUTELY NO WARRANTY!\n"
                 + "It is free software, and you are welcome to\n"
                 + "redistribute it under certain conditions, see\n"
                 + "https://opensource.org/licenses/MIT\n"
                 + "for details",
            justify=tk.CENTER,
            font=license_font,
        )
        license_label.grid(pady=20)

        ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        ok_button.grid(pady=(0, 15))
        ok_button.focus_set()

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._ok, True)

    def _ok(self, event=None):
        self.destroy()

def open_about(*args):
    from thonny import ui_utils
    ui_utils.show_dialog(AboutPluginDialog(get_workbench()))

# load plugin
#--------------

def load_plugin():
    """Adds EV3 buttons on toolbar and commands under Run and Tools menu. Add EV3 configuration window."""

    # Add EV3 configuration window
    workbench=get_workbench()
    workbench.set_default("ev3.ip", "192.168.0.1")
    workbench.set_default("ev3.username", "robot")
    workbench.set_default("ev3.password", "maker")
    workbench.set_default("ev3.rpyc_timeout", "0.1")
    workbench.set_default("ev3.show_start_stop_buttons", 0)

    workbench.set_default("ev3.show_fullscreen", 0)
    workbench.set_default("ev3.show_maximized", 0)
    workbench.set_default("ev3.show_on_second_monitor", 0)
    workbench.set_default("ev3.playfield", "small")

    workbench.add_configuration_page(key="EV3",title="EV3", page_class=Ev3ConfigurationPage,order=1)


    # icons

    image_path_simulator = os.path.join(os.path.dirname(__file__), "res", "simulator.gif")

    image_path_upload = os.path.join(os.path.dirname(__file__), "res", "up.gif")
    image_path_run = os.path.join(os.path.dirname(__file__), "res", "flash.gif")
    image_path_log = os.path.join(os.path.dirname(__file__), "res", "log.gif")
    image_path_killall = os.path.join(os.path.dirname(__file__), "res", "killall.gif")

    image_path_clean = os.path.join(os.path.dirname(__file__), "res", "clean.gif")
    image_path_mirror = os.path.join(os.path.dirname(__file__), "res", "mirror.gif")

    image_path_doc = os.path.join(os.path.dirname(__file__), "res", "doc.gif")
    image_path_api = os.path.join(os.path.dirname(__file__), "res", "api.gif")


    # menu items (first group in device menu; all without icons)

    get_workbench().add_command(command_id="ev3_install_logging",
                                menu_name="tempdevice",
                                command_label="Install ev3devlogging package to the EV3.",
                                caption="Install ev3devlogging package to the EV3.",
                                handler=install_logging,
                                #tester=command_enabled,
                                group=270,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3_install_rpyc_server",
                                menu_name="tempdevice",
                                command_label="Install rpyc server on the EV3. The server is immediately started after installation.",
                                caption="Install rpyc server on the EV3. The server is immediately started after installation.",
                                handler=install_rpyc_server,
                                #tester=command_enabled,
                                group=270,
                                include_in_toolbar=False)

    # menu items (second group in device menu; first three with icons also on toolbar)

    get_workbench().add_command(command_id="ev3upload",
                                menu_name="tempdevice",
                                command_label="Upload current script to EV3",
                                handler=upload_current_script,
                                #tester=currentscript_available,
                                default_sequence="<F10>",
                                group=280,
                                caption="Upload current script to EV3",
                                image=image_path_upload,
                                include_in_toolbar=True)


    get_workbench().add_command(command_id="ev3log",
                                menu_name="tempdevice",
                                command_label="Download log of current script from EV3",
                                caption="Download log of current script from EV3",
                                handler=download_log_of_current_script,
                                #tester=currentscript_available,
                                default_sequence=None,
                                group=280,
                                image=image_path_log,
                                include_in_toolbar=True)


    get_workbench().add_command(command_id="ev3list",
                                menu_name="tempdevice",
                                command_label="List all files in homedir on EV3",
                                caption="List all files in homedir on EV3",
                                handler=list_files_on_ev3,
                                #tester=command_enabled,
                                default_sequence=None,
                                group=280,
                                #image=image_path_clean,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3mirror",
                                menu_name="tempdevice",
                                command_label="Mirror directory of current script to homedir on EV3",
                                caption="Mirror directory of current script to homedir on EV3",
                                handler=mirror_scriptdir_on_ev3,
                                #tester=currentscript_available,
                                default_sequence=None,
                                group=280,
                                image=image_path_mirror,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3clean",
                                menu_name="tempdevice",
                                command_label="Cleanup EV3 by deleting all files stored in homedir on EV3",
                                caption="Cleanup EV3 by deleting all files stored in homedir on EV3",
                                handler=cleanup_files_on_ev3,
                                #tester=command_enabled,
                                default_sequence=None,
                                group=280,
                                image=image_path_clean,
                                include_in_toolbar=True)




    # menu items (third group in device menu; with icons but only on menu)

    show_start_stop_buttons=get_workbench().get_option("ev3.show_start_stop_buttons")

    get_workbench().add_command(command_id="ev3start",
                                menu_name="tempdevice",
                                command_label="Start current script on the EV3",
                                caption="Start current script on the EV3",
                                handler=start_current_script_on_ev3,
                                #tester=currentscript_and_command_enabled,
                                default_sequence="<Control-F10>",
                                group=290,
                                image=image_path_run,
                                include_in_toolbar=show_start_stop_buttons)

    get_workbench().add_command(command_id="ev3stop",
                                menu_name="tempdevice",
                                command_label="Stop program/motors/sound on EV3",
                                caption="Stop program/motors/sound on EV3",
                                handler=stop_ev3_program_motors_sound,
                                #tester=currentscript_and_command_enabled,
                                default_sequence="<Control-F11>",
                                group=290,
                                image=image_path_killall,
                                include_in_toolbar=show_start_stop_buttons)

    # menu items (fourth group in device menu; with icon also on toolbar)

    get_workbench().add_command(command_id="ev3runsim",
                                menu_name="tempdevice",
                                command_label="Run simulator of EV3",
                                caption="Run simulator of EV3",
                                handler=run_simulator,
                                # tester=command_enabled,
                                default_sequence="<F4>",
                                group=300,
                                image=image_path_simulator,
                                include_in_toolbar=True)

    # menu items (fifth group in device menu; with icon also on toolbar)

    get_workbench().add_command(command_id="ev3dev2help",
                                #menu_name="tempdevice",
                                menu_name="help",
                                command_label="ev3dev2 documentation",
                                caption="ev3dev2 documentation",
                                handler=open_ev3dev2_help,
                                default_sequence="<F1>",
                                #group=330,
                                group=50,
                                image=image_path_doc,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3dev2api",
                                #menu_name="tempdevice",
                                menu_name="help",
                                command_label="ev3dev2 API",
                                caption="ev3dev2 API",
                                handler=open_ev3dev2_api,
                                default_sequence="<F2>",
                                #group=330,
                                group=50,
                                image=image_path_api,
                                include_in_toolbar=True)





    # about menu
    get_workbench().add_command("ev3dev_plugin", "help", "About Ev3dev plugin", open_about, group=61)




    # HACK to subscribe an extra function call to command for the Stop/Restart button (with command_id='restart')
    # note: get_workbench().add_command only allows adding, not modifying an existing command
    #       There should come support for this in official plugin API.
    for cmd in get_workbench()._commands:
        if cmd['command_id']== "restart":
            orig_handler=cmd["handler"]
            def new_handler():
                orig_handler()
                # rpyc only because when program is started on thonny
                # then program is running local on pc in simulator or is using
                # steering mode with rpyc commands with ev3devrpyc library.
                # So if steering mode is used we must also remote stop the ev3 with rpyc.
                # However no need to use slower ssh protocol to stop ev3, because when using steering mode we now
                # that an rpyc server is running on ev3.
                stop_ev3_program_motors_sound__bg__rpyc_only()
            cmd["handler"]=new_handler
        if cmd['command_id']== "run_current_script":
            xorig_handler=cmd["handler"]
            def xnew_handler():
                os.environ['EV3IP'] = get_workbench().get_option("ev3.ip")
                xorig_handler()
            cmd["handler"]=xnew_handler

    # HACK: remove annoying ""Where are all the commands?" menu item from "Device" menu added by micropython plugin
    # Note: we add all ev3 commands to "Device" Menu (instead of tools)
    for cmd in get_workbench()._commands:
        if cmd['command_id']== "devicedeprecation":
            get_workbench()._commands.remove(cmd)








