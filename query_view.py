import gi

from psycopg2 import DatabaseError
from alert import Alert

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class QueryView(object):
    query_tree = None

    def __init__(self, query_tree, query_info, conn):
        sel = query_tree.get_selection()
        sel.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.query_tree = query_tree
        self.query_info = query_info
        self.conn = conn

    def run_query(self, query):
        try:
            for column in self.query_tree.get_columns():
                self.query_tree.remove_column(column)

            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()

            self.query_info.set_text(cursor.statusmessage)

            if not cursor.description:
                return

            columns = []
            # TODO get rid of manual incrementing
            i = 0
            for description in cursor.description:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(description.name.replace('_', '__'), renderer, text=i)
                column.set_resizable(True)
                i += 1
                self.query_tree.append_column(column)
                columns.append(str)

            store = Gtk.ListStore(*columns)

            for row in cursor.fetchall():
                store.append([str(i) for i in row])

            self.query_tree.set_model(store)

        except DatabaseError as e:
            Alert(e.message, self.query_tree.get_toplevel())
            self.conn.rollback()

        self.query_tree.show_all()
