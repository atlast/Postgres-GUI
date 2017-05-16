import json
import uuid
import copy
import keyring


APP_NAMESPACE = 'io.atlast.postgres-gui'


class Connections(object):
    FILE_NAME = 'connections.json'

    def __init__(self):
        self.connections = []
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.FILE_NAME) as data_file:
                self.connections = json.load(data_file)

                # Pull out password from OS keyring and insert back in data
                for connection in self.connections:
                    connection['password'] = keyring.get_password(APP_NAMESPACE, connection['uuid'])
        except:
            pass

    def save_to_file(self):
        with open(self.FILE_NAME, 'w') as outfile:
            tmp_connections = copy.deepcopy(self.connections)

            # Save password in OS keyring and remove from data to be saved to file
            for connection in tmp_connections:
                keyring.set_password(APP_NAMESPACE, connection['uuid'], connection['password'])
                del connection['password']

            json.dump(tmp_connections, outfile)

    def count(self):
        return len(self.connections)

    def get_connections(self):
        return self.connections

    def get_new_connection(self):
        return {
            'uuid': uuid.uuid1().urn,
            'label': 'Untitled',
            'host': 'localhost',
            'port': '5432'
        }

    def remove(self, data):
        try:
            self.connections.remove(data)
        except:
            # TODO this is not the right way to do this.
            pass

    def save_data(self, data):
        data['label'] = data['host']
        for connection in self.connections:
            if connection['uuid'] == data['uuid']:
                connection = data['uuid']
                return

        self.connections.append(data)
