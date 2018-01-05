#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dialogs/search.py

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

import gtk

import defaults

FIND_ACTION = -1

class SearchDialog:
    def __init__(self, builder, parent):
        self.builder = builder

        self.dialog = self.builder.get_object("search_dialog")
        self.dialog.set_transient_for(parent)
        self.parent = parent

        self.entry_box = self.builder.get_object("entry_box")

    def run(self, textview):
        while True:
            if self.dialog.run() == FIND_ACTION:
                self.forward_search(textview, self.entry_box.get_text())
            else:
                self.dialog.hide()
                return False
		
    def forward_search(self, textview, word):
        try:
            textbuffer = textview.get_buffer()
            last_pos = textbuffer.get_mark('pos_end')
            if last_pos:
                start = textbuffer.get_iter_at_mark(last_pos)

                first, last = start.forward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
                if first:
                    mark  = textbuffer.create_mark('pos_end', last, False)
                    mark2 = textbuffer.create_mark('pos_beg', first, False)

                    textview.scroll_mark_onscreen(mark)
                    textbuffer.select_range(first, last)
            else:		
                bounds = textbuffer.get_selection_bounds()

                if bounds:
	                start, end = bounds
                else:
	                start = textbuffer.get_start_iter()

                first, last = start.forward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)

                if first:
                    mark  = textbuffer.create_mark('pos_end', last, False)
                    mark2 = textbuffer.create_mark('pos_beg', first, False)

                    textview.scroll_mark_onscreen(mark)
                    textbuffer.select_range(first, last)
        except:
            return
