import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Alert(object):
    def __init__(self, message, window):
        d = Gtk.Dialog(
            title="Alert",
            parent=window,
            flags=1,
            buttons=("Ok", Gtk.ResponseType.CANCEL)
        )
        label = Gtk.Label(message)
        label.set_padding(40, 30)
        d.vbox.add(label)
        d.show_all()
        d.run()
        d.destroy()
