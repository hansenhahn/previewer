'''
Created on 27/06/2010

@author: Hansen
'''

from gi.repository import Gtk

def FileChooser(window, folder, mode):
    if mode == 'save':
        title = 'Salvar arquivo...'
        action = Gtk.FileChooserAction.SAVE
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
    else:
        title = 'Abrir Arquivo...'
        action = Gtk.FileChooserAction.OPEN
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

    chooser = Gtk.FileChooserDialog(title = title,
                                    parent = window,
                                    action = action,
                                    buttons = buttons)

    chooser.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
    chooser.set_do_overwrite_confirmation(True)

    chooser.set_current_folder(folder)

    filename = None

    response = chooser.run()
    if response == Gtk.ResponseType.OK:
        filename = chooser.get_filename()
    chooser.destroy()

    return filename

