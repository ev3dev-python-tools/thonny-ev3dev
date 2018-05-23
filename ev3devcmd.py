
import paramiko
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
    ssh.connect(args.address, username=args.username, password=args.password)

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
        print("succesfully uploaded file to ev3 as: " + destpath)
    else:
        print("Failed to upload because file '{0}' already exists on ev3. Use --force option to force overwriting.".format(destpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)



def start(args):

    # allow to execute file from everywhere on ev3, however by default to path relative to homedir
    srcpath=args.file

    # srcpath not given as absolute path, then take it relative to homedir
    if srcpath[0] != "/" and srcpath[0] != "\\":
        srcpath='/home/'+ args.username + '/' + srcpath
        # remove any . or ..
        srcpath=os.path.abspath(srcpath)

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()

    if not file_exist_on_ev3(ftp,srcpath):
        print("The file '{0}' doesn't exist on the ev3.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    try:
        ssh.exec_command('/usr/bin/brickmanrun ' + srcpath)
    except Exception as inst:
        print("Failed to start the execution of the file '{0}' on the ev3'.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("Succesfully started  the file '{0}' on the ev3.".format(srcpath))
    print("This command only starts the execution on the ev3, but doesn't wait for the execution to be finished." )
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
        print("The file '{0}' doesn't exist on the ev3.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("ftp.get({0}, {1}".format(srcpath, destpath))




    try:
        ftp.get(srcpath, destpath)
    except IOError:
        print("Failed to download the file on the ev3 at '{0}  to file '{1}'.".format(srcpath),file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    ftp.close()
    ssh.close()
    print("succesfully downloaded the file on ev3 at '{0}' to file '{1}'.".format(srcpath,destpath) )

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
    print("succesfully deleted on ev3 the file: " + destpath)


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
    #for line in data:
    #    print(line)

    data = stderr.read().splitlines()
    #for line in data:
    #    print(line,file=sys.stderr)



    print("add /etc/systemd/system/rpycd.service")

    ftp.put(os.path.join(dir_path,'thonnycontrib','ev3dev','res','rpycd.service'), '/tmp/rpycd.service')


    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/rpycd.service /etc/systemd/system/rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("start rpycd.service")

    stdin, stdout, stderr = ssh.exec_command('sudo systemctl start rpycd.service',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("add /usr/lib/python3/dist-packages/ev3devcontext.py")

    ftp.put(os.path.join(dir_path,'thonny','shared','ev3devcontext.py'), '/tmp/ev3devcontext.py')


    stdin, stdout, stderr = ssh.exec_command('sudo mv /tmp/ev3devcontext.py /usr/lib/python3/dist-packages/ev3devcontext.py',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    data = stderr.read().splitlines()

    print("patch finished succesfull")

    ftp.close()
    ssh.close()



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


    parser = argparse.ArgumentParser(prog='ev3dev')
    parser.add_argument('-a', '--address',action='store',default=default_ip,help="network address of ev3. Can also be set with EV3IP environment variable.")
    parser.add_argument('-u', '--username',action='store',default=default_user,help="username used to login with ssh on ev3. Can also be set with EV3USERNAME environment variable.")
    parser.add_argument('-p', '--password',action='store',default=default_password,help="password used to login with ssh on ev3. Can also be set with EV3PASSWORD environment variable.")


    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list',help="list all files in home folder on ev3")
    parser_list.set_defaults(func=listfiles)
    parser_list.add_argument('dir', nargs='?', default='/home/USERNAME')
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload',help="upload file to ev3")
    parser_upload.add_argument('file', type=str)
    parser_upload.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_upload.set_defaults(func=upload)
    # create the parser for the "start" command
    parser_start = subparsers.add_parser('start',help='start file on ev3; must already be on ev3')
    parser_start.add_argument('file', type=str)
    parser_start.set_defaults(func=start)
    # create the parser for the "download" command
    parser_download = subparsers.add_parser('download',help='download file from ev3')
    parser_download .add_argument('file', type=str)
    parser_download.add_argument('-f', '--force',action='store_true',help="overwrite file if already exist")
    parser_download .set_defaults(func=download)
    # create the parser for the "delete" command
    parser_delete = subparsers.add_parser('delete', help='delete a file in home folder on ev3')
    parser_delete.add_argument('file', type=str)
    parser_delete.set_defaults(func=delete)
    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('cleanup', help='delete all files in home folder on ev3')
    parser_clean.set_defaults(func=cleanup)

    # create the parser for the "clean" command
    parser_patch = subparsers.add_parser('patch', help='install additions on the ev3 for thonny-ev3dev when just having installed a newly installed ev3dev image')
    parser_patch.set_defaults(func=patch)

    # parse args,
    args=parser.parse_args(argv[1:])



    # and call the function found by parsing, and pass it the args
    args.func(args)
    sys.stdout.flush()




if __name__ == '__main__':  # start main by default
    sys.exit(main())
