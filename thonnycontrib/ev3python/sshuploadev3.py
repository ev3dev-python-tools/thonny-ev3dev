
import paramiko
import sys
import os.path


def main(argv=None):
    """
    Entry point for the command line tool 'sshuploadev3'.
    """
    if not argv:
        argv = sys.argv[1:]


    srcpath=argv[0]
    destpath=os.path.basename(srcpath)

    print("start uploading: " + srcpath)
    sys.stdout.flush()


    myusername='robot'
    mypassword='maker'
    myip='192.168.0.1'

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


if __name__ == '__main__':  # start main by default
    main(sys.argv[1:])
