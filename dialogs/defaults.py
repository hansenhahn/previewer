'''
Created on 27/06/2010

@author: Hansen
'''

import gtk

def FileChooser(window, folder, mode):
    if mode == 'save':
        title = 'Salvar arquivo...'
        action = gtk.FILE_CHOOSER_ACTION_SAVE
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)
    else:
        title = 'Abrir Arquivo...'
        action = gtk.FILE_CHOOSER_ACTION_OPEN
        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)

    chooser = gtk.FileChooserDialog(title = title,
                                    parent = window,
                                    action = action,
                                    buttons = buttons)

    chooser.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    chooser.set_do_overwrite_confirmation(True)

    chooser.set_current_folder(folder)

    filename = None

    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        filename = chooser.get_filename()
    chooser.destroy()

    return filename

