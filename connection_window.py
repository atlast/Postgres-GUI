import psycopg2
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sshtunnel import SSHTunnelForwarder
from paramiko import SSHException

from connections import Connections
from query_window import QueryWindow
from window_manager import WindowManager
from alert import Alert

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        label = Gtk.Label(data['label'])
        label.set_alignment(0, 1)
        self.add(label)

class ConnectionWindow(object):
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_objects_from_file('app.glade', ('winConnections', ))

        self.window = builder.get_object('winConnections')

        self.connection_list = builder.get_object('listConnections')

        self.ent_host = builder.get_object('entHost')
        self.ent_port = builder.get_object('entPort')
        self.ent_user = builder.get_object('entUser')
        self.ent_password = builder.get_object('entPassword')
        self.ent_database = builder.get_object('entDatabase')
        self.ent_remote_host = builder.get_object('entRemoteHost')
        self.ent_remote_user = builder.get_object('entRemoteUser')
        self.file_remote_key = builder.get_object('fileRemoteKey')

        self.connections = Connections()

        for connection in self.connections.get_connections():
            self.connection_list.add(ListBoxRowWithData(connection))

        if self.connections.count() == 0:
            self.on_add_connection(None)

        builder.connect_signals({
            'onAddConnection': self.on_add_connection,
            'onListSelected': self.on_list_selected,
            'onListActivated': self.on_list_activated,
            'onRemoveConnection': self.on_remove_connection,
            'onSaveConnection': self.on_save_connection,
            'onConnect': self.on_connect
        })

        WindowManager.add_window(self.window)
        self.window.show_all()

    def on_add_connection(self, obj):
        connection = self.connections.get_new_connection()
        self.connection_list.add(ListBoxRowWithData(connection))
        self.connection_list.show_all()

    def on_remove_connection(self, obj):
        selected_row = self.connection_list.get_selected_row()
        self.connection_list.remove(selected_row)

        self.connections.remove(selected_row.data)
        self.connections.save_to_file()

        if len(self.connection_list) == 0:
            self.on_add_connection(None)

        self.connection_list.show_all()
        self.connection_list.select_row(self.connection_list.get_row_at_index(0))

    def on_list_activated(self, obj, list_box_row):
        if not list_box_row:
            return

        self.on_list_selected(obj, list_box_row)
        self.on_connect(obj)

    def on_list_selected(self, obj, list_box_row):
        if not list_box_row:
            return

        self.ent_host.set_text(list_box_row.data['host'] if 'host' in list_box_row.data else '')
        self.ent_port.set_text(list_box_row.data['port'] if 'port' in list_box_row.data else '')
        self.ent_user.set_text(list_box_row.data['user'] if 'user' in list_box_row.data else '')
        self.ent_password.set_text(list_box_row.data['password'] if 'password' in list_box_row.data else '')
        self.ent_database.set_text(list_box_row.data['database'] if 'database' in list_box_row.data else '')
        self.ent_remote_host.set_text(list_box_row.data['remote_host'] if 'remote_host' in list_box_row.data else '')
        self.ent_remote_user.set_text(list_box_row.data['remote_user'] if 'remote_user' in list_box_row.data else '')
        if 'remote_key' in list_box_row.data and list_box_row.data['remote_key']:
            self.file_remote_key.set_filename(list_box_row.data['remote_key'])
        else:
            self.file_remote_key.unselect_all()

    def on_connect(self, obj):
        try:
            local_port = self.ent_port.get_text()
            tunnel = None

            if self.ent_remote_host.get_text():
                tunnel = SSHTunnelForwarder(
                    self.ent_remote_host.get_text(),
                    ssh_username=self.ent_remote_user.get_text(),
                    ssh_pkey=self.file_remote_key.get_filename(),
                    remote_bind_address=('127.0.0.1', int(self.ent_port.get_text()))
                )

                tunnel.start()
                local_port = tunnel.local_bind_port

            conn = psycopg2.connect(
                database=self.ent_database.get_text(),
                user=self.ent_user.get_text(),
                host=self.ent_host.get_text(),
                port=local_port,
                password=self.ent_password.get_text()
            )

            QueryWindow(conn, tunnel)
            WindowManager.remove(self.window)
            self.window.destroy()
        except SSHException as e:
            print e
            Alert('Unable to create SSH tunnel', self.window)
        except Exception as e:
            print e
            Alert('Unable to connect to server.', self.window)

    def on_save_connection(self, obj):
        data = self.connection_list.get_selected_row().data
        data['host'] = self.ent_host.get_text()
        data['port'] = self.ent_port.get_text()
        data['user'] = self.ent_user.get_text()
        data['password'] = self.ent_password.get_text()  # TODO change from saving plain text passwords
        data['database'] = self.ent_database.get_text()
        data['remote_host'] = self.ent_remote_host.get_text()
        data['remote_user'] = self.ent_remote_user.get_text()
        data['remote_key'] = self.file_remote_key.get_filename()

        self.connections.save_data(data)
        self.connections.save_to_file()
