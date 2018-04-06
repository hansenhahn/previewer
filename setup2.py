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
import sys, os, site, shutil

site_dir = site.getsitepackages()[1] 
include_dll_path = os.path.join(site_dir, "gnome") 
  
gtk_dirs_to_include = ['etc', 'lib\\gtk-3.0', 'lib\\girepository-1.0', 'lib\\gio', 'lib\\gdk-pixbuf-2.0', 'share\\glib-2.0', 'share\\fonts', 'share\\icons', 'share\\themes\\Default', 'share\\themes\\HighContrast'] 

gtk_dlls = [] 
tmp_dlls = [] 
cdir = os.getcwd() 
for dll in os.listdir(include_dll_path): 
    if dll.lower().endswith('.dll'): 
        gtk_dlls.append(os.path.join(include_dll_path, dll)) 
        tmp_dlls.append(os.path.join(cdir, dll)) 

for dll in gtk_dlls: 
    shutil.copy(dll, cdir)         
        
opts = {
    'py2exe': {
        'includes': ['gi'],
        'packages': ['gi'],
        'dist_dir': 'editor',
        'optimize': 2,
        'compressed': True,
		'bundle_files': 3,
        'dll_excludes': [
            'libgstreamer-1.0-0.dll','api-ms-win-core-libraryloader-l1-2-0.dll']   ,             
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

dest_dir = os.path.join(cdir, 'editor') 
for dll in tmp_dlls: 
    shutil.copy(dll, dest_dir) 
    os.remove(dll) 
  
for d  in gtk_dirs_to_include: 
    shutil.copytree(os.path.join(site_dir, "gnome", d), os.path.join(dest_dir, d))