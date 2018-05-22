from thonny.globals import get_workbench
from tkinter.messagebox import showerror
from thonny.ui_utils import SubprocessDialog
from thonny import THONNY_USER_BASE

from thonny.globals import register_runner, get_runner

from thonny.misc_utils import running_on_mac_os, running_on_windows, running_on_linux


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


myip='192.168.0.1'


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
            cmd.environment={ "EV3MODE" : "remote", "EV3IP": myip }

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
           )




def patch_ev3():
    """Patch EV3."""
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd','patch']
    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Patch a newly installed ev3dev sdcard for usage with thonny-ev3dev plugin", autoclose=False)
    dlg.wait_window()




def upload(file=None):
    """Uploads given .py file to EV3."""
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd','upload','--force']
    if file != None:
        list.append(file)
    else:
        return
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
        ast.parse(code)
        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
        py_file = get_workbench().get_current_editor().save_file(False)
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
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd','start']
    if file != None:
        # take basename to find it in on the ev3 on the user's homedir!
        list.append(os.path.basename(file))
    else:
        return
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


def download_log(file=None):
    """Uploads given .py file to EV3."""
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd','download',"--force"]
    if file != None:
        # take basename to find it in on the ev3 on the user's homedir!
        # also add ".err.log" if file doesn't end with it!
        file=os.path.basename(file.strip())
        if not file.endswith(".err.log"):
            file=file + ".err.log"
        list.append(file)
    else:
        return
    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Downloading log of program from EV3", autoclose=True)
    dlg.wait_window()
    if dlg.returncode == 0:
        get_workbench().get_editor_notebook().show_file(file)



def download_log_of_current_script():
    """upload current python script to EV3"""
    current_editor = get_workbench().get_editor_notebook().get_current_editor()
    code = current_editor.get_text_widget().get("1.0", "end")
    try:
        ast.parse(code)
        #Return None, if script is not saved and user closed file saving window, otherwise return file name.
        py_file = get_workbench().get_current_editor().save_file(False)
        if py_file is None:
            return
        download_log(py_file)
    except Exception:
        error_msg = traceback.format_exc(0)+'\n'
        showerror("Error", error_msg)

def cleanup_files_on_ev3():
    """Uploads given .py file to EV3."""
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'ev3devcmd','cleanup']
    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = MySubprocessDialog(get_workbench(), proc, "Delete files in homedir on EV3", autoclose=False)
    dlg.wait_window()



def load_plugin():
    """Adds upload button on GUI and commands under Tools menu."""

    image_path_remoterun = os.path.join(os.path.dirname(__file__), "res", "remoterun.gif")
    image_path_remotedebug = os.path.join(os.path.dirname(__file__), "res", "remotedebug.gif")


    image_path_upload = os.path.join(os.path.dirname(__file__), "res", "up.gif")
    image_path_run = os.path.join(os.path.dirname(__file__), "res", "flash.gif")
    image_path_log = os.path.join(os.path.dirname(__file__), "res", "log.gif")

    image_path_clean = os.path.join(os.path.dirname(__file__), "res", "clean.gif")




    # menu buttons

    # "Run current script using the remote control EV3 API"  => by using API word we explicitly say the API is remotely controling the ev3 and not the whole program
    # "Run current script using the remote control thonny.ev3 API"  -> no too technical
    # "Run current script using remote control of the EV3"  => "using" better then "with" because we explicitly use that for the ev3, other stuff is not using that!
    # "Run current script with remote control of the EV3"
    # "Run current script with the EV3 remote controlled"
    # "Run current script where we remote control the EV3"
    # "Run current script where the EV3 is remotely controlled"
    # "Run current script using the thonny EV3 API in remote control mode"
    # "Run current script with remotely controlling the EV3"
    # "Run current script with the thonny.ev3 API remotely controlling the EV3"

    # "Run current script with remotely controlling the EV3"  -> unclear how remote control is done
    # "Run current script using the remote control EV3 API"   -> clear that you need remote control api -> in thonny.ev3

    # "Run current script using the EV3 API in remote control mode"  -> also makes clear api can switch modes

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

    get_workbench().add_command("ev3patch", "tools", "Patch a newly installed ev3dev sdcard for usage with thonny-ev3dev plugin",
                                patch_ev3,
                                command_enabled,
                                default_sequence=None,
                                group=270,
                                #image_filename=image_path_upload,
                                include_in_toolbar=True)

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





