SSH Menu
========

SSH Menu is a SSH menu plugin for Terminator v1.9 (ie GTK3 based versions) or later.

Install
-------

Installing SSH Menu is as simple as copying ssh_menu.py to ~/.config/terminator/plugins/ and reloading Terminator.

How to use it
-------------

After copying ssh_menu to your terminator plugins dir, you should have a new 'SSH menu' option within the Terminator context menu. Selecting this menu option will open the SSH Menu window. From here you can use the 'Configure' button to add new commands to SSH menu.

Whilst it is expected most people will use this plugin to store and launch ssh sessions via ssh commands, it can be used to store and run any shell command. Due to the lack of encryption, 2FA etc it would be recommended you do not use this plugin to store passwords or other sensitive data.

Note that you currently need to close and re-open the SSH Menu window before newly added commands are displayed and deleted commands get removed.
