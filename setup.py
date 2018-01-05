#!/usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py

# Copyright 2009 Diego Hansen Hahn (aka DiegoHH) <diegohh90 [at] hotmail [dot] com>

# lazynds is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.

# lazynds is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with lazynds. If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import py2exe
import glob
import sys

opts = {
    'py2exe': {
        'includes': 'pango,atk,gobject,cairo,pangocairo,gio,gtk.keysyms,encodings,encodings.*',
        'dll_excludes': [
            'iconv.dll','intl.dll','libatk-1.0-0.dll',
            'libgdk_pixbuf-2.0-0.dll','libgdk-win32-2.0-0.dll',
            'libglib-2.0-0.dll','libgmodule-2.0-0.dll',
            'libgobject-2.0-0.dll','libgthread-2.0-0.dll',
            'libgtk-win32-2.0-0.dll',
			'libpango-1.0-0.dll',
            'libpangowin32-1.0-0.dll','libcairo-2.dll',
            'libpangocairo-1.0-0.dll','libpangoft2-1.0-0.dll',
			'zlib1.dll',  'libxml2.dll',
        ],
        'dist_dir': 'editor',
        'optimize': 2,
        'compressed': True,
		'bundle_files': 3,
    }
}

setup(
    name = 'editor',
    version = '1.0.0',
    description = u'Visualizador de Textos'.encode('windows-1252'),
    author = 'Diego Hansen Hahn',
    author_email = 'diegohh90@hotmail.com',
    license = 'GPL',

    windows = [{'script': 'editor.py'}],
                # 'icon_resources': [(1, 'lazyicon.ico')]}],
    options=opts,
	zipfile = 'editor.lib',
	package_dir={"" : "."},

    data_files=[('Pixmaps', glob.glob('Pixmaps/*.*')),
                ('MyProjects', glob.glob('MyProjects/*.*')),
				('', ['editor.ui'])	],
)
