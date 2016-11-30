#!/usr/bin/env python

# TODO update listbox label on save
# TODO requires sudo apt-get install python-psycopg2
# TODO requires sudo apt-get install python-pip; pip install sshtunnel

import os
import json
import uuid

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from connection_window import ConnectionWindow
ConnectionWindow()

style_provider = Gtk.CssProvider()

css = open(os.path.dirname(os.path.abspath(__file__)) + '/style.css', 'rb') # rb needed for python 3 support
css_data = css.read()
css.close()

style_provider.load_from_data(css_data)

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

Gtk.main()
