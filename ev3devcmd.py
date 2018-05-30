
import paramiko
import rpyc
import sys
import os.path
import argparse



def checkfile(PATH):
    if not ( os.path.isfile(PATH) and os.access(PATH, os.R_OK) ):
        print("Either file '{0}' is missing or is not readable".format(PATH),file=sys.stderr)
        sys.exit(1)


def sshconnect(args):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(args.address, username=args.username, password=args.password,look_for_keys=False)

    return ssh

def file_exist_on_ev3(ftp,filepath):
    file_exist=True
    try:
        ftp.lstat(filepath)
    except FileNotFoundError:
        file_exist=False
    return  file_exist

def upload(args):

    srcpath=args.file
    checkfile(srcpath)

    # for safety:  can only upload file into  homedir
    destpath='/home/'+ args.username + '/' + os.path.basename(srcpath)

    #print("start uploading:  srcpath=" + srcpath)
    #print("start uploading: destpath=" + destpath)
    #sys.stdout.flush()

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



def start(args):

    # allow to execute file from everywhere on EV3, however by default to path relative to homedir
    srcpath=args.file

    # srcpath not given as absolute path, then take it relative to homedir
    if srcpath[0] != "/" and srcpath[0] != "\\":
        srcpath='/home/'+ args.username + '/' + srcpath
        # remove any . or ..
        srcpath=os.path.abspath(srcpath)

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

def download(args):


    srcpath=args.file
    destpath=os.path.basename(srcpath)

    if srcpath[0] != "." and srcpath[0] != "/" and srcpath[0] != "\\":
        srcpath='/home/'+ args.username + '/' + srcpath

    from pathlib import Path
    home = str(Path.home())
    destpath=os.path.join(home,destpath)

    if os.path.isfile(destpath) and not args.force:
        print("Failed to download because destination '{0}' already exists. Use --force option to force overwriting.".format(destpath),file=sys.stderr)
        sys.exit(1)

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    if not file_exist_on_ev3(ftp,srcpath):
        print("The file '{0}' doesn't exist on the EV3.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("ftp.get({0}, {1}".format(srcpath, destpath))




    try:
        ftp.get(srcpath, destpath)
    except IOError:
        print("Failed to download the file on the EV3 at '{0}  to file '{1}'.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    ftp.close()
    ssh.close()
    print("succesfully downloaded the file on EV3 at '{0}' to file '{1}'.".format(srcpath,destpath) )

def listfiles(args):

    if args.dir=='/home/USERNAME':
        args.dir='/home/'+args.username

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

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()
    ftp.remove(destpath)
    ftp.close()
    ssh.close()
    print("succesfully deleted on EV3 the file: " + destpath)


def patch(args):

    # patch
    #  - ev3devcontext.py  :  thonny/shared/ev3devcontext.py  => ev3:/usr/lib/python3/dist-packages/
    #  - rpyc systemd
    #          sudo apt-get install rpyc       => problem need network on ev3!!

    # import urllib.request
    # import tempfile
    #
    # # Download the file from `url` and save it locally
    # url='https://github.com/tomerfiliba/rpyc/archive/3.4.4.zip'
    # tempdir=tempfile.gettempdir()
    # distfile=os.path.join(tempdir,'rpyc-3.4.4.zip')
    # distfile_ev3 ='/tmp/rpyc-3.4.4.zip'
    # urllib.request.urlretrieve(url,distfile)


    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    print("add /usr/bin/brickmanrun")

    ftp.put(os.path.join(dir_path,'thonnycontrib','ev3dev','res','brickmanrun'), '/tmp/brickmanrun')
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


    print("add /usr/bin/rpyc_classic__threaded_hup_reset.py")

    ftp.put(os.path.join(dir_path,'thonnycontrib','ev3dev','res','rpyc_classic__threaded_hup_reset.py'), '/tmp/rpyc_classic__threaded_hup_reset.py')
    ftp.chmod('/tmp/rpyc_classic__threaded_hup_reset.py', 0o775)

    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/rpyc_classic__threaded_hup_reset.py /usr/bin/rpyc_classic__threaded_hup_reset.py',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()


    print("add /etc/systemd/system/rpycd.service")

    ftp.put(os.path.join(dir_path,'thonnycontrib','ev3dev','res','rpycd.service'), '/tmp/rpycd.service')


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



    print("add /usr/lib/python3/dist-packages/ev3devcontext.py")

    #ftp.put(os.path.join(dir_path,'thonny','shared','ev3devcontext.py'), '/tmp/ev3devcontext.py')
    ftp.put(os.path.join(dir_path,'ev3devcontext.py'), '/tmp/ev3devcontext.py')

    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/ev3devcontext.py /usr/lib/python3/dist-packages/ev3devcontext.py',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("\n\nfinished")

    ftp.close()
    ssh.close()



def _remote_rpyc_stop_and_reset(soft_reset,credentials):
    conn=None
    try:
        ip=credentials.address
        conn = rpyc.classic.connect(ip) # host name or IP address of the EV3
    except:
        pass

    if conn:

        # kill motors
        ev3= conn.modules['ev3dev.ev3']
        for m in ev3.list_motors():
            #print(m)
            m.reset()

        os= conn.modules['os']
        sudoPassword='maker'



        # kill programs running on ev3
        command="kill -9 -`pgrep -f 'python3 /home/robot'`"
        # no sudo needed, program runs as user robot
        os.system(command)


        # kill sound via beep
        command='pkill -f /usr/bin/aplay'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command))


        # kill sound aplay
        command='pkill -f /usr/bin/beep'
        os.system('echo %s|sudo -S %s' % (sudoPassword, command))


        if soft_reset:


            command='systemctl restart brickman'
            os.system('echo %s|sudo -S %s' % (sudoPassword, command))

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




def stop_ev3_programms__and__rpyc_motors_sound(args):
    _remote_rpyc_stop_and_reset(False,args)


def soft_reset_ev3(args):
    _remote_rpyc_stop_and_reset(True,args)


# def sighup(args):
#     """send SIGHUP signal to the RPyC server on the ev3 to close all connected RPyC clients"""
#
#     ssh=sshconnect(args)
#
#     try:
#         stdin, stdout, stderr =ssh.exec_command("sudo pkill -1 -f 'rpyc_classic__threaded_hup_reset.py'",get_pty=True)
#         stdin.write(args.password+'\n')
#         stdin.flush()
#         data = stdout.read().splitlines()
#         data = stderr.read().splitlines()
#
#     except Exception as inst:
#         print("Failed to send SIGHUP signal to the RPyC server on the EV3",file=sys.stderr)
#         ssh.close()
#         sys.exit(1)
#
#     ssh.close()


def cleanup(args):

    # only allow cleanup of homedir; other operations to dangerous
    # note: assumes no subdirs are in homedir, and if they are there, then the cleanup
    #       prints an error when it fails in deleting an directory as an file
    args.dir='/home/'+args.username + '/'

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    try:
        files=ftp.listdir(args.dir)
    except IOError:
        print("Failed to access directory  '{0}'.".format(args.dir),file=sys.stderr)

        ftp.close()
        ssh.close()
        sys.exit(1)

    print("Deleting files in '{0}':".format(args.dir))
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
    parser_list = subparsers.add_parser('list',help="list all files in home folder on EV3")
    parser_list.set_defaults(func=listfiles)
    parser_list.add_argument('dir', nargs='?', default='/home/USERNAME')
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload',help="upload file to EV3")
    parser_upload.add_argument('file', type=str)
    parser_upload.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_upload.set_defaults(func=upload)
    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start',help='start file on EV3; must already be on EV3')
    parser_start.add_argument('file', type=str)
    parser_start.set_defaults(func=start)
    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download',help='download file from EV3')
    parser_download .add_argument('file', type=str)
    parser_download.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_download .set_defaults(func=download)
    # create the parser for the "delete" command
    parser_delete = subparsers.add_parser('delete', help='delete a file in home folder on EV3')
    parser_delete.add_argument('file', type=str)
    parser_delete.set_defaults(func=delete)
    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('cleanup', help='delete all files in home folder on EV3')
    parser_clean.set_defaults(func=cleanup)

    # create the parser for the "clean" command
    parser_patch = subparsers.add_parser('install_additions', help='install additions on the EV3 for thonny-ev3dev when just having installed a newly installed EV3dev image')
    parser_patch.set_defaults(func=patch)

    # # create the parser for the "nohub" command
    # parser_sighup = subparsers.add_parser('sighup', help="send SIGHUP signal to the RPyC server on the EV3 to close all connected RPyC clients")
    # parser_sighup.set_defaults(func=sighup)

    # create the parser for the "softreset" command
    parser_sighup = subparsers.add_parser('softreset', help="soft reset of the EV3  (stop programs,rpyc started sound/motors,restart brickman and rpycd service)")
    parser_sighup.set_defaults(func=soft_reset_ev3)

    # create the parser for the "softreset" command
    parser_sighup = subparsers.add_parser('stop', help="stop all programs on the EV3  (also rpyc started sound/motors)")
    parser_sighup.set_defaults(func=stop_ev3_programms__and__rpyc_motors_sound)

    # parse args,
    args=parser.parse_args(argv[1:])



    # and call the function found by parsing, and pass it the args
    args.func(args)
    sys.stdout.flush()




if __name__ == '__main__':  # start main by default
    sys.exit(main())
