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
from thonny.ui_utils import create_string_var


#MySubprocessDialog = SubprocessDialog


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
        self.text["height"] = 12
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

def get_base_ev3dev_cmd():

    basecmd = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd']

    credentials =  get_credentials()
    return basecmd + [ "-a", credentials.address, "-u", credentials.username, "-p", credentials.password]


def upload(file=None):
    """Uploads given .py file to EV3."""


    if file == None:
        return
    list = get_base_ev3dev_cmd() + ['upload','--force', file]

    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Uploading program to EV3", autoclose=True)
    dlg.wait_window()



def run_simulator():

    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3dev2simulator']
    print(list)
    env = os.environ.copy()
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, env=env)
    #os.system("/Applications/Thonny-3.2.1.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m ev3dev2simulator.Simulator")

def upload_current_script():
    """upload current python script to EV3"""
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

    # when rpyc_only then use a timeout of 3 seconds; we have time, because no ssh fallback done!
    credentials = {
        'address': get_workbench().get_option("ev3.ip"),
        'username': get_workbench().get_option("ev3.username"),
        'password': get_workbench().get_option("ev3.password"),
        'rpyc_only': True,
        'rpyc_timeout': 3
    }
    stop_args=  AttrDict(credentials)

    t = threading.Thread(target=ev3devcmd.stop, args=[stop_args])
    t.start()


def stop_ev3_program_motors_sound():

    # credentials=get_credentials()
    # t = Thread(target=ev3devcmd.stop,args=[credentials])
    # t.start()

    list = get_base_ev3dev_cmd() + ['--rpyc-timeout',get_workbench().get_option("ev3.rpyc_timeout"),'stop']

    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Stop/kill all programs and motors/sound on EV3", autoclose=True)
    dlg.wait_window()


def start(file=None):
    """ Starts given .py file on the EV3.
        Note: thonny-ev3dev plugin assumes file in user's (thonny)  homedir on ev3
    """

    if file == None:
        return
    # take basename to find it in on the ev3 on the user's homedir!
    file = os.path.basename(file)
    list = get_base_ev3dev_cmd() + ['start', file]


    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Start program on EV3", autoclose=True)
    dlg.wait_window()




def start_current_script():
    """upload current python script to EV3"""
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
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Downloading log of program from EV3", autoclose=True)
    dlg.wait_window()
    if dlg.returncode == 0:
        from pathlib import Path
        home = str(Path.home())
        open_file(currentfile,home,True)



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
        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
        current_editor = get_workbench().get_editor_notebook().get_current_editor()
        src_file = current_editor.get_filename(False)
        if src_file is None:
            return
        download_log(src_file)
    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)

def cleanup_files_on_ev3():
    """cleanup files in homedir on EV3."""

    list = get_base_ev3dev_cmd() + ['cleanup']

    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Delete files in homedir on EV3", autoclose=True)
    dlg.wait_window()
    # dlg = MySubprocessDialog(get_workbench(), proc, "Delete files in homedir on EV3", autoclose=True)
    # dlg.wait_window()


def install_rpyc_server():
    """Install rpyc server on the EV3. The server is immediately started after installation."""
    list = get_base_ev3dev_cmd() + ['install_rpyc_server']

    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE

    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)


    dlg = MySubprocessDialog(get_workbench(), proc, "Install rpyc server on the EV3. The server is immediately started after installation.", autoclose=False)
    dlg.wait_window()

def install_logging():
    """Install ev3devlogging package to the EV3."""
    list = get_base_ev3dev_cmd() + ['install_logging']

    env = os.environ.copy()
    #env["PYTHONUSERBASE"] = THONNY_USER_BASE

    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)


    dlg = MySubprocessDialog(get_workbench(), proc, "Install ev3devlogging package to the EV3", autoclose=False)
    dlg.wait_window()


def cmd_interrupt_reset():
    if get_runner().get_state() == "waiting_toplevel_command":
        get_workbench().get_view("ShellView").submit_command("%Reset\n")
    else:
        get_runner().interrupt_backend()

class Ev3ConfigurationPage(ConfigurationPage):
    """
     configure:
      * ip address
      * username
      * password
    """


    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

        ttk.Label(self, text="EV3 connection settings").pack(side=tk.TOP, padx=5, pady=(5,30))
        workbench=get_workbench()

        for name in ('ip','username','password','rpyc_timeout'):
            self.__dict__[name]=create_string_var(workbench.get_option("ev3."+name))
        self.makeentry( "IP address:", self.ip, width=10)
        self.makeentry( "User name:", self.username, width=10)
        self.makeentry( "Password:", self.password, width=10)
        self.makeentry( "Rpyc Timeout(secs):", self.rpyc_timeout, width=10)

    def makeentry(self,caption, variable, **options):
        row = ttk.Frame(self)
        label=ttk.Label(row, width=15, text=caption, anchor='w')
        entry = ttk.Entry(row,textvariable=variable, **options)

        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        return entry

    def apply(self):
        workbench=get_workbench()
        for name in ('ip','username','password','rpyc_timeout'):
            variable=self.__dict__[name]
            if variable.modified:
                value = variable.get()
                workbench.set_option("ev3."+name, value)




def command_enabled():
    return  get_runner().get_state() == "waiting_toplevel_command"

def currentscript_and_command_enabled():
    return (get_workbench().get_editor_notebook().get_current_editor() is not None
            and get_runner().get_state() == "waiting_toplevel_command"
            and get_workbench().get_editor_notebook().get_current_editor().get_filename()
            and get_workbench().get_editor_notebook().get_current_editor().get_filename().endswith(".py")
            )


def load_plugin():
    """Adds EV3 buttons on toolbar and commands under Run and Tools menu. Add EV3 configuration window."""

    # Add EV3 configuration window
    workbench=get_workbench()
    workbench.set_default("ev3.ip", "192.168.0.1")
    workbench.set_default("ev3.username", "robot")
    workbench.set_default("ev3.password", "maker")
    workbench.set_default("ev3.rpyc_timeout", "0.1")

    workbench.add_configuration_page(key="EV3",title="EV3", page_class=Ev3ConfigurationPage,order=1)


    # icons

    image_path_simulator = os.path.join(os.path.dirname(__file__), "res", "simulator.gif")

    image_path_upload = os.path.join(os.path.dirname(__file__), "res", "up.gif")
    image_path_run = os.path.join(os.path.dirname(__file__), "res", "flash.gif")
    image_path_log = os.path.join(os.path.dirname(__file__), "res", "log.gif")
    image_path_killall = os.path.join(os.path.dirname(__file__), "res", "killall.gif")

    image_path_clean = os.path.join(os.path.dirname(__file__), "res", "clean.gif")

    # def add_command(
    #         self,
    #         command_id: str,
    #         menu_name: str,
    #         command_label: str,
    #         handler: Optional[Callable[[], None]] = None,
    #         tester: Optional[Callable[[], bool]] = None,
    #         default_sequence: Optional[str] = None,
    #         extra_sequences: Sequence[str] = [],
    #         flag_name: Optional[str] = None,
    #         skip_sequence_binding: bool = False,
    #         accelerator: Optional[str] = None,
    #         group: int = 99,
    #         position_in_group="end",
    #         image: Optional[str] = None,
    #         caption: Optional[str] = None,
    #         alternative_caption: Optional[str] = None,
    #         include_in_menu: bool = True,
    #         include_in_toolbar: bool = False,
    #         submenu: Optional[tk.Menu] = None,
    #         bell_when_denied: bool = True,
    #         show_extra_sequences=False,
    # ) -> None:

    # menu buttons




    get_workbench().add_command(command_id="ev3upload",
                                menu_name="tools",
                                command_label="Upload current script to EV3",
                                handler=upload_current_script,
                                tester=currentscript_and_command_enabled,
                                default_sequence="<F10>",
                                group=280,
                                caption="Upload current script to EV3",
                                image=image_path_upload,
                                include_in_toolbar=True)


    get_workbench().add_command(command_id="ev3log",
                                menu_name="tools",
                                command_label="Download log of current script from EV3",
                                caption="Download log of current script from EV3",
                                handler=download_log_of_current_script,
                                tester=currentscript_and_command_enabled,
                                default_sequence=None,
                                group=280,
                                image=image_path_log,
                                include_in_toolbar=True)


    get_workbench().add_command(command_id="ev3clean",
                                menu_name="tools",
                                command_label="Cleanup EV3 by deleting all files stored in homedir on EV3",
                                caption="Cleanup EV3 by deleting all files stored in homedir on EV3",
                                handler=cleanup_files_on_ev3,
                                #tester=command_enabled,
                                default_sequence=None,
                                group=280,
                                image=image_path_clean,
                                include_in_toolbar=True)



    get_workbench().add_command(command_id="ev3start",
                                menu_name="tools",
                                command_label="Start current script on the EV3",
                                caption="Start current script on the EV3",
                                handler=start_current_script,
                                tester=currentscript_and_command_enabled,
                                default_sequence="<Control-F10>",
                                group=290,
                                image=image_path_run,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3stop",
                                menu_name="tools",
                                command_label="Stop program/motors/sound on EV3",
                                caption="Stop program/motors/sound on EV3",
                                handler=stop_ev3_program_motors_sound,
                                #tester=currentscript_and_command_enabled,
                                default_sequence="<Control-F11>",
                                group=290,
                                image=image_path_killall,
                                include_in_toolbar=False)


    get_workbench().add_command(command_id="ev3runsim",
                                menu_name="tools",
                                command_label="Run simulator of EV3",
                                caption="Run simulator of EV3",
                                handler=run_simulator,
                                # tester=command_enabled,
                                default_sequence="<F4>",
                                group=300,
                                image=image_path_simulator,
                                include_in_toolbar=True)

    # menu items

    get_workbench().add_command(command_id="ev3_install_logging",
                                menu_name="tools",
                                command_label="Install ev3devlogging package to the EV3.",
                                caption="Install ev3devlogging package to the EV3.",
                                handler=install_logging,
                                tester=command_enabled,
                                group=270,
                                include_in_toolbar=False)

    get_workbench().add_command(command_id="ev3_install_rpyc_server",
                                menu_name="tools",
                                command_label="Install rpyc server on the EV3. The server is immediately started after installation.",
                                caption="Install rpyc server on the EV3. The server is immediately started after installation.",
                                handler=install_rpyc_server,
                                tester=command_enabled,
                                group=270,
                                include_in_toolbar=False)



    #print(get_workbench()._commands)

    for cmd in get_workbench()._commands:
        #print(cmd['command_id'])
        if cmd['command_id']== "restart":
            orig_handler=cmd["handler"]
            def new_handler():
                stop_ev3_program_motors_sound__bg__rpyc_only()
                #install_rpyc_server()
                orig_handler()
            cmd["handler"]=new_handler


    # get_workbench().add_command(
    #     "restart",
    #     "run",
    #     _("Stop/Restart backend"),
    #     caption=_("Stop"),
    #     handler=self.cmd_stop_restart,
    #     default_sequence="<Control-F2>",
    #     group=100,
    #     image="stop",
    #     include_in_toolbar=True,
    # )







