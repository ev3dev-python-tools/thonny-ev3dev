from thonny.globals import get_workbench
from tkinter.messagebox import showerror
from thonny.ui_utils import SubprocessDialog
from thonny import THONNY_USER_BASE

from threading import Thread


from thonny.globals import register_runner, get_runner

from thonny.misc_utils import running_on_mac_os, running_on_windows, running_on_linux

from thonny.config_ui import ConfigurationPage
from thonny.ui_utils import create_string_var

from tkinter import ttk, messagebox
from tkinter.dialog import Dialog

from thonny import tktextext, misc_utils
from thonny.globals import get_workbench
from thonny.misc_utils import running_on_mac_os, running_on_windows, running_on_linux
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback

import signal
import ast
import re
import subprocess
import sys
import traceback
import jedi
import os
import textwrap

import tokenize

import ev3devcmd




from thonny.common import serialize_message, ToplevelCommand, \
    InlineCommand, parse_shell_command, \
    CommandSyntaxError, parse_message, DebuggerCommand, InputSubmission, \
    UserError




import collections
import threading
from thonny.ui_utils import get_main_background, center_window


# improved  SubprocessDialog from thonny/ui_utils.py
# 1. fix printing error code in _start_listening
# 2. removed confirmation messagebox for canceling in _close
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
        self.text["width"] = 60
        self.text["height"] = 12
        if long_description is not None:
            self.text.direct_insert("1.0", long_description + "\n\n")

        self.button = ttk.Button(main_frame, text="Cancel", command=self._close)
        self.button.grid(row=1, column=0, pady=(0,15))

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)


        self.title(title)
        if misc_utils.running_on_mac_os():
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











def print_error_in_backend(error_str):
    error_source='import sys; print("{}",file=sys.stderr)'.format(error_str)
    cmd=ToplevelCommand(command='execute_source', source=error_source)
    get_runner().send_command(cmd)





def set_focus_on_shell_after_delay():
    def focusback():
        from time import sleep
        sleep(0.1)
        get_workbench().get_view("ShellView").focus_set()

    t = Thread(target=focusback)
    t.start()

def _handle_cd_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "cd"

    if len(args) == 0:
        cmd=ToplevelCommand(command='execute_source', source='import os;from pathlib import Path;home = str(Path.home());os.chdir(home);print("changed to home directory: " + home)')
        get_runner().send_command(cmd)
    else:
       get_runner().send_command(ToplevelCommand(command="cd", path=args[0]))

def _handle_pwd_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "pwd"

    if len(args) == 0:
        cmd=ToplevelCommand(command='execute_source', source='import os;print(os.getcwd())')
        get_runner().send_command(cmd)
    else:
        print_error_in_backend("Command 'pwd' doesn't take arguments")


def _handle_help_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "help"


    magic_cmds=get_workbench().get_view("ShellView").text._command_handlers.keys()
    help_msg="magic commands:\\n" + "\\n".join(map(lambda cmd: "    %"+cmd,magic_cmds))
    help_source="print('"+help_msg+"')"
    cmd=ToplevelCommand(command='execute_source', source=help_source)
    get_runner().send_command(cmd)


def _handle_ls_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "ls"


    if len(args) == 0:
        ls_source='import os; print("\\n".join( sorted(map(lambda item: str(item.name) if (item.is_file()) else str(item.name)+"/" , filter(lambda item:  ( not item.name.startswith(".") ) and ( item.is_dir() or item.name.endswith(".py") or item.name.endswith(".log"))     , os.scandir())   )) ))'
        cmd=ToplevelCommand(command='execute_source', source=ls_source)
        get_runner().send_command(cmd)
    else:
        print_error_in_backend("Command 'ls' doesn't take arguments")



def _handle_open_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "open"

    if len(args) == 1:
        try:
            cwd=get_runner().get_cwd()
            # open file, and to open that window tab viewable it must get focus
            open_file(args[0],cwd)
            # hack to make new prompt to appear
            cmd=ToplevelCommand(command='execute_source', source='')
            get_runner().send_command(cmd)
            # directly setting focus on shell back doesn't work so we use a delay
            set_focus_on_shell_after_delay()
        except FileNotFoundError:
            print_error_in_backend("failed to open")
    else:
        print_error_in_backend("Command 'open' takes one argument")

def _handle_reload_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "reload"

    if len(args) == 1:
        try:
            cwd=get_runner().get_cwd()
            # open file, and to open that window tab viewable it must get focus
            #  => using forced reloading if file already open => no dialog shown, even if there are local changes
            open_file(args[0],cwd,True)
            # hack to make new prompt to appear
            cmd=ToplevelCommand(command='execute_source', source='')
            get_runner().send_command(cmd)
            # directly setting focus on shell back doesn't work so we use a delay
            set_focus_on_shell_after_delay()
        except FileNotFoundError:
            print_error_in_backend("failed to open")
    else:
        print_error_in_backend("Command 'open' takes one argument")



def _handle_reset_from_shell(cmd_line):
    command, args = parse_shell_command(cmd_line)
    assert command == "Reset"

    if len(args) == 0:
        get_runner().send_command(ToplevelCommand(command="Reset"))

        # stop programmings running on ev3 and stop sound/motors via rpyc
        stop_ev3_programs__and__rpyc_motors_sound()
        #rpyc_stop_in_background()

    else:
        print_error_in_backend("Command 'Reset' doesn't take arguments")


def _handle_rundebug_from_shell(cmd_line):
    """
    Handles all commands that take a filename and 0 or more extra arguments.
    Passes the command to backend.

    (Debugger plugin may also use this method)
    """
    command, args = parse_shell_command(cmd_line)

    if len(args) >= 1:
        get_workbench().get_editor_notebook().save_all_named_editors()

        origcommand=command
        if command == "Ev3RemoteRun":
            command="Run"
        if command == "Ev3RemoteDebug":
            command="Debug"

        cmd = ToplevelCommand(command=command,
                              filename=args[0],
                              args=args[1:])

        if origcommand == "Ev3RemoteRun" or origcommand == "Ev3RemoteDebug":
            cmd.environment={ "EV3MODE" : "remote", "EV3IP": get_workbench().get_option("ev3.ip") }

        if os.path.isabs(cmd.filename):
            cmd.full_filename = cmd.filename
        else:
            runner=get_runner()
            cmd.full_filename = os.path.join(runner.get_cwd(), cmd.filename)

        if command in ["Run", "run", "Debug", "debug"]:
            with tokenize.open(cmd.full_filename) as fp:
                cmd.source = fp.read()

        get_runner().send_command(cmd)
    else:

        print_error_in_backend("Command '{}' takes at least one argument".format(command))




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
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Uploading program to EV3", autoclose=True)
    dlg.wait_window()


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
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
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
        py_file = get_workbench().get_current_editor().save_file(False)
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
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Downloading log of program from EV3", autoclose=True)
    dlg.wait_window()
    if dlg.returncode == 0:
        from pathlib import Path
        home = str(Path.home())
        open_file(srcpath,home,True)



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
        src_file = get_workbench().get_current_editor().get_filename(False)
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
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Delete files in homedir on EV3", autoclose=False)
    dlg.wait_window()


def patch_ev3():
    """Install additions needed for thonny-ev3dev plugin on EV3."""
    list = get_base_ev3dev_cmd() + ['install_additions']

    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    #env["PYTHONPATH"] = ":".join(sys.path)

    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)


    dlg = MySubprocessDialog(get_workbench(), proc, "Install thonny-ev3dev plugin additions to the ev3dev sdcard", autoclose=False)
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

        for name in ('ip','username','password'):
            self.__dict__[name]=create_string_var(workbench.get_option("ev3."+name))
        self.makeentry( "IP address:", self.ip, width=10)
        self.makeentry( "User name:", self.username, width=10)
        self.makeentry( "Password:", self.password, width=10)   #, show="*")

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
        for name in ('ip','username','password'):
            variable=self.__dict__[name]
            if variable.modified:
                value = variable.get()
                workbench.set_option("ev3."+name, value)




def get_button_handler_for_magiccmd_on_current_file(magiccmd):
    def button_handler_for_magiccmd_on_current_file():
        # generate a magic command to submit to shell (shell will execute it)
        get_runner().execute_current(magiccmd)

        # hack to get a newline after magic command is done
        if get_runner().get_state() == "waiting_toplevel_command":
            get_workbench().get_view("ShellView").submit_command("\n")

    return  button_handler_for_magiccmd_on_current_file

def command_enabled():
    return  get_runner().get_state() == "waiting_toplevel_command"

def currentscript_and_command_enabled():
    return (get_workbench().get_editor_notebook().get_current_editor() is not None
            and get_runner().get_state() == "waiting_toplevel_command"
            and get_workbench().get_editor_notebook().get_current_editor().get_filename()
            and get_workbench().get_editor_notebook().get_current_editor().get_filename().endswith(".py")
            )

def enabled():
    return True



# def rpyc_stop_in_background():
#     def rpyc_stop_in_background__target():
#         ev3devcmd.sighup(get_credentials())
#
#     t = Thread(target=rpyc_stop_in_background__target)
#     t.start()



def stop_ev3_programs__and__rpyc_motors_sound():

    #soft_reset=False
    #t = Thread(target=remote_rpyc_stop_and_reset,args=(soft_reset,))

    credentials=get_credentials()
    t = Thread(target=ev3devcmd.stop_ev3_programs__and__rpyc_motors_sound,args=[credentials])
    t.start()




def soft_reset_ev3():


    list = get_base_ev3dev_cmd() + ['softreset']

    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Soft reset EV3", autoclose=False)
    dlg.wait_window()

    # #soft_reset=True
    # #t = Thread(target=remote_rpyc_stop_and_reset,args=(soft_reset,))
    # t = Thread(target=soft_reset_ev3())
    # t.start()




def load_plugin():
    """Adds EV3 buttons on toolbar and commands under Run and Tools menu. Add EV3 configuration window."""

    # Add EV3 configuration window
    workbench=get_workbench()
    workbench.set_default("ev3.ip", "192.168.0.1")
    workbench.set_default("ev3.username", "robot")
    workbench.set_default("ev3.password", "maker")
    workbench.add_configuration_page("EV3", Ev3ConfigurationPage)


    # icons

    image_path_remoterun = os.path.join(os.path.dirname(__file__), "res", "remoterun.gif")
    image_path_remotedebug = os.path.join(os.path.dirname(__file__), "res", "remotedebug.gif")


    image_path_upload = os.path.join(os.path.dirname(__file__), "res", "up.gif")
    image_path_run = os.path.join(os.path.dirname(__file__), "res", "flash.gif")
    image_path_log = os.path.join(os.path.dirname(__file__), "res", "log.gif")

    image_path_clean = os.path.join(os.path.dirname(__file__), "res", "clean.gif")





    # menu buttons

    get_workbench().add_command("ev3remoterun", "run", "Run current script using the EV3 API in remote control mode" ,
                                get_button_handler_for_magiccmd_on_current_file("Ev3RemoteRun"),
                                currentscript_and_command_enabled,
                                default_sequence="<F9>",
                                group=20,
                                image_filename=image_path_remoterun,
                                include_in_toolbar=True)
    get_workbench().add_command("ev3remotedebug", "run", "Debug current script using the EV3 API in remote control mode" ,
                                get_button_handler_for_magiccmd_on_current_file("Ev3RemoteDebug"),
                                currentscript_and_command_enabled,
                                default_sequence="<Control-F9>",
                                group=20,
                                image_filename=image_path_remotedebug,
                                include_in_toolbar=True)

    get_workbench().add_command("ev3patch", "tools", "Install ev3dev additions to the ev3dev sdcard on the EV3",
                                patch_ev3,
                                command_enabled,
                                default_sequence=None,
                                group=270,
                                #image_filename=image_path_upload,
                                include_in_toolbar=False)

    get_workbench().add_command("ev3softreset", "tools", "Soft reset the EV3  (stop programs,rpyc started sound/motors,restart brickman and rpycd service)",
                                soft_reset_ev3,
                                command_enabled,
                                default_sequence=None,
                                group=275,
                                #image_filename=image_path_clean,
                                include_in_toolbar=False)



    get_workbench().add_command("ev3upload", "tools", "Upload current script to EV3",
                                upload_current_script,
                                currentscript_and_command_enabled,
                                default_sequence="<F10>",
                                group=280,
                                image_filename=image_path_upload,
                                include_in_toolbar=True)
    get_workbench().add_command("ev3run", "tools", "Start current script on the EV3",
                                start_current_script,
                                currentscript_and_command_enabled,
                                default_sequence="<Control-F10>",
                                group=280,
                                image_filename=image_path_run,
                                include_in_toolbar=True)
    get_workbench().add_command("ev3log", "tools", "Download log of current script from EV3",
                                download_log_of_current_script,
                                currentscript_and_command_enabled,
                                default_sequence=None,
                                group=280,
                                image_filename=image_path_log,
                                include_in_toolbar=True)

    get_workbench().add_command("ev3clean", "tools", "Cleanup EV3 by deleting all files stored in homedir on EV3",
                                cleanup_files_on_ev3,
                                command_enabled,
                                default_sequence=None,
                                group=290,
                                image_filename=image_path_clean,
                                include_in_toolbar=True)



    orig_interrupt_backend=get_runner().interrupt_backend
    def wrapped_interrupt_backend():

        # kill program on pc
        orig_interrupt_backend()

        # stop programmings running on ev3 and stop sound/motors via rpyc
        stop_ev3_programs__and__rpyc_motors_sound()


    get_runner().interrupt_backend = wrapped_interrupt_backend



    # magic commands
    shell = get_workbench().get_view("ShellView")

    shell.add_command("Ev3RemoteRun", _handle_rundebug_from_shell)
    shell.add_command("Ev3RemoteDebug", _handle_rundebug_from_shell)


    shell.add_command("Reset", _handle_reset_from_shell)

    shell.add_command("pwd", _handle_pwd_from_shell)
    shell.add_command("cd", _handle_cd_from_shell)
    shell.add_command("ls", _handle_ls_from_shell)
    shell.add_command("help", _handle_help_from_shell)
    shell.add_command("open", _handle_open_from_shell)
    shell.add_command("reload", _handle_reload_from_shell)






