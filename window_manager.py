import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class WindowManager(object):
    windows = []

    @staticmethod
    def remove(window):
        WindowManager.windows.remove(window)

        if len(WindowManager.windows) == 0:
            Gtk.main_quit()

    @staticmethod
    def on_delete(window, event):
        WindowManager.remove(window)

    @staticmethod
    def add_window(window):
        window.connect('delete-event', WindowManager.on_delete)
        WindowManager.windows.append(window)
