import argparse
import os
import socket
import sys
import paramiko

from time import sleep

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
    return ssh



def file_exist_on_ev3(ftp,filepath):
    file_exist=True
    try:
        ftp.lstat(filepath)
    except FileNotFoundError:
        file_exist=False
    return  file_exist


# requires ev3killall installed
def killall(args):

    print("stop programs and motors/sound on EV3")

    ssh=sshconnect(args)
    ftp = ssh.open_sftp()
    password=args.password

    if not file_exist_on_ev3(ftp,'/usr/bin/ev3killall'):
        print("You need to install the EV3 additions to get the ev3killall command working.",file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    try:
        #ssh.exec_command('/usr/bin/ev3killall')
        stdin, stdout, stderr = ssh.exec_command('sudo /usr/bin/ev3killall',get_pty=True)
        stdin.write(args.password+'\n')
        stdin.flush()
        data = stdout.read().splitlines()
        print(data)
        data = stderr.read().splitlines()
        print("\n--------------\n")
        print(data)
    except Exception as inst:
        print("Failed running /usr/bin/ev3killall on the EV3.",file=sys.stderr)
        ftp.close()
        ssh.close()
        sys.exit(1)

    print("Succesfully runned the command ev3killall on the EV3.")

    ftp.close()
    ssh.close()

    # quickly show in modal dialog in thonny before it exits
    print("\n\nstart succesfull")
    sleep(4)  # longer because start on ev3 anyway slow


def testcmd(args):
    print("stop programs and motors/sound on EV3")

    ssh=sshconnect(args)
    password=args.password

    stdin, stdout, stderr = ssh.exec_command('sudo ls',get_pty=True)
    stdin.write(args.password+'\n')
    stdin.flush()
    data = stdout.read().splitlines()
    print(data)
    data = stderr.read().splitlines()
    print("\n--------------\n")
    print(data)


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


    # parse args,
    args=parser.parse_args(argv[1:])


    killall(args)




if __name__ == '__main__':  # start main by default
    sys.exit(main())

