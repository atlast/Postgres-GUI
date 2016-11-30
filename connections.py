import json
import uuid

class Connections(object):
    FILE_NAME = 'connections.json'

    def __init__(self):
        self.connections = []
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(self.FILE_NAME) as data_file:
                self.connections = json.load(data_file)
        except:
            pass

    def save_to_file(self):
        with open(self.FILE_NAME, 'w') as outfile:
            json.dump(self.connections, outfile)

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
