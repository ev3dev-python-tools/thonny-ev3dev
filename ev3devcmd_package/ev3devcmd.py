import socket
import paramiko
import sys
import os
import argparse
import sftpclone.sftpclone
import ev3devlogging

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
        print("\nProblem: failed connecting with EV3: timeout happened.\n         EV3 maybe not connected?\n         Within the Thonny IDE you can fix the EV3 address in \"Tools > Options\" menu.\n         With the ev3dev command you can give the EV3 address as an option.")
        sys.exit(1)
    except paramiko.ssh_exception.AuthenticationException as e:
        print("\nProblem: failed connecting with EV3: authentication failed.\n          Within the Thonny IDE you can the credentials in \"Tools > Options\" menu.\n         With the ev3dev command you can give the credentials as options.")
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    return ssh


def file_exist_on_ev3(ftp,filepath):
    file_exist=True
    try:
        ftp.lstat(filepath)
    except FileNotFoundError:
        file_exist=False
    return  file_exist

def line_buffered(f):
    line_buf = ""
    while not f.channel.exit_status_ready():
        b=f.read(1)
        line_buf += b.decode('utf-8')
        if line_buf.endswith('\n'):
            yield line_buf
            line_buf = ''


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
        print("Running start command on the EV3.")
        client_shell = ssh.invoke_shell()
        stdin = client_shell.makefile('wb')
        stdout = client_shell.makefile('rb')

        # getting sudo rights
        source=r'''
            runprogram(){
                program=$(realpath "$1")
                errlogfile="$program".err.log
                directory=$(dirname "$program")
                /usr/bin/brickrun --directory $directory -- $program 2> $errlogfile  
                if [[ ! -s $errlogfile ]]; then rm -f $errlogfile; fi
            }
        '''

        source= source + '''
            runprogram "{}" >/dev/null &
        '''.format(srcpath)

        stdin.write(source)
        stdin.write('exit\n')
        stdin.flush()

        # read stdout output  line for line so that we can show progress
        # note: stdout also contains stderr of shell

        # stdin gets also output to stdout, so filter that first out (don't print)
        for line in line_buffered(stdout):
            if ("exit" in line):
                break

        # only display stdout without prompt($)
        for line in line_buffered(stdout):
            if (not "$" in line) and (not line.startswith('>')) and (not "Last login:" in line) and (not "logout" in line):
                  print(line, end = '')
    except Exception as inst:
        print(inst)
        print("Failed running start command on the EV3.",file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("\n\nStart succesfully")

    ftp.close()
    ssh.close()

    # quickly show in modal dialog in thonny before it exits
    sleep(4)  # longer because start on ev3 anyway slow







def killall(args):

    print("stop/kill all programs and motors/sound on EV3\n\n")

    ssh=sshconnect(args)
    password=args.password

    try:

        # first quickly kill process, then do slower cleanup afterwards
        print("kill program running on EV3\n")
        ssh.exec_command("kill -9 -`pgrep -f 'python3 /home/robot'`")

        # create interactive shell
        client_shell = ssh.invoke_shell()
        stdin = client_shell.makefile('wb')
        stdout = client_shell.makefile('rb')

        print("stop motors running on EV3\n")
        stdin.write(r'''
            # kill motors
            python3 -c "exec(\"import ev3dev.ev3\nfor m in ev3dev.ev3.list_motors():\n  m.reset()\")"
        ''')
        stdin.flush()
        # getting sudo rights
        stdin.write('echo {}| sudo -S echo "getting sudo rights" &> /dev/null'.format(password))
        stdin.write(r'''
            printf "stop sound on EV3\n"
            # kill sound via beep
            sudo  pkill -f /usr/bin/aplay
            
            # kill sound aplay
            sudo pkill -f /usr/bin/beep
            
            printf "set leds back to default of green\n"
            python3 -c "exec(\"import ev3dev.ev3\nev3dev.ev3.Leds.set_color(ev3dev.ev3.Leds.LEFT, ev3dev.ev3.Leds.GREEN)\nev3dev.ev3.Leds.set_color(ev3dev.ev3.Leds.RIGHT, ev3dev.ev3.Leds.GREEN)\")"
        ''')
        stdin.write('exit\n')
        stdin.flush()
        # read stdout output  line for line so that we can show progress
        # note: stdout also contains stderr of shell

        # stdin gets also output to stdout, so filter that first out (don't print)
        for line in line_buffered(stdout):
            if ("exit" in line):
                break

        # only display stdout without prompt($)
        for line in line_buffered(stdout):
            if (not "$" in line) and (not line.startswith('>')) and (not password in line) and (not "Last login:" in line) and (not "logout" in line):
                print(line, end = '')
    except Exception as inst:
        print("Failed running /usr/bin/ev3killall on the EV3.",file=sys.stderr)
        ssh.close()
        sys.exit(1)

    print("\n\nSuccesfully runned the command 'killall' on the EV3.")
    ssh.close()




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

     # tree -F

    if args.dir=='/home/USERNAME':
        args.dir='/home/'+args.username

    print("List files in '{0}':\n".format(args.dir))

    ssh=sshconnect(args)

    stdin, stdout, stderr = ssh.exec_command('tree -nF',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    for line in data:
        line = str(line, 'utf-8')
        if not args.password in line:
           print(line)
    data = stderr.read().splitlines()
    for line in data:
         print(str(line, 'utf-8'),file=sys.stderr)


    ssh.close()




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






# base mirror of a sourcedir into homedir which preserves . files in homedir
#----------------------------------------------------------------------------
# note: base mirror removes all files not in sourcedir from homedir (except . files in homedir)
orig_rmdir = None
orig_remove = None
base_remote_path = None

def new_remove(remote_path):
    global orig_remove
    global base_remote_path
    if remote_path.startswith( os.path.join(base_remote_path,".") ):
        #print("skip delete: " + remote_path)
        return

    orig_remove(remote_path)

def new_rmdir(remote_path):
    global orig_rmdir
    global base_remote_path
    if remote_path.startswith( os.path.join(base_remote_path,".") ):
        #print("skip delete: " + remote_path)
        return

    orig_rmdir(remote_path)


def base_mirror(args,local_path,dest_path):



    # do extra connect  only for nice error message in case of failure (don't want to hack sftpclone library for that)
    ssh=sshconnect(args)

    remote_url=r'{username}:{password}@{server}:{dest_dir}'.format(username=args.username, password=args.password,server=args.address,dest_dir=dest_path)

    # disable the default of DEBUG logging into CRITICAL only logging
    import logging
    #sftpclone.sftpclone.logger = sftpclone.sftpclone.configure_logging(level=logging.CRITICAL)
    sync = sftpclone.sftpclone.SFTPClone(local_path,remote_url)

    # exclude from syncing the files and dirs in root of sourcedir which start with '.'
    import glob
    # expand local path to real path  => important for getting paths right in exclude list which is compared with the realpath
    # note: within sftpclone paths give are also converted to real paths
    local_path = os.path.realpath(os.path.expanduser(local_path))
    sync.exclude_list = {
        g
        for g in glob.glob(sftpclone.sftpclone.path_join(local_path, ".*"))
    }

    global orig_remove
    global base_remote_path
    base_remote_path=sync.remote_path

    global orig_rmdir

    #sftp.remove
    orig_remove=sync.sftp.remove
    sync.sftp.remove=new_remove

    #sftp.rmdir
    orig_rmdir=sync.sftp.rmdir
    sync.sftp.rmdir=new_rmdir

    sync.run()



#  mirror and cleanup ; implemented using base_mirror
#----------------------------------------------------


def mirror(args):

    src_path=args.sourcedir
    dest_path='/home/'+ args.username

    print("Mirror")
    base_mirror(args,src_path,dest_path)
    print("\n\nmirror succesfull")
    sleep(1)

def cleanup(args):

    # cleanup of homedir; other locations are not cleanable (because to dangerous)
    # note: also removes subdirs in homedir
    dest_path='/home/'+ args.username
    import tempfile
    src_path=tempfile.mkdtemp()

    print("Cleanup")
    base_mirror(args,src_path,dest_path)
    print("\n\ncleanup succesfull")
    sleep(1)


def install_rpyc_server(args):

    print("install rpyc_server")
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    print("install rpyc-4.1.2 package on EV3 (can take 60 seconds)")

    ftp.put(os.path.join(dir_path,'ev3devcmd_res','rpyc-4.1.2.tar.gz'), '/tmp/rpyc-4.1.2.tar.gz')

    stdin, stdout, stderr = ssh.exec_command('sudo tar -C /tmp -xzvf /tmp/rpyc-4.1.2.tar.gz',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    stdin, stdout, stderr = ssh.exec_command('cd /tmp/rpyc-4.1.2/;sudo python3 setup.py install',get_pty=True)
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

    print("start rpycd.service (can take 30 seconds)")

    # restart instead of start, to make sure older version is stopped first
    stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("\n\nfinished")

    ftp.close()
    ssh.close()

def install_ev3devlogging(args):
    print("install ev3devlogging package on EV3")
    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    ftp.put(ev3devlogging.__file__, '/tmp/ev3devlogging.py')

    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/ev3devlogging.py /usr/lib/python3/dist-packages/ev3devlogging.py',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("\n\nfinished")

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


    # use RawDescriptionHelpFormatter: which allows formatting you desription with newlines yourself, however the commandline options
    #                                  are formatted automatically (newlines you place are ignored).
    parser = argparse.ArgumentParser(prog='ev3dev', formatter_class=argparse.RawDescriptionHelpFormatter,
              description="Commands to upload/start/download/delete/cleanup programs on the EV3\nComplete documentation at: https://github.com/harcokuppens/thonny-ev3dev/wiki/ev3devcmd ")

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

    # create the parser for the "mirror" command
    #  mirrors everything from source directory into homedir on EV3
    #  with the --delete option it also deletes everything in homedir on EV3 which was not in sourcedir (excluding . files in homedir)
    # does : rsync -avuze ssh --exclude='/.*' --delete sourcedir/ <ip-ev3>:
    parser_upload = subparsers.add_parser('mirror',help="upload file to homedir on EV3")

    parser_upload.add_argument('srcdir', type=str,help="source directory on pc; destination path on EV3 is /home/USERNAME/")
    parser_upload.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_upload.set_defaults(func=upload)

    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download',help='download file from homedir on EV3')
    parser_download.add_argument('file', type=str,help="destination path on pc; source path on EV3 is /home/USERNAME/basename(file)")
    parser_download.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_download.set_defaults(func=download)
    # create the parser for the "delete" command
    parser_delete = subparsers.add_parser('delete', help='delete a file in homedir on EV3')
    parser_delete.add_argument('file', type=str,help="file in EV3's homedir; directory of file is ignored")
    parser_delete.set_defaults(func=delete)
    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('cleanup', help='delete all files in homedir on EV3')
    parser_clean.set_defaults(func=cleanup)
    # create the parser for the "clean" command
    parser_mirror = subparsers.add_parser('mirror', help='mirror sourcedir into homedir on EV3. Also subdirs are mirrored, and all other files within homedir but not in sourcedir are removed.')
    parser_mirror.add_argument('sourcedir', type=str,help="source directory which gets mirrored.")
    parser_mirror.set_defaults(func=mirror)

    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start',help="run program on EV3; program must already be on EV3's homedir")
    parser_start.add_argument('file', type=str,help="program in EV3's homedir; directory of file is ignored")
    parser_start.set_defaults(func=start)

    # create the parser for the "killall" command
    parser_killall = subparsers.add_parser('killall', help="stop/kill all programs and motors/sound on EV3")
    parser_killall.set_defaults(func=killall)


    # create the parser for the "install_ev3devlogging" command
    parser_install_ev3devlogging = subparsers.add_parser('install_logging', help='install ev3devlogging package on the EV3 when just having installed a newly installed ev3dev image')
    parser_install_ev3devlogging.set_defaults(func=install_ev3devlogging)

    # create the parser for the "install_rpyc_server" command
    parser_install_rpyc_server = subparsers.add_parser('install_rpyc_server', help='install rpyc server on the EV3 when just having installed a newly installed ev3dev image')
    parser_install_rpyc_server.set_defaults(func=install_rpyc_server)

    # parse args,
    args=parser.parse_args(argv[1:])


    # and call the function found by parsing, and pass it the args
    args.func(args)
    sys.stdout.flush()




if __name__ == '__main__':  # start main by default
    sys.exit(main())
