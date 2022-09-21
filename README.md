# CSEC473: HW4 Red Team Script



<h2 style="text-align:left;"><span style="float:center;">RSSHEX (Root SSH Exploit) </span>
</h2>

**Author: Kenyon Litt**

## Purpose
According to the CIS ubuntu linux LTS benchmark, important files critical to system operation should be kept as root ownership for read/write with no other users able to access them. An example of these important files would be /etc/shadow (encrypted password data) and /etc/passwd (user access, and information data). Another important system hardening technique is to always disable root access, as that account has authorization for the entire system. Despite these recommendations, if a sudo’d user can change the file permissions (by accident or on purpose) of shadow and passwd, privilege escalation can occur into the root account, through the SSH config and service. As demonstrated manually, this process essentially happens as a user can remove the password for a user account, remove the ability in ssh for passwords to be required and to remove the protection of root access through ssh (even if its disabled for the system). This script automates and tests for permission and configuration vulnerabilities with ssh and file permissions and can present a root shell to the user on the system via any new (or existing) user account. If this script is successful, it can not only be used for further leverage, but also provide a good metric to configuration security if these options are enabled (aka if this works, other configs or services may be vulnerable due to bad parameters ). 
This tool is relatively easy, as I created it to just run and only prompt the user for one thing while it runs: the new user it wants to create for the escalation. This tool only really requires basic python packages that I personally didn’t need to install when writing it (so most people should be able to make it run on a Linux system out of the box – great for competitions where time/access to download packages is important).


## Requirements
- **A Debian (or Linux) based system**
- **A User account with sudo privledes (or permissions to eddit /etc/passwd, /etc/shadow, and /etc/ssh/sshd**
- **Python 3**
- **OpenSSH Server/Client Installed**
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to verify the following packages (most should be installed by default):

```bash
pip install doctest
```
```bash
pip install genericpath
```
```bash
pip install socket
```
```bash
pip install subprocess
```
```bash
pip install os
```

Next you will need the required linux packages for ssh if they are not installed as well

```bash
apt-get update
apt-get install openssh-server
apt-get install openssh-client
```

Now you should be ready to run the script (if you do need permissions to run it, do chmod +x .../hw4.py)

## Usage
To start the script, run it with python3 either with sudo or not (you will be prompted later for user password)
(Ensure the account you are using has permissions to read/write, and sudo. This will be tested in the verification step but its important for it to successfully work)
```bash
/bin/python3 ../hw4.py
sudo /bin/python3 ../hw4.py
```
Once the script runs it will Initalize and preform a verification:
![img1](https://i.gyazo.com/3de175aff626150e558606c0a1f5c25c.png)
In this example, you can see the verification completed with success. The script will then start the main process and ask for a user account to use (or create):
![img2](https://i.gyazo.com/e3acad86071cc23ecd0c20d5026ce42a.png)
After we have entered a user, the system will go ahead and create the user, modify the shadow and passwd file of the user to remove the password and change the id, as well as modify the sshd config if needed:
![img3](https://i.gyazo.com/ef4c00f4475fa0c11ec006e253158bc4.png)
Once the new user has been set to root, a test connection to the systems ssh server is done to make sure the connection is possible and the user id and group id is correctly set and a shell is created where we can run what commands we want:
![img4](https://i.gyazo.com/6fa4af6c4c7b40978d0fa4ea5ec35c98.png)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
The main github link is here: https://github.com/kql5923/csec473-hw4-redtool
