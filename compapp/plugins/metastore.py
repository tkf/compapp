import json

from ..descriptors import Delegate
from ..core import Plugin


class MetaStore(Plugin):

    metafile = 'meta.json'
    datastore = Delegate()
    log = Delegate()

    @property
    def metafilepath(self):
        return self.datastore.path(self.metafile)

    def prepare(self):
        self.data = {}

    def record(self, name, data):
        self.data[name] = data
        if not self.datastore.is_writable():
            self.log.debug(
                'Datastore is not available. Not saving meta data {}'
                .format(name))
            return
        with open(self.metafilepath, 'w') as file:
            json.dump(self.data, file)

    def load(self):
        with open(self.metafilepath) as file:
            self.data = json.load(file)
