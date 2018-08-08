import socket
import paramiko
import rpyc
import sys
import os
import argparse

import ev3devcontext


import functools
print = functools.partial(print, flush=True)

from time import sleep

def checkfile(PATH):
    if not ( os.path.isfile(PATH) and os.access(PATH, os.R_OK) ):
        print("Either file '{0}' is missing or is not readable".format(PATH),file=sys.stderr)
        sys.exit(1)

def sshconnect(args):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # like for rpyc.classic.connect we use a 3 seconds timeout for ssh.connect
        ssh.connect(args.address, username=args.username, password=args.password,timeout=3,look_for_keys=False)
    except socket.timeout as e:
        print("\nProblem: failed connecting with EV3: timeout happened.\n         EV3 maybe not connected?\n         Or fix EV3 address in \"Tools > Options\" menu.")
        sys.exit(1)
    except paramiko.ssh_exception.AuthenticationException as e:
        print("\nProblem: failed connecting with EV3: authentication failed.\n         Fix credentials in \"Tools > Options\" menu.")
        sys.exit(1)
    return ssh

def file_exist_on_ev3(ftp,filepath):
    file_exist=True
    try:
        ftp.lstat(filepath)
    except FileNotFoundError:
        file_exist=False
    return  file_exist




def upload(args):
    # allow any source path on pc ( relative paths taken relative from cwd where this command is executed)
    # allow only destination path in homedir on ev3 
    
    filename=os.path.basename(args.file)
    srcdir=os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(args.file)))
    srcpath=os.path.join(srcdir,filename)
    checkfile(srcpath)

    # for simplicity:  can only upload file into  homedir, 
    #                  so we only need to specify srcpath of file on pc
    destpath='/home/'+ args.username + '/' + filename


    print("uploading file to EV3 as: " + destpath)

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    if args.force or not file_exist_on_ev3(ftp,destpath):
        ftp.put(srcpath, destpath)
        ftp.chmod(destpath, 0o775)
        ftp.close()
        ssh.close()
        print("succesfully uploaded file to EV3 as: " + destpath)
    else:
        print("Failed to upload because file '{0}' already exists on EV3. Use --force option to force overwriting.".format(destpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    # quickly show in modal dialog in thonny before it exits
    print("\n\nupload succesfull")
    sleep(1)


def steer(args):
    import subprocess
    my_command=[sys.executable, args.file]
    my_env = os.environ.copy()
    my_env["EV3IP"] = args.address
    my_env["EV3MODE"] = 'remote' 
    subprocess.Popen(my_command, env=my_env)

def start(args):

    # for safety:  we can only upload file into  homedir
    # so programs we start also only in homedir

    srcpath='/home/'+ args.username + '/' + os.path.basename(args.file)

    print("Start the execution of the file '{0}' on the EV3'.".format(srcpath))
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    if not file_exist_on_ev3(ftp,srcpath):
        print("The file '{0}' doesn't exist on the EV3.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    try:
        ssh.exec_command('/usr/bin/brickmanrun ' + srcpath)
    except Exception as inst:
        print("Failed to start the execution of the file '{0}' on the EV3'.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("Succesfully started  the file '{0}' on the EV3.".format(srcpath))
    print("This command only starts the execution on the EV3, but doesn't wait for the execution to be finished." )

    ftp.close()
    ssh.close()

    # quickly show in modal dialog in thonny before it exits
    print("\n\nstart succesfull")
    sleep(4)  # longer because start on ev3 anyway slow

def download(args):
    # allow only source path in homedir on ev3 
    # allow any destination path on pc ( relative paths taken relative from cwd where this command is executed)


    # for simplicity:  can only download file from  homedir on ev3, 
    #                  so we only need to specify destpath of file on pc
    filename=os.path.basename(args.file)
    srcpath='/home/'+ args.username + '/' + filename
    destdir=os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(args.file)))
    destpath=os.path.join(destdir,filename)

    if not os.path.isdir(destdir):
        print("Failed to download because destination directory '{0}' does not exists.".format(os.path.dirname(destpath)),file=sys.stderr)
        sys.exit(1)
    if os.path.isfile(destpath) and not args.force:
        print("Failed to download because destination '{0}' already exists. Use --force option to force overwriting.".format(destpath),file=sys.stderr)
        sys.exit(1)

    print("Download file '{0}'".format(srcpath))
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    if not file_exist_on_ev3(ftp,srcpath):
        print("The file '{0}' doesn't exist on the EV3.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    #print("ftp.get({0}, {1})".format(srcpath, destpath))

    try:
        ftp.get(srcpath, destpath)
    except IOError:
        print("Failed to download the file from the EV3 at '{0}  to file '{1}'.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    ftp.close()
    ssh.close()
    print("succesfully downloaded the file from the EV3 at '{0}' to file '{1}'.".format(srcpath,destpath) )


def listfiles(args):

    if args.dir=='/home/USERNAME':
        args.dir='/home/'+args.username

    print("List files in '{0}'".format(args.dir))

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    try:
        files=ftp.listdir(args.dir)
    except IOError:
        print("Failed to list '{0}'.".format(args.dir),file=sys.stderr)

        ftp.close()
        ssh.close()
        sys.exit(1)


    ftp.close()
    ssh.close()

    print("files in '{0}':".format(args.dir))
    for item in files:
        if item[0]==".": continue
        print("    " + item)


def delete(args):
    # deleting a basename => deletes file in user's home directory
    srcpath=args.file
    destpath='/home/'+ args.username + '/' + os.path.basename(srcpath)

    print("Delete on EV3 the file: " + destpath)
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()
    ftp.remove(destpath)
    ftp.close()
    ssh.close()
    print("succesfully deleted on EV3 the file: " + destpath)


def patch(args):

    print("install ev3dev addons")
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    print("add /usr/bin/brickmanrun")

    ftp.put(os.path.join(dir_path,'ev3devcmd_res','brickmanrun'), '/tmp/brickmanrun')
    ftp.chmod('/tmp/brickmanrun', 0o775)


    ## next doesn't work, probably because use of pipe
    # ssh.exec_command('echo maker | sudo -S mv /tmp/rpycd.service /etc/systemd/system/rpycd.service',get_pty=True)

    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/brickmanrun /usr/bin/brickmanrun',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()

    data = stdout.read().splitlines()
    # for line in data:
    #     print(line)

    data = stderr.read().splitlines()
    # for line in data:
    #     print(line,file=sys.stderr)


    print("install ev3devcontext package on EV3")

    ftp.put(ev3devcontext.__file__, '/tmp/ev3devcontext.py')

    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/ev3devcontext.py /usr/lib/python3/dist-packages/ev3devcontext.py',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("add rpycd.service")

    ftp.put(os.path.join(dir_path,'ev3devcmd_res','rpycd.service'), '/tmp/rpycd.service')


    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/rpycd.service /etc/systemd/system/rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("enable  rpycd.service")

    stdin, stdout, stderr = ssh.exec_command('sudo systemctl enable rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    # for line in data:
    #     print(line)
    data = stderr.read().splitlines()
    # for line in data:
    #     print(line,file=sys.stderr)

    print("start rpycd.service")

    # restart instead of start, to make sure older version is stopped first
    stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()


    print("\n\nfinished")


    ftp.close()
    ssh.close()



def _remote_rpyc_stop_and_reset(soft_reset,credentials):

    try:
        ip=credentials.address
        # rpyc.classic.connect has by default a timeout of 3  seconds (see rpyc.SocketStream.connect)
        conn = rpyc.classic.connect(ip) # host name or IP address of the EV3
    except socket.timeout as e:
        print("\nProblem: failed connecting with EV3: timeout happened.\n         EV3 maybe not connected?\n         Or fix EV3 address in \"Tools > Options\" menu.")
        sys.exit(1)


    os= conn.modules['os']
    sudoPassword='maker'


    print("kill programs running on EV3")
    # kill programs running on ev3
    command="kill -9 -`pgrep -f 'python3 /home/robot'`"
    # no sudo needed, program runs as user robot
    os.system(command)

    print("stop motors on EV3")
    # kill motors
    ev3= conn.modules['ev3dev.ev3']
    for m in ev3.list_motors():
        m.reset()

    print("stop sound on EV3")
    # kill sound via beep
    command='pkill -f /usr/bin/aplay'
    os.system('echo %s|sudo -S %s' % (sudoPassword, command))
    # kill sound aplay
    command='pkill -f /usr/bin/beep'
    os.system('echo %s|sudo -S %s' % (sudoPassword, command))

    print("set leds back to default of green")
    ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.GREEN)
    ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.GREEN)


    if soft_reset:

        print("restart brickman on EV3")
        command='systemctl restart brickman'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command))

        print("restart rpycd server on EV3")
        # restart rpycd server
        # note: throws error because we use rpyc protocol to restart rpycd daemone
        #      => gives:
        #            raise EOFError("connection closed by peer")
        #         when loosing rpyc connection
        try:
            command='systemctl restart rpycd'
            os.system('echo %s|sudo -S %s' % (sudoPassword, command))
        except EOFError:
            pass
        #rpyc_stop_in_background()

    print("finished")




def stop_ev3_programs__and__rpyc_motors_sound(args):
    print("stop programs and motors/sound on EV3")
    _remote_rpyc_stop_and_reset(False,args)


def soft_reset_ev3(args):
    print("soft reset the EV3")
    _remote_rpyc_stop_and_reset(True,args)



def cleanup(args):

    # only allow cleanup of homedir; other operations to dangerous
    # note: assumes no subdirs are in homedir, and if they are there, then the cleanup
    #       prints an error when it fails in deleting an directory as an file
    args.dir='/home/'+args.username + '/'

    print("Cleanup")
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    try:
        files=ftp.listdir(args.dir)
    except IOError:
        print("Failed to access directory  '{0}'.".format(args.dir),file=sys.stderr)

        ftp.close()
        ssh.close()
        sys.exit(1)

    print("deleting files in '{0}':".format(args.dir))
    for item in files:
        if item[0]==".": continue

        print("    delete " + args.dir + item)
        try:
           ftp.remove(args.dir + item)
        except IOError:
            print("    Failed to delete '{0}'.".format(args.dir + item),file=sys.stderr)

    ftp.close()
    ssh.close()

def main(argv=None):
    """
    Entry point for the command line tool 'sshuploadev3'.
    """


    if argv is None:
        argv = sys.argv

    # get default values from environment or from hardcoded defaults
    # note: with commandline options you can overwrite the default values
    default_ip=os.environ.get('EV3IP') or '192.168.0.1'
    default_user=os.environ.get('EV3USERNAME') or 'robot'
    default_password=os.environ.get('EV3PASSWORD') or 'maker'


    parser = argparse.ArgumentParser(prog='ev3dev',description="commands to upload/start/download/delete/cleanup programs on the EV3")
    parser.add_argument('-a', '--address',action='store',default=default_ip,help="network address of EV3. Can also be set with EV3IP environment variable.")
    parser.add_argument('-u', '--username',action='store',default=default_user,help="username used to login with ssh on EV3. Can also be set with EV3USERNAME environment variable.")
    parser.add_argument('-p', '--password',action='store',default=default_password,help="password used to login with ssh on EV3. Can also be set with EV3PASSWORD environment variable.")


    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list',help="list all files in homedir on EV3")
    parser_list.set_defaults(func=listfiles)
    parser_list.add_argument('dir', nargs='?', default='/home/USERNAME')
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload',help="upload file to homedir on EV3")
    parser_upload.add_argument('file', type=str,help="source path on pc; destination path on EV3 is /home/USERNAME/basename(file)")
    parser_upload.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_upload.set_defaults(func=upload)
    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download',help='download file from homedir on EV3')
    parser_download.add_argument('file', type=str,help="destination path on pc; source path on EV3 is /home/USERNAME/basename(file)")
    parser_download.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_download.set_defaults(func=download)
    # create the parser for the "delete" command
    parser_delete = subparsers.add_parser('delete', help='delete a file in homedir on EV3')
    parser_delete.add_argument('file', type=str)
    parser_delete.add_argument('file', type=str,help="file in EV3's homedir; directory of file is ignored")
    parser_delete.set_defaults(func=delete)
    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('cleanup', help='delete all files in homedir on EV3')
    parser_clean.set_defaults(func=cleanup)

    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start',help="run program on EV3; program must already be on EV3's homedir")
    parser_start.add_argument('file', type=str,help="program in EV3's homedir; directory of file is ignored")
    parser_start.set_defaults(func=start)
    # create the parser for the "steer" command
    parser_steer = subparsers.add_parser('steer',help="run program on PC remotely steering the EV3")
    parser_steer.add_argument('file', type=str,help="EV3 program on pc")
    parser_steer.set_defaults(func=steer)
    # create the parser for the "stop" command
    parser_sighup = subparsers.add_parser('stop', help="stop all programs on the EV3  (also rpyc started sound/motors)")
    parser_sighup.set_defaults(func=stop_ev3_programs__and__rpyc_motors_sound)
    
    # create the parser for the "softreset" command
    parser_sighup = subparsers.add_parser('softreset', help="soft reset the EV3  (stop programs,rpyc started sound/motors,restart brickman and rpycd service)")
    parser_sighup.set_defaults(func=soft_reset_ev3)

    # create the parser for the "install_additions" command
    parser_patch = subparsers.add_parser('install_additions', help='install ev3dev additions on the EV3 when just having installed a newly installed ev3dev image')
    parser_patch.set_defaults(func=patch)



    # parse args,
    args=parser.parse_args(argv[1:])


    # and call the function found by parsing, and pass it the args
    args.func(args)
    sys.stdout.flush()




if __name__ == '__main__':  # start main by default
    sys.exit(main())
