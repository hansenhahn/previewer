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

import collections
import re

from gi.repository import Gtk, Gdk, GObject

WHITESPACE = (' ', '\t')

class Writer(Gtk.TextBuffer):

    maxlen = 50

    @property
    def can_undo(self):
        return bool(self.sec_stack)

    @property
    def can_redo(self):
        return bool(self.fst_stack)

    def __init__(self):
        Gtk.TextBuffer.__init__(self)

        self.connect('insert-text', self.on_insert_text)
        self.connect('delete-range', self.on_delete_range)

        self.fst_stack = collections.deque(maxlen = Writer.maxlen)
        self.sec_stack = collections.deque(maxlen = Writer.maxlen)

        self.not_undoable_action = True

    def get_line(self, index):
        if index > (self.get_line_count() - 1):
            return False

        start = self.get_iter_at_line(index)
        end = start.copy()
        end.forward_to_line_end()
        return self.get_text(start, end, True)

    def get_text_init(self, matches):
        ''' Procura por uma linha que coincida com os padrões informados pelo usuário.
        Essa linha será o pivô do bloco (a partir da onde o texto será lido.'''

        iter = self.get_iter_at_mark(self.get_insert())
        index = iter.get_line() #Indice da linha atual no buffer

        while index >= 0: # Caso extremo, não ter um pivô no arquivo. O Texto é lido a partir do começo
            line = self.get_line(index).strip('\r\n')
            if any([re.match(pattern, line) for pattern in matches]):
                break
            index -= 1
        return (index + 1)

    def get_stats(self):
        iter = self.get_iter_at_mark(self.get_insert())
        index = iter.get_line() #Indice da linha atual no buffer
        return index

    def on_insert_text(self, buffer, iter, text, lenght):
        def can_be_merged(previous, current):
            if not current.mergeable or not previous.mergeable:
                return False
            elif current.offset != (previous.offset + previous.lenght):
                return False
            elif current.text in WHITESPACE and not previous.text in WHITESPACE:
                return False
            elif previous.text in WHITESPACE and not current.text in WHITESPACE:
                return False
            else:
                return True

        if not self.not_undoable_action:
            return
        # Quando um novo texto é adicionado ao sec_stack, o fst_stack deve ser reiniciado
        self.fst_stack = collections.deque(maxlen = Writer.maxlen)

        current_insert = UndoableInsert(iter, text, lenght)
        if len(self.sec_stack) != 0:
            previous_insert = self.sec_stack.pop()
        else:
            self.sec_stack.append(current_insert)
            return

        if not isinstance(previous_insert, UndoableInsert):
            self.sec_stack.append(previous_insert)
            self.sec_stack.append(current_insert)
            return

        if can_be_merged(previous_insert, current_insert):
            previous_insert.lenght += current_insert.lenght
            previous_insert.text += current_insert.text
            self.sec_stack.append(previous_insert)
        else:
            self.sec_stack.append(previous_insert)
            self.sec_stack.append(current_insert)

    def on_delete_range(self, buffer, start, end):
        def can_be_merged(previous, current):
            if not current.mergeable or not previous.mergeable:
                return False
            elif previous.delete_key_used != current.delete_key_used:
                return False
            elif previous.start != current.start and previous.start != current.end:
                return False
            elif current.text not in WHITESPACE and previous.text in WHITESPACE:
                return False
            elif current.text in WHITESPACE and previous.text not in WHITESPACE:
                return False
            else:
                return True

        if not self.not_undoable_action:
            return

        self.fst_stack = collections.deque(maxlen = Writer.maxlen)
        current_delete = UndoableDelete(buffer, start, end)
        if len(self.sec_stack) != 0:
            previous_delete = self.sec_stack.pop()
        else:
            self.sec_stack.append(current_delete)
            return

        if not isinstance(previous_delete, UndoableDelete):
            self.sec_stack.append(previous_delete)
            self.sec_stack.append(current_delete)
            return

        if can_be_merged(previous_delete, current_delete):
            if previous_delete.start == current_delete.start:
                previous_delete.text += current_delete.text
                previous_delete.end += current_delete.end - current_delete.start
            else:
                previous_delete.text = '%s%s' % (current_delete.text, previous_delete.text)
                previous_delete.start = current_delete.start
            self.sec_stack.append(previous_delete)
        else:
            self.sec_stack.append(previous_delete)
            self.sec_stack.append(current_delete)

    def clear_stacks(self):
        self.fst_stack = collections.deque(maxlen = Writer.maxlen)
        self.sec_stack = collections.deque(maxlen = Writer.maxlen)

    def undo_event(self):
        self.not_undoable_action = False

        action = self.sec_stack.pop()
        self.fst_stack.append(action)

        if isinstance(action, UndoableInsert):
            start = self.get_iter_at_offset(action.offset)
            end = self.get_iter_at_offset(action.offset + action.lenght)
            self.delete(start, end)
            self.place_cursor(start)
        else:
            start = self.get_iter_at_offset(action.start)
            end = self.get_iter_at_offset(action.end)
            self.insert(start, action.text)
            if action.delete_key_used:
                self.place_cursor(start)
            else:
                self.place_cursor(start)

        self.not_undoable_action = True

    def redo_event(self):
        self.not_undoable_action = False

        action = self.fst_stack.pop()
        self.sec_stack.append(action)

        if isinstance(action, UndoableInsert):
            start = self.get_iter_at_offset(action.offset)
            self.insert(start, action.text)
            cursor_pos = self.get_iter_at_offset(action.offset + action.lenght)
            self.place_cursor(cursor_pos)
        else:
            start = self.get_iter_at_offset(action.start)
            end = self.get_iter_at_offset(action.end)
            self.delete(start, end)
            self.place_cursor(start)

        self.not_undoable_action = True


class UndoableInsert(object):
    def __init__(self, iter, text, lenght):
        self.offset = iter.get_offset()
        self.text = text
        self.lenght = lenght
        if self.lenght > 1 or self.text in ('\r', '\n', ' '):
            self.mergeable = False
        else:
            self.mergeable = True

class UndoableDelete(object):
    def __init__(self, buffer, start_iter, end_iter):
        self.text = buffer.get_text(start_iter, end_iter, True)
        self.start = start_iter.get_offset()
        self.end = end_iter.get_offset()
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        if insert_iter.get_offset() <= self.start:
            self.delete_key_used = True
        else:
            self.delete_key_used = False

        if self.end - self.start > 1 or self.text in ('\r', '\n', ' '):
            self.mergeable = False
        else:
            self.mergeable = True
