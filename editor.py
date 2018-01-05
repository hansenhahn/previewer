#!/usr/bin/env python
# -*- coding: utf-8 -*-

# editor.py

# Copyright 2010 Diego Hansen Hahn (aka DiegoHH) <diegohh90 [at] hotmail [dot] com>

# RH-Editor is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.

# RH-Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with RH-Editor. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Diego Hansen Hahn"
__version__ = "v1.0.0"

import re
import os
import sys

import pygtk
pygtk.require('2.0')

import gtk
import pango

import dialogs
import drawer
import writer
from configobj import ConfigObj

fontDescription = 'monospace 10'

# MELHORAR O __init__ DA FUNÇÃO!!!

class Main:

    def __init__(self):
        if hasattr(sys, 'frozen'):
            self.local_path = os.path.realpath(os.path.dirname(sys.executable))
            sys.path.append(self.local_path)
        else:
            self.local_path = os.path.realpath(os.path.dirname(__file__))

        #self.__init_config()

        self.wtree_path = os.path.join(self.local_path, 'editor.ui')

        self.builder = gtk.Builder()
        self.builder.add_from_file(self.wtree_path)
        self.builder.connect_signals(self)

        self.main_window = self.builder.get_object('main_window')
        self.main_window.connect('delete-event', self.on_main_window_delete_event)
        self.main_window.connect('destroy', gtk.main_quit)

        self.treeview = self.builder.get_object('treeview')
        self.treeview.connect('row-activated', self.on_treeview_row_activated)


        self.main_window.show_all()

        self.main_box = self.builder.get_object('hbox1')
        self.main_box.hide()


        self.project_dialog = dialogs.ProjectDialog(self.builder, self.main_window)
        self.search_dialog = dialogs.SearchDialog(self.builder, self.main_window)

        self.file_list = self.builder.get_object('file_list')

        self.__load_config()

        self.main_box.show_all()

        self.teste = self.builder.get_object('viewport3')
        self.teste2 = self.builder.get_object('textview1')
        self.teste2.modify_font(pango.FontDescription(fontDescription))

        self.teste3 = self.builder.get_object('textview2')
        self.teste3.modify_font(pango.FontDescription(fontDescription))
        self.buf = self.teste3.get_buffer()

        self.panel_separator = self.builder.get_object("hpaned1")

        self.drawing_area = drawer.Drawer(self.config_files,
                                          bg = os.path.join(self.config_path, self.main_config['BackgroundFolder']),
                                          font = os.path.join(self.config_path, self.main_config['FontFolder']))


        self.writing_area = writer.Writer()

        self.teste2.set_buffer(self.writing_area)

        self.writing_area.connect('changed', self.on_writing_area_changed)
        self.writing_area.connect('mark-set', self.on_writing_area_mark_set)
        self.s_id_1 = self.writing_area.connect('modified-changed', self.on_writing_area_modified_changed)

        self.drawing_area.connect('expose-event', self.on_drawing_area_expose_event)
        self.drawing_area.show()

        self.teste.add(self.drawing_area)

        self.file_list_iter = []
        self.__init_file_list()

    def on_main_window_delete_event(self, widget, event):
        return False

    def on_hpaned1_expose_event(self, widget, event):
        alloc = widget.get_allocation()        
        widget.set_position(alloc.width/2)

    def __load_config(self):
        filename = self.project_dialog.run()
        filename = filename.encode('windows-1252')

        self.config_path, self.config_name = os.path.split(filename)

        self.config_files = []

        self.main_config = ConfigObj(filename, unrepr = True)

        path = os.path.join(self.config_path, self.main_config['ConfigFolder'])
        for file in os.listdir(path):
            self.config_files.append(ConfigObj(os.path.join(path, file), unrepr = True))


    def __init_file_list(self):
        path = os.path.join(self.config_path, self.main_config['TextFolder'])

        for file in os.listdir(path):
            iter = self.file_list.append([gtk.gdk.pixbuf_new_from_file('Pixmaps/text-x-generic.png'), file, None])
            self.file_list_iter.append(iter)

        if not self.file_list_iter:
            return

        self.file_stack = {}
        self.file_index = 0

        self.treeview.set_cursor(0, None, False)
        self.on_treeview_row_activated(self.treeview, self.file_index, None)


    def on_treeview_row_activated(self, treeview, path, collum):
        self.writing_area.disconnect(self.s_id_1)

        # Se houver um arquivo aberto, adicionar o buffer de texto dele no stack
        if hasattr(self, 'filename'):
            text = self.writing_area.get_text(self.writing_area.get_start_iter(),self.writing_area.get_end_iter())
            self.file_stack.update({self.filename:text})

        self.file_index = treeview.get_cursor()[0][0]
        path = os.path.join(self.config_path, self.main_config['TextFolder'])

        self.filename = os.path.join(path, os.listdir(path)[self.file_index])

        if self.filename in self.file_stack:
            text = self.file_stack[self.filename]
        else:
            file = open(self.filename, 'r')
            text = unicode(file.read().decode(self.main_config['Encoding']))
            file.close()

        self.writing_area.set_text(text)
        self.writing_area.set_modified(False)

        self.writing_area.clear_stacks()

        name = os.listdir(path)[self.file_index]

        path = os.path.join(self.config_path, self.main_config['OriginalFolder'])
        name = os.path.join(path, name)

        file = open(name, 'r')
        text = unicode(file.read().decode(self.main_config['Encoding']))
        file.close()

        self.buf.set_text(text)

        self.s_id_1 = self.writing_area.connect('modified-changed', self.on_writing_area_modified_changed)


    def on_writing_area_mark_set(self, buffer, iter, mark):
        if mark.get_name() == 'insert':
            self.drawing_area.refresh()


    def on_drawing_area_expose_event(self, widget, event):
        self.drawing_area.render_background()
        index = self.writing_area.get_text_init(self.main_config['Matches'])

        while True:
            line = self.writing_area.get_line(index)
            if not line:
                break # Se o índice for maior que o total de linhas do texto

            if line[0] in ('\r', '\n'):
                line = ' '

            for tag in self.main_config['Tags']:
                line = re.sub(tag, '', line)

            matches = [re.match(pattern, line) for pattern in self.main_config['Matches']]
            if any(matches):
                break #Se o padrão for encontrado, para de imprimir
            elif not self.drawing_area.render(line):
                break # Se não foi possível desenhar a linha
            else:
                index += 1
        # Reseta os valores x,y da área de desenho
        self.drawing_area.xpos = self.drawing_area.cfg_in_use['ScreenXPos']
        self.drawing_area.ypos = self.drawing_area.cfg_in_use['ScreenYPos']


    def on_writing_area_changed(self, buffer):
        self.drawing_area.refresh()


    def on_writing_area_modified_changed(self, buffer):
        if self.file_index != None and buffer.get_modified():
            iter = self.file_list_iter[self.file_index]
            self.file_list.set_value(iter, 2, gtk.gdk.pixbuf_new_from_file('Pixmaps/software-update-urgent.png'))

    def on_menu_save_activate(self, widget):
        if not hasattr(self, 'filename'):
            return

        text = self.writing_area.get_text(self.writing_area.get_start_iter(),self.writing_area.get_end_iter())

        file = open(self.filename, 'w')
        file.write(unicode(text).encode(self.main_config['Encoding']))
        file.close()

        iter = self.file_list_iter[self.file_index]
        self.file_list.set_value(iter, 2, None)

        pass

    def on_menu_find_activate(self, widget):
        self.search_dialog.run(self.teste2)

    def on_menu_undo_activate(self, widget):
        if self.writing_area.can_undo:
            self.writing_area.undo_event()


    def on_menu_redo_activate(self, widget):
        if self.writing_area.can_redo:
            self.writing_area.redo_event()

def Run():
    #import psyco
    #psyco.full()

    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    try:
        gtk.main()
    finally:
        gtk.gdk.threads_leave()

if __name__ == '__main__':
    Main()
    Run()

