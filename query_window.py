import psycopg2

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

from window_manager import WindowManager
from data_view import DataView
from query_view import QueryView


class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, table_name):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = table_name
        label = Gtk.Label(table_name)
        label.set_alignment(0, 1)
        label.set_padding(5, 2.5)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        self.add(label)


class QueryWindow(object):
    LIMIT_SIZE = 20
    tunnel = None

    def __del__(self):
        if self.tunnel:
            self.tunnel.stop()

    def __init__(self, conn, tunnel):
        self.cursor = conn.cursor()

        self.last_detail_table = ''
        self.last_query_table = ''
        self.current_tab = 0
        self.current_page = 0
        self.current_table = ''
        self.store = None
        self.tunnel = tunnel

        builder = Gtk.Builder()
        builder.add_objects_from_file('app.glade', ('winQuery', ))

        builder.connect_signals({
            'on_table_row_selected': self.on_table_row_selected,
            'on_tab_selected': self.on_tab_selected,
            'on_previous_page': self.on_previous_page,
            'on_next_page': self.on_next_page,
            'on_filter_activate': self.on_filter_activate,
            'on_run_query': self.on_run_query,
            'on_data_key_press': self.on_data_key_press
        })

        self.query_tabs = builder.get_object('queryTabs')

        self.ent_data_filter = builder.get_object('entDataFilter')
        self.txt_query = builder.get_object('txtQuery')

        self.list_tables = builder.get_object('listTables')
        self.fetch_tables()

        self.data_view = DataView(builder.get_object('dataTree'), conn)
        self.query_view = QueryView(builder.get_object('queryTree'), builder.get_object('lblQueryInfo'), conn)

        self.window = builder.get_object('winQuery')
        WindowManager.add_window(self.window)
        self.window.show_all()

    def fetch_tables(self):
        self.cursor.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)' ORDER BY relname")

        for table in self.cursor.fetchall():
            self.list_tables.add(ListBoxRowWithData(table[0]))

    def on_table_row_selected(self, list, row):
        if not row:
            return

        self.ent_data_filter.set_text('')
        self.ent_data_filter.show_all()
        self.current_table = row.data
        self.refresh(row.data)

    def refresh_details(self, table):
        if table == self.last_detail_table:
            return

        self.last_detail_table = table

        print 'REFRESHING DETAILS'
        pass

    def refresh_data(self, table):
        self.data_view.set_table(table)

    def refresh_query(self, table):
        pass

    def on_data_key_press(self, element, key):
        print key, key.is_modifier, key.get_keyval()

    def on_run_query(self, el):
        buffer = self.txt_query.get_buffer()
        start, end = buffer.get_bounds()
        self.query_view.run_query(buffer.get_text(start, end, False))

    def on_previous_page(self, el):
        self.data_view.previous_page()

    def on_next_page(self, el):
        self.data_view.next_page()

    def refresh(self, table):
        if self.current_tab == 1:
            self.refresh_details(table)
        elif self.current_tab == 0:
            self.refresh_data(table)
        else:
            self.refresh_query(table)

    def on_tab_selected(self, notebook, pane, index):
        self.current_tab = index
        self.refresh(self.current_table)

    def on_filter_activate(self, element):
        self.data_view.set_where(element.get_text())
        self.data_view.refresh_data()
