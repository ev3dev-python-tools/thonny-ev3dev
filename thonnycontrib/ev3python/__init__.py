from thonny.globals import get_workbench
from tkinter.messagebox import showerror
from thonny.ui_utils import SubprocessDialog
from thonny import THONNY_USER_BASE

import ast
import re
import subprocess
import sys
import traceback
import jedi
import os
import textwrap



def upload(file=None):
    """Uploads given .py file to EV3."""
    list = [sys.executable.replace("thonny.exe", "pythonw.exe"), '-m', 'thonnycontrib.ev3python.sshuploadev3']
    if file != None:
        list.append(file)
    env = os.environ.copy()
    env["PYTHONUSERBASE"] = THONNY_USER_BASE
    proc = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True, env=env)
    dlg = SubprocessDialog(get_workbench(), proc, "Uploading program to EV3", autoclose=False)
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


def upload_current_script_enabled():
    """Return false if uploading is not possible."""
    return True


def load_plugin():
    """Adds upload button on GUI and commands under Tools menu."""
    image_path = os.path.join(os.path.dirname(__file__), "res", "up.gif")
    get_workbench().add_command("uploadev3", "tools", "Upload current script to EV3",
                                upload_current_script,
                                upload_current_script_enabled,
                                default_sequence="<F9>",
                                group=120,
                                image_filename=image_path,
                                include_in_toolbar=True)

