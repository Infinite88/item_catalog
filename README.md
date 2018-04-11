#Item Catalog

## Section 0: INTRO
   The Item Catalog is an app where a user create, update, and delete categories and
   their items.

## Section 1: Requirements
VirtualBox:

VirtualBox is the software that actually runs the VM. You can download it from virtualbox.org, here. Install the platform package for your operating system.  You do not need the extension pack or the SDK.

Vagrant:

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  You can download it from vagrantup.com. Install the version for your operating system

Run the virtual machine!

Using the terminal, change directory to fullstack/vagrant (cd fullstack/vagrant), then type vagrant up to launch your virtual machine.

Once it is up and running, type vagrant ssh to log into it. This will log your terminal in to the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type exit at the shell prompt.  To turn the virtual machine off (without deleting anything), type vagrant halt. If you do this, you'll need to run vagrant up again before you can log into it. Be sure to change to the /vagrant directory by typing cd /vagrant in order to share files between your home machine and the VM.

## Section 2: Requirements:
Flask == 0.9
SQLAlchemy == 0.8.4
Requests == 2.7.0
dicttoxml == 1.6.6
httplib2 == 0.9.1

## Section 3: Installation:
to clone run command 'git clone https://github.com/Infinite88/Catalog_Item.git'

## Section 4: SET UP AND HOW TO RUN: 
1. Run the command 'vagrant up' from the /vagrant directory.
2. Run command 'vagrant ssh' and change directories by running 'cd /vagrant/catalog/'.
3. 'rm catalog.db' to remove current database
4. 'python projectdata.py' to create new database
5. Run the command 'python application.py'
6. Runs port 8000 so go to your favorite web browser and type in localhost:8000.
7. Enjoy!!!!! 