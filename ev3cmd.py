
import paramiko
import sys
import os.path
import argparse


myusername='robot'
mypassword='maker'
myip='192.168.0.1'


def upload(args):
    srcpath=args.file
    destpath=os.path.basename(srcpath)

    #print("start uploading:  srcpath=" + srcpath)
    #print("start uploading: destpath=" + destpath)
    sys.stdout.flush()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    ssh.connect(myip, username=myusername, password=mypassword)

    ftp = ssh.open_sftp()
    ftp.put(srcpath, destpath)
    ftp.chmod(destpath, 0o775)
    ftp.close()
    print("\n\nsuccesfully uploaded file: " + destpath)
    sys.stdout.flush()


def start(args):
    print("\n\nTODO")

def fetchlog(args):
    print("\n\nTODO")

def cleanup(args):
    print("\n\nTODO")

def main(argv=None):
    """
    Entry point for the command line tool 'sshuploadev3'.
    """


    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(prog='ev3dev', add_help=False)
    subparsers = parser.add_subparsers()
    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload')
    parser_upload.add_argument('file', type=str)
    parser_upload.set_defaults(func=upload)
    # create the parser for the "start" command
    parser_fetchlog = subparsers.add_parser('start')
    parser_fetchlog.add_argument('file', type=str)
    parser_fetchlog.set_defaults(func=start)
    # create the parser for the "fetchlog" command
    parser_fetchlog = subparsers.add_parser('fetchlog')
    parser_fetchlog.add_argument('file', type=str)
    parser_fetchlog.set_defaults(func=fetchlog)
    # create the parser for the "clean" command
    parser_clean = subparsers.add_parser('cleanup')
    parser_clean.set_defaults(func=cleanup)

    # parse args,
    args=parser.parse_args(argv[1:])
    # and call the function found by parsing, and pass it the args
    args.func(args)





if __name__ == '__main__':  # start main by default
    sys.exit(main())
