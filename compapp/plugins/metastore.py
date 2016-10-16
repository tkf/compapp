import json
import glob
import os

from ..descriptors import Link
from ..core import Plugin


class MetaStore(Plugin):

    _parentstore = Link('...datastore')
    log = Link('...log')

    def prepare(self):
        self.data = {}

    def record(self, name, data):
        self.data[name] = data
        if not self._parentstore.is_writable():
            self.log.debug(
                'Datastore is not available. Not saving meta data {}'
                .format(name))
            return
        path = self._parentstore.path('meta-{}.json'.format(name))
        with open(path, 'w') as file:
            json.dump(data, file)

    def load(self):
        files = glob.glob(self._parentstore.path('meta-*.json', mkdir=False))
        for path in files:
            filename = os.path.basename(path)
            name = filename[len('meta-'):-len('.json')]
            with open(path) as file:
                self.data[name] = json.load(file)
