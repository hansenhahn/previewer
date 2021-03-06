#!/usr/bin/env python
# -*- coding: utf-8 -*-

# dialogs/project.py

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

import defaults

NEW_PROJECT = -1
LOAD_PROJECT = -2

class ProjectDialog:
    def __init__(self, builder, parent):
        self.builder = builder

        self.dialog = self.builder.get_object('project_dialog')
        self.dialog.set_transient_for(parent)
        self.parent = parent

    def run(self):

        response = self.dialog.run()
        if response == LOAD_PROJECT:
            self.dialog.hide()
            filename = defaults.FileChooser(self.parent, 'MyProjects', 'open')
        elif response == NEW_PROJECT:
            pass
        else:
            filename = None

        return filename



