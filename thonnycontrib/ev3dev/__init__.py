from thonny.globals import get_workbench
from tkinter.messagebox import showerror
from thonny.ui_utils import SubprocessDialog
from thonny import THONNY_USER_BASE

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




from thonny.common import serialize_message, ToplevelCommand, \
    InlineCommand, parse_shell_command, \
    CommandSyntaxError, parse_message, DebuggerCommand, InputSubmission, \
    UserError


class MySubprocessDialog(SubprocessDialog):
    """Shows incrementally the output of given subprocess.
    Allows cancelling"""

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







def get_button_handler_for_magiccmd_on_current_file(magiccmd):
    def button_handler_for_magiccmd_on_current_file():
        # generate a magic command to submit to shell (shell will execute it)
        get_runner().execute_current(magiccmd)

        # run python code in shell
        #get_workbench().get_view("ShellView").submit_command("print('hello')\n")

        # hack to get a newline after magic command is done
        if get_runner().get_state() == "waiting_toplevel_command":
            get_workbench().get_view("ShellView").submit_command("\n")

    return  button_handler_for_magiccmd_on_current_file



def currentfile_magiccmd_handler(cmd_line):
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
        raise CommandSyntaxError("Command '%s' takes at least one argument", command)





def command_enabled():
    return  get_runner().get_state() == "waiting_toplevel_command"

def currentscript_and_command_enabled():
    return (get_workbench().get_editor_notebook().get_current_editor() is not None
            and get_runner().get_state() == "waiting_toplevel_command"
            and get_workbench().get_editor_notebook().get_current_editor().get_filename().endswith(".py")
           )





def get_base_ev3dev_cmd():

    basecmd = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd']

    ip=get_workbench().get_option("ev3.ip")
    username=get_workbench().get_option("ev3.username")
    password=get_workbench().get_option("ev3.password")

    credentials = [ "-a", ip, "-u", username, "-p", password]

    return basecmd + credentials


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
        if not filename.endswith(".py"):
            return

        ast.parse(code)

        if not code.startswith('#!'):
            if tkMessageBox.askokcancel("Shebang", "To make a python file on the EV3 executable Thonny prepends the shebang line:\n\n      !#/usr/bin/env python3\n"):
                current_editor.get_text_widget().direct_insert("1.0", "#!/usr/bin/env python3\n")
            else:
               return

        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
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


def download_log(srcpath=None):
    """downloads log of given .py file from EV3."""

    if srcpath == None:
        return
    list = get_base_ev3dev_cmd() + ['download','--force']
    if srcpath != None:
        # take basename to find it in on the ev3 on the user's homedir!
        # also add ".err.log" if file doesn't end with it!
        srcpath=os.path.basename(srcpath.strip())
        if not srcpath.endswith(".err.log"):
            srcpath=srcpath + ".err.log"
        list.append(srcpath)

    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Downloading log of program from EV3", autoclose=True)
    dlg.wait_window()
    if dlg.returncode == 0:
        from pathlib import Path
        home = str(Path.home())
        destpath=os.path.join(home,srcpath)
        get_workbench().get_editor_notebook().show_file(destpath)

        get_workbench().get_current_editor()._load_file(destpath)
        get_workbench().get_current_editor().get_text_widget().edit_modified(False)

        #get_workbench().get_editor_notebook().update_editor_title(get_workbench().get_current_editor())
        #get_workbench().get_editor_notebook().update_appearance()



def download_log_of_current_script():
    """upload current python script to EV3"""
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
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Install thonny-ev3dev plugin additions to the ev3dev sdcard", autoclose=False)
    dlg.wait_window()



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

    get_workbench().add_command("ev3patch", "tools", "Install thonny-ev3dev plugin additions to the ev3dev sdcard",
                                patch_ev3,
                                command_enabled,
                                default_sequence=None,
                                group=270,
                                #image_filename=image_path_upload,
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



    # magic commands
    shell = get_workbench().get_view("ShellView")

    shell.add_command("Ev3RemoteRun", currentfile_magiccmd_handler)
    shell.add_command("Ev3RemoteDebug", currentfile_magiccmd_handler)





