#!/usr/bin/python
# Terminator by Chris Jones, Stephen Boddy et al
# GPL v2 only
# ssh_menu.py - Terminator plugin to add an SSH / command menu
#
# Original version by Mario Lameiras, 2014
# GTK3 port by Dan MacDonald, 2017
# menu extension by Hans Matzen (tuxlogger), 2019

import sys
import os

# Fix imports when testing this file directly
if __name__ == '__main__':
  sys.path.append( os.path.join(os.path.dirname(__file__), "../.."))

from gi.repository import Gtk
import terminatorlib.plugin as plugin
from terminatorlib.config import Config
from terminatorlib.translation import _
from terminatorlib.util import get_config_dir

(CC_COL_NAME, CC_COL_COMMAND, CC_COL_GROUP) = range(0,3)

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['SSHMenu']

class SSHMenu(plugin.MenuItem):
    """SSH Menu"""
    capabilities = ['terminal_menu']
    cmd_list = []
    conf_file = os.path.join(get_config_dir(),"ssh_menu")

    def __init__( self):
      config = Config()
      sections = config.plugin_get_config(self.__class__.__name__)
      if not isinstance(sections, dict):
          return
      for part in sections:
        s = sections[part]
        if not (s.__contains__("name") and s.__contains__("command")):
          print "SSHMenu: Ignoring section {s}"
          continue
        name = s["name"]
        command = s["command"]
        group = s["group"]
        self.cmd_list.append(
	      { 'name' : name,
		'command' : command,
		'group' : group
	      }
	    )

    def callback(self, menuitems, menu, terminal):
	"""Add our menu items to the menu"""
	item = Gtk.MenuItem(_('SSH Menu'))
	item.connect("activate", self.menu, terminal)
	menuitems.append(item)

	#  submenu = Gtk.Menu()
	#  item.set_submenu(submenu)

	#  menuitem = Gtk.ImageMenuItem(Gtk.STOCK_PREFERENCES)
	#  menuitem.connect("activate", self.configure)
	#  submenu.append(menuitem)
	#
	# added context menu entry opening treelike using submenus 
	# 2019-09-22 by tuxlog
	#
	# open new tab
	allgroups = []
	groupnum = len(self.cmd_list)
	for elem in range(groupnum):
		allgroups.append(self.cmd_list[elem]['group'])
	groups = list(set(allgroups))

	sshmenu1 = Gtk.Menu()
	sshsubmenu1 = Gtk.MenuItem("SSH Hosts")
	sshsubmenu1.set_submenu(sshmenu1)

	for group in groups:
		sshmenu2 = Gtk.Menu()
		sshsubmenu2 = Gtk.MenuItem(group)
		sshsubmenu2.set_submenu(sshmenu2)
		sshmenu1.append(sshsubmenu2)

		subgroup = [d for d in self.cmd_list if d['group'] == group]
		for command in subgroup:
			sshsubmenu3 = Gtk.MenuItem( command['name'] )
			sshsubmenu3.connect("activate", self._execute_from_menu, terminal, command['command'] )
			sshmenu2.append( sshsubmenu3 )

	menuitems.append(sshsubmenu1)

    def _save_config(self):
      config = Config()
      config.plugin_del_config(self.__class__.__name__)
      config.save()
      i = 0
      length = len(self.cmd_list)
      while i < length:
        name = self.cmd_list[i]['name']
        command = self.cmd_list[i]['command']
        group = self.cmd_list[i]['group']

        item = {}
        item['name'] = name
        item['command'] = command
        item['group'] = group

        config.plugin_set(self.__class__.__name__, name, item)
        config.save()
        i = i + 1

    #def _save_order(self,selection, data):
     # print "todo!"

    def _execute(self, treeview, path, view_column, data):
      (model, iter) = data['selection'].get_selected()
      command = model.get_value(iter,1)
      if command[len(command)-1] != '\n':
        command = command + '\n'

      #
      # changed to open a new tab on every execution
      # 2019-09-22 by tuxlog
      #
      # open new tab
      data['terminal'].get_toplevel().tab_new()
      # get focussed terminal
      focterm=data['terminal'].get_toplevel().get_focussed_terminal()
      # send command to focussed terminal
      focterm.vte.feed_child(command.encode('utf-8'))

    def menu(self, widget, terminal, data = None):
      ui = {}

      window = Gtk.Window()
      scroll = Gtk.ScrolledWindow(None, None)
      scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
      #scroll.set_border_width(1)

      window.set_title("SSH Menu")
      window.move(1,100)
      window.resize(200,500)
      window.set_resizable(True)
      #window. set_decorated(False)
      # Create a new button
      buttonsbox = Gtk.HBox(False, 0)
      box1 = Gtk.VBox(False, 0)

      button = Gtk.Button("Close", Gtk.STOCK_CLOSE)
      button.connect_object("clicked", Gtk.Widget.destroy, window)

      buttonPreferences = Gtk.Button("Configure", Gtk.STOCK_PREFERENCES)
      buttonPreferences.connect("clicked", self.configure)

      buttonsbox.pack_start(button, True, False, 0)
      buttonsbox.pack_end(buttonPreferences, True, False, 0)
      box1.pack_start(buttonsbox, False, False, 0)

      allgroups = []
      groupnum = len(self.cmd_list)
      for elem in range(groupnum):
        allgroups.append(self.cmd_list[elem]['group'])
      groups = list(set(allgroups))

      store = Gtk.TreeStore(str,str,str)

      for group in groups:
        rabbit = store.append(None, [group,"blah","blah"])
        subgroup = [d for d in self.cmd_list if d['group'] == group]
        for command in subgroup:
          store.append(rabbit,[command['name'], command['command'], command['group']])

      treeview = Gtk.TreeView(store)
      selection = treeview.get_selection()
      selection.set_mode(Gtk.SelectionMode.SINGLE)

      #selection.connect("changed", self._save_order, {'terminal' : terminal, 'selection' : selection })
      treeview.connect("row-activated", self._execute, {'terminal' : terminal, 'selection' : selection })
      ui['treeview'] = treeview

      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Groups", renderer, text=CC_COL_NAME)

      treeview.append_column(column)

      treeview.set_reorderable(True)
      treeview.set_enable_search(True)
      # expand all nodes to get quicker, HM, 29.09.2019
      treeview.expand_all()

      hbox = Gtk.HBox()
      hbox.pack_start(treeview, True, True, 0)

      outbox = Gtk.VBox(False, 0)

      inbox = Gtk.VBox(False, 0)
      inbox.pack_start(scroll, True, True, 5)
      inbox.pack_start(box1,False, False, 8)

      scroll.add_with_viewport(hbox)
      scroll.show()
      outbox.pack_start(inbox, True, True, 0)
      window.add(outbox)
      window.show_all()
      return

    def configure(self, widget, data = None):
      ui = {}
      window = Gtk.Dialog(
	      _("SSH Menu Configuration"),
	      None,
	      Gtk.DialogFlags.MODAL,
	      (
		Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
		Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT
	      )
	    )
      store = Gtk.ListStore(str, str, str)

      for command in self.cmd_list:
        store.append([command['name'], command['command'], command['group']])

      treeview = Gtk.TreeView(store)
      #treeview.connect("cursor-changed", self.on_cursor_changed, ui)
      selection = treeview.get_selection()
      selection.set_mode(Gtk.SelectionMode.SINGLE)
      selection.connect("changed", self.on_selection_changed, ui)
      ui['treeview'] = treeview

      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Name", renderer, text=CC_COL_NAME)
      treeview.append_column(column)

      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Command", renderer, text=CC_COL_COMMAND)
      treeview.append_column(column)

      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn("Group", renderer, text=CC_COL_GROUP)
      treeview.append_column(column)

      hbox = Gtk.HBox()
      hbox.pack_start(treeview, True, True, 0)
      window.vbox.pack_start(hbox, True, True, 0)

      button_box = Gtk.VBox()

      button = Gtk.Button(stock=Gtk.STOCK_GOTO_TOP)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_goto_top, ui)
      button.set_sensitive(False)
      ui['button_top'] = button

      button = Gtk.Button(stock=Gtk.STOCK_GO_UP)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_go_up, ui)
      button.set_sensitive(False)
      ui['button_up'] = button

      button = Gtk.Button(stock=Gtk.STOCK_GO_DOWN)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_go_down, ui)
      button.set_sensitive(False)
      ui['button_down'] = button

      button = Gtk.Button(stock=Gtk.STOCK_GOTO_LAST)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_goto_last, ui)
      button.set_sensitive(False)
      ui['button_last'] = button

      button = Gtk.Button(stock=Gtk.STOCK_NEW)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_new, ui)
      ui['button_new'] = button

      button = Gtk.Button(stock=Gtk.STOCK_EDIT)
      button_box.pack_start(button, False, True, 0)
      button.set_sensitive(False)
      button.connect("clicked", self.on_edit, ui)
      ui['button_edit'] = button

      button = Gtk.Button(stock=Gtk.STOCK_DELETE)
      button_box.pack_start(button, False, True, 0)
      button.connect("clicked", self.on_delete, ui)
      button.set_sensitive(False)
      ui['button_delete'] = button

      hbox.pack_start(button_box, True, True, 0)
      window.show_all()
      res = window.run()
      if res == Gtk.ResponseType.ACCEPT:
        #we save the config
        iter = store.get_iter_first()
        self.cmd_list = []
        while iter:
          (name, command, group) = store.get(iter,
	      CC_COL_NAME,
	      CC_COL_COMMAND,
	      CC_COL_GROUP)
          self.cmd_list.append(
		    {'name': name,
		    'command' : command,
		    'group' : group}
	  	)
          iter = store.iter_next(iter)
        self._save_config()

      window.destroy()
      return

    def on_selection_changed(self,selection, data=None):
      treeview = selection.get_tree_view()
      (model, iter) = selection.get_selected()
      data['button_top'].set_sensitive(iter is not None)
      data['button_up'].set_sensitive(iter is not None)
      data['button_down'].set_sensitive(iter is not None)
      data['button_last'].set_sensitive(iter is not None)
      data['button_edit'].set_sensitive(iter is not None)
      data['button_delete'].set_sensitive(iter is not None)

    def _create_command_dialog(self, name_var = "", command_var = "", group_var = ""):
      dialog = Gtk.Dialog(
		_("New Command"),
		None,
		Gtk.DialogFlags.MODAL,
		(
		  Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
		  Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT
		)
      	)
      table = Gtk.Table(3, 2)

      label = Gtk.Label(label=_("Name:"))
      table.attach(label, 0, 1, 1, 2)
      name = Gtk.Entry()
      name.set_text(name_var)
      table.attach(name, 1, 2, 1, 2)

      label = Gtk.Label(label=_("Command:"))
      table.attach(label, 0, 1, 2, 3)
      command = Gtk.Entry()
      command.set_text(command_var)
      table.attach(command, 1, 2, 2, 3)

      label = Gtk.Label(label=_("Group:"))
      table.attach(label, 0, 1, 3, 4)
      group = Gtk.Entry()
      group.set_text(group_var)
      table.attach(group, 1, 2, 3, 4)

      dialog.vbox.pack_start(table, True, True, 0)
      dialog.show_all()
      return (dialog,name,command,group)

    def _error(self, msg):
      err = Gtk.MessageDialog(dialog,
	      Gtk.DialogFlags.MODAL,
	      Gtk.MessageType.ERROR,
	      Gtk.ButtonsType.CLOSE,
	      msg
	    )
      err.run()
      err.destroy()

    def on_new(self, button, data):
      (dialog,name,command,group) = self._create_command_dialog()
      res = dialog.run()
      item = {}
      if res == Gtk.ResponseType.ACCEPT:
        item['name'] = name.get_text()
        item['command'] = command.get_text()
        item['group'] = group.get_text()
        if item['name'] == '' or item['command'] == '' or item['group'] == '':
          err = Gtk.MessageDialog(dialog,
		  Gtk.DialogFlags.MODAL,
		  Gtk.MessageType.ERROR,
		  Gtk.ButtonsType.CLOSE,
		  _("You need to define a name, command and group")
		)
          err.run()
          err.destroy()
        else:
          # we have a new command
          store = data['treeview'].get_model()
          iter = store.get_iter_first()
          name_exist = False
          while iter != None:
            if store.get_value(iter,CC_COL_NAME) == item['name']:
              name_exist = True
              break
            iter = store.iter_next(iter)
          if not name_exist:
            store.append((item['name'], item['command'], item['group']))
          else:
            self._err(_("Name *%s* already exist") % item['name'])
      dialog.destroy()

    def on_goto_top(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()

      if not iter:
        return
      firstiter = store.get_iter_first()
      store.move_before(iter, firstiter)

    def on_go_up(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()

      if not iter:
        return

      tmpiter = store.get_iter_first()

      if(store.get_path(tmpiter) == store.get_path(iter)):
        return

      while tmpiter:
        next = store.iter_next(tmpiter)
        if(store.get_path(next) == store.get_path(iter)):
          store.swap(iter, tmpiter)
          break
        tmpiter = next

    def on_go_down(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()

      if not iter:
        return
      next = store.iter_next(iter)
      if next:
        store.swap(iter, next)

    def on_goto_last(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()

      if not iter:
        return
      lastiter = iter
      tmpiter = store.get_iter_first()
      while tmpiter:
        lastiter = tmpiter
        tmpiter = store.iter_next(tmpiter)

      store.move_after(iter, lastiter)

    def on_delete(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()
      if iter:
        store.remove(iter)
      return

    def on_edit(self, button, data):
      treeview = data['treeview']
      selection = treeview.get_selection()
      (store, iter) = selection.get_selected()

      if not iter:
        return

      (dialog,name,command,group) = self._create_command_dialog(
		name_var = store.get_value(iter, CC_COL_NAME),
		command_var = store.get_value(iter, CC_COL_COMMAND),
		group_var = store.get_value(iter, CC_COL_GROUP)
	  )
      res = dialog.run()
      item = {}
      if res == Gtk.ResponseType.ACCEPT:
        item['name'] = name.get_text()
        item['command'] = command.get_text()
        item['group'] = group.get_text()
        if item['name'] == '' or item['command'] == '' or item['group'] == '':
          err = Gtk.MessageDialog(dialog,
		  Gtk.DialogFlags.MODAL,
		  Gtk.MessageType.ERROR,
		  Gtk.ButtonsType.CLOSE,
		  _("You need to define a name, command and group")
		)
          err.run()
          err.destroy()
        else:
          tmpiter = store.get_iter_first()
          name_exist = False
          while tmpiter != None:
            if store.get_path(tmpiter) != store.get_path(iter) and store.get_value(tmpiter,CC_COL_NAME) == item['name']:
              name_exist = True
              break
            tmpiter = store.iter_next(tmpiter)
          if not name_exist:
            store.set(iter,
                      CC_COL_NAME, item['name'],
                      CC_COL_COMMAND, item['command'],
                      CC_COL_GROUP, item['group']
                      )
          else:
            self._err(_("Name *%s* already exist") % item['name'])

      dialog.destroy()

    def _execute_from_menu(self, widget, terminal, command):
	if command[len(command)-1] != '\n':
		command = command + '\n'

	# open new tab
	terminal.get_toplevel().tab_new()
	# get focussed terminal
	focterm=terminal.get_toplevel().get_focussed_terminal()
	# send command to focussed terminal
	focterm.vte.feed_child(command.encode('utf-8'))

if __name__ == '__main__':
  c = SSHMenu()
  c.configure(None, None)
  Gtk.main()
