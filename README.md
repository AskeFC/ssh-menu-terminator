SSH Menu
========

SSH Menu is a SSH menu plugin for Terminator v1.9 (ie GTK3 based versions) or later.

Installation
------------

Installing SSH Menu is as simple as copying ssh_menu.py to ~/.config/terminator/plugins/ and then enabling it under Terminator's Plugins tab, under Preferences.

How to use it
-------------

Following installation, you should have a new 'SSH menu' option within the Terminator context (right click) menu. Selecting this menu option will open the SSH Menu window. From here you can use the 'Configure' button to add new commands to SSH menu.

Whilst it is expected most people will use this plugin to store and launch ssh sessions via ssh commands, it can be used to store and run any shell command. Due to the lack of encryption, it is recommended you do not use this plugin to store passwords or other sensitive data.

Note that you currently need to close and re-open the SSH Menu window before newly added commands are displayed and deleted commands get removed.

Development
-----------

If you want to debug or help develop this plugin, start Terminator from any non-Terminator terminal emulator with the command:

```
terminator -dd --debug-classes SSHMenu
```
 
Like terminator, this plugin was created with Python 2 and GTK 3.
