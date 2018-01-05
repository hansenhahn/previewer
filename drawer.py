#!/usr/bin/env python
# -*- coding: utf-8 -*-

# drawer.py

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

from math import ceil
import os

import gtk

import nftr

small_font = 'Fontes/fontq.NFTR'
normal_font = 'Fontes/fontevent.NFTR'

warning = 'Pixmaps/dialog-warning.png'

LEFT_BUTTON = 1
RIGHT_BUTTON = 3

class Drawer(gtk.DrawingArea):
    __gsignals__ = {'realize': 'override',
                    'button-press-event' : 'override'}

    def __init__(self, cfg, **paths):
        gtk.DrawingArea.__init__(self)

        self.cfg_file = cfg
        self.paths = paths

        self.__set_cfg()
        self.__set_settings()


    def __set_cfg(self):
        # Começa gerando o menu
        self.context_menu = gtk.Menu()
        self.context_menu.set_title('Fundos de Tela')
        for id, cfg in enumerate(self.cfg_file):
            menu_item = gtk.MenuItem(cfg['ScreenName'])
            menu_item.connect('activate', self.on_menu_item_activate, id)
            self.context_menu.append(menu_item)
        self.context_menu.show_all()

        # Seta a configuração inicial
        self.cfg_in_use = self.cfg_file[0]


    def __set_settings(self):
        self.background_file = os.path.join(self.paths['bg'], self.cfg_in_use['ScreenBackground'])
        self.font_file = os.path.join(self.paths['font'], self.cfg_in_use['ScreenFont'])
        self.xpos = self.cfg_in_use['ScreenXPos']
        self.ypos = self.cfg_in_use['ScreenYPos']
        self.newline = self.cfg_in_use['ScreenNewLine']

        self.font_specs = nftr.Decode(self.font_file)

        self.font_cmap = self.font_specs.read_cmap()
        self.font_cwdh = self.font_specs.read_cwdh()
        self.font_cglp = self.font_specs.read_cglp()

        self.font_width = self.font_specs.header['CGLP']['width']
        self.font_height = self.font_specs.header['CGLP']['height']

        self.___generate_bitmask()

    def ___generate_bitmask(self):
        uknown = '\xff' * int(ceil(float(self.font_width)/8.0)) * self.font_height

        self.font_masks = [gtk.gdk.bitmap_create_from_data(self.window, mask, self.font_width, self.font_height) for mask in self.font_cglp]
        self.font_uknown = gtk.gdk.bitmap_create_from_data(self.window, uknown, self.font_width, self.font_height)


    def render_background(self):
        self.gc = gtk.gdk.GC(self.window)
        self.window.draw_pixbuf(self.gc, gtk.gdk.pixbuf_new_from_file(self.background_file), 0, 0, 0, 0, -1, -1)


    def render(self, line):
        if self.ypos > 192: # Limite vertical atigindo
            self.gc = gtk.gdk.GC(self.window)
            self.window.draw_pixbuf(self.gc, gtk.gdk.pixbuf_new_from_file(warning), 0, 0, 5, 5, -1, -1)
            return False

        gc = gtk.gdk.GC(self.window)

        for x in unicode(line.strip('\r\n')).encode('windows-1252'):
            if x in self.font_cmap:
                index = self.font_cmap.index(x)
                mask = self.font_masks[index]
                parameters = self.font_cwdh[index]
            else:
                mask = self.font_uknown
                parameters = (0, 0, self.font_width)

            gc.set_clip_origin(self.xpos + parameters[0], self.ypos)
            gc.set_clip_mask(mask)
            gc.set_rgb_fg_color(gtk.gdk.Color(0, 0, 0))
            self.window.draw_rectangle(gc, True, self.xpos + parameters[0], self.ypos, self.font_width, self.font_height)
            self.xpos += parameters[2] + 1

            if self.xpos > 256:
                gc = gtk.gdk.GC(self.window)
                self.window.draw_pixbuf(gc, gtk.gdk.pixbuf_new_from_file(warning), 0, 0, 5, 5, -1, -1)
                break

        self.xpos = self.cfg_in_use['ScreenXPos']
        self.ypos += self.newline
        return True


    def on_menu_item_activate(self, widget, id):
        self.cfg_in_use = self.cfg_file[id]
        self.__set_settings()

        self.refresh()


    def do_button_press_event(self, event):
        if event.button == RIGHT_BUTTON:
            self.context_menu.popup(None, None, None, event.button, event.time)
            return True
        return False


    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)

        events = gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK

        self.window = gtk.gdk.Window(self.get_parent_window(),
                         x = self.allocation.x,
                         y = self.allocation.y,
                         width = self.allocation.width,
                         height = self.allocation.height,
                         window_type = gtk.gdk.WINDOW_CHILD,
                         wclass = gtk.gdk.INPUT_OUTPUT,
                         visual = self.get_visual(),
                         colormap = self.get_colormap(),
                         event_mask = self.get_events() | events)
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)


    def refresh(self):
        alloc = self.get_allocation()
        rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
        self.window.invalidate_rect(rect, True)
        self.window.process_updates(True)
        return False
