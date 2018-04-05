#!/usr/bin/env python
# -*- coding: utf-8 -*-

# nftr.py

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

import struct

import gtk

class Decode:
    def __init__(self, _guess):
        if isinstance(_guess, str):
            self.file = open(_guess, 'rb')
        elif isinstance(_guess, file):
            self.file = _guess
        else:
            raise TypeError('expecting filename or file')

        self.read_header()

    def read_header(self):
        self.header = {'NFTR':{},'FINF':{},'CGLP':{},'CWDH':{},'CMAP':{}}
        self.file.seek(0, 0)
        # NFTR
        stamp = self.file.read(4)[::-1]
        if stamp == 'NFTR':
            self.file.read(4)
            self.header['NFTR'].update({'filesize':struct.unpack('<L', self.file.read(4))[0]})
            self.header['NFTR'].update({'size':struct.unpack('<H', self.file.read(2))[0]})
            self.header['NFTR'].update({'chunks':struct.unpack('<H', self.file.read(2))[0]})
        # FINF
        stamp = self.file.read(4)[::-1]
        if stamp == 'FINF':
            self.header['FINF'].update({'size':struct.unpack('<L', self.file.read(4))[0]})
            self.file.read(8) #??
            self.header['FINF'].update({'cglp':struct.unpack('<L', self.file.read(4))[0]})
            self.header['FINF'].update({'cwdh':struct.unpack('<L', self.file.read(4))[0]})
            self.header['FINF'].update({'cmap':struct.unpack('<L', self.file.read(4))[0]})


        self.file.seek(self.header['FINF']['cglp'] - 8, 0)
        stamp = self.file.read(4)[::-1]
        if stamp == 'CGLP':
            self.header['CGLP'].update({'size':struct.unpack('<L', self.file.read(4))[0]})
            self.header['CGLP'].update({'width':struct.unpack('B', self.file.read(1))[0]})
            self.header['CGLP'].update({'height':struct.unpack('B', self.file.read(1))[0]})
            self.header['CGLP'].update({'length':struct.unpack('<H', self.file.read(2))[0]})
            self.file.read(2)
            self.header['CGLP'].update({'bpp':struct.unpack('<H', self.file.read(2))[0]})
            self.header['CGLP'].update({'data':self.file.tell()})

        self.file.seek(self.header['FINF']['cwdh'] - 8, 0)
        stamp = self.file.read(4)[::-1]
        if stamp == 'CWDH':
            self.header['CWDH'].update({'size':struct.unpack('<L', self.file.read(4))[0]})
            self.header['CWDH'].update({'min':struct.unpack('<H', self.file.read(2))[0]})
            self.header['CWDH'].update({'max':struct.unpack('<H', self.file.read(2))[0]})
            self.file.read(4)
            self.header['CWDH'].update({'data':self.file.tell()})

        self.file.seek(self.header['FINF']['cmap'] - 8, 0)
        stamp = self.file.read(4)[::-1]
        if stamp == 'CMAP':
            self.header['CMAP'].update({'size':struct.unpack('<L', self.file.read(4))[0]})
            self.header['CMAP'].update({'min':struct.unpack('<H', self.file.read(2))[0]})
            self.header['CMAP'].update({'max':struct.unpack('<H', self.file.read(2))[0]})
            self.file.read(8)
            self.header['CMAP'].update({'data':self.file.tell()})

    def read_cglp(self):
        self.file.seek(self.header['CGLP']['data'], 0)
        shift= [7,6,5,4,3,2,1,0]

        font = []
        for x in range(self.header['CGLP']['size'] / self.header['CGLP']['length']):
            letter = []
            bitmap = []
            char = self.file.read(self.header['CGLP']['length'])
            # Bits
            for s in char:
                s = struct.unpack('B', s)[0]
                letter += [1 & (s >> i) for i in shift]
            # Separa em grupos de 9
            letter = zip(*[iter(letter)]* self.header['CGLP']['width'])
            for byte in letter:
                byte = list(byte)
                while len(byte) % 8 != 0:
                    byte.append(0)              
                bitmap += map(lambda x: x*255 , byte)
                # Separa em grupos de 8, para formar os bytes
                # group = zip(*[iter(byte)]*8)
                # lines = map(lambda e: reduce(lambda x,y:(x << 1) + y, reversed(e)), group)
                # for data in lines:
                    # bitmap += struct.pack('B',data)
            font.append(bitmap)
        return font

    def read_cmap(self):
        self.file.seek(self.header['CMAP']['data'], 0)
        charset = ''
        for map in range(self.header['CMAP']['min'], self.header['CMAP']['max'] + 1):
            index = struct.unpack('<H', self.file.read(2))[0]
            if index != 0xffff:
                charset += struct.pack('B', map)
        return charset

    def read_cwdh(self):
        ''' (Offset, Largura, Próximo Offset) '''
        self.file.seek(self.header['CWDH']['data'], 0)
        width_table = []
        for x in range(self.header['CWDH']['max']-self.header['CWDH']['min'] + 1):
            width_table.append((struct.unpack('B', self.file.read(1))[0],
                                struct.unpack('B', self.file.read(1))[0],
                                struct.unpack('B', self.file.read(1))[0]))
        return width_table






