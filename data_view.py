import gi

from psycopg2 import DatabaseError
from alert import Alert

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

class DataView(object):
    data_tree = None
    table = None
    store = None
    row_size = 20
    where = None
    page = 0
    order = None
    order_direction = 'ASC'
    last_selected_column = None

    def __init__(self, data_tree, conn):
        sel = data_tree.get_selection()
        sel.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.data_tree = data_tree
        self.conn = conn
        self.columns = []

    def set_table(self, table):
        if self.table == table:
            return

        self.table = table
        self.reset_table()
        self.refresh_schema()
        self.refresh_data()

    def set_where(self, where):
        self.where = where

    def set_sort(self, column):
        if self.order == column:
            self.order_direction = 'DESC' if self.order_direction == 'ASC' else 'ASC'
        else:
            self.order_direction = 'ASC'

        self.last_selected_column.set_sort_order(1 if self.order_direction == 'ASC' else 0)

        self.order = column

    def on_column_click(self, column, column_name):
        self.page = 0
        self.last_selected_column.set_sort_indicator(False)
        column.set_sort_indicator(True)
        self.last_selected_column = column

        self.set_sort(column_name)
        self.refresh_data()

    def reset_table(self):
        self.page = 0
        self.order = None
        self.order_direction = 'ASC'
        self.where = None
        self.last_selected_column = None

    def refresh_schema(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 1' % self.table)

        for column in self.data_tree.get_columns():
            self.data_tree.remove_column(column)

        self.columns = []
        # TODO get rid of manual incrementing
        i = 0
        for description in cursor.description:
            s = None
            if description.type_code == 16:
                renderer = Gtk.CellRendererToggle()
                self.columns.append(bool)
                column = Gtk.TreeViewColumn(description.name.replace('_', '__'), renderer, active=i)
            else:
                renderer = Gtk.CellRendererText()
                renderer.set_property('editable', True)
                renderer.connect('edited', self.on_text_edit, i)
                renderer.set_property('placeholder-text', 'Null')
                renderer.set_property('ellipsize', Pango.EllipsizeMode.END)
                self.columns.append(str)
                column = Gtk.TreeViewColumn(description.name.replace('_', '__'), renderer, text=i)

            column.set_clickable(True)
            column.set_resizable(True)
            column.set_fixed_width(100)
            if i == 0:
                # TODO Should this be here?
                self.order = description.name
                column.set_sort_indicator(True)
                column.set_sort_order(1)
                self.last_selected_column = column
            column.connect('clicked', self.on_column_click, description.name)
            self.data_tree.append_column(column)
            i += 1

        self.store = Gtk.ListStore(*self.columns)
        self.data_tree.set_model(self.store)

    def on_text_edit(self, widget, row, text, column_num):
        if self.data_tree.get_column(0).get_title() != 'id':
            Alert('Unable to update because we can\'t handle a missing ID column. TODO fix this')

        self.store[row][column_num] = text
        column = self.data_tree.get_column(column_num)
        column_name = column.get_title().replace('__', '_')

        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE %s SET %s=\'%s\' WHERE id=%s' % (self.table, column_name, text, self.store[row][0]))
            self.conn.commit()
        except DatabaseError as e:
            Alert(e.message, self.data_tree.get_toplevel())
            self.conn.rollback()

    def refresh_data(self):
        self.store.clear()

        query = 'SELECT * FROM %s' % self.table

        if self.where:
            query += ' WHERE %s' % self.where

        if self.order:
            query += ' ORDER BY %s %s' % (self.order, self.order_direction)

        query += ' LIMIT %s OFFSET %s' % (self.row_size, self.page * self.row_size)

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()

            for row in cursor.fetchall():
                data = []

                for i, val in enumerate(row):
                    if self.columns[i](val) == 'None':
                        data.append(None)
                    else:
                        data.append(self.columns[i](val))

                self.store.append(data)

        except DatabaseError as e:
            Alert(e.message, self.data_tree.get_toplevel())
            self.conn.rollback()

        self.data_tree.show_all()

    def previous_page(self):
        if self.page == 0:
            return

        self.page -= 1
        self.refresh_data()

    def next_page(self):
        self.page += 1
        self.refresh_data()
