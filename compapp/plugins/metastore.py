import json

from ..descriptors import Link
from ..core import Plugin
from .datastores import SubDataStore


class MetaStore(Plugin):

    # FIXME: The plugin hooks of this (below) datastore are not
    #        called.  Probably all plugins have to be derived from
    #        `PluginWrapper` (after appropriate rename) so that nested
    #        plugins like below are handled properly?  At the moment,
    #        not calling plugin hooks of `datastore` is fine since
    #        almost nothing is done in the hooks.
    datastore = SubDataStore
    log = Link('...log')

    def prepare(self):
        self.data = {}

    def record(self, name, data):
        self.data[name] = data
        if not self.datastore.is_writable():
            self.log.debug(
                'Datastore is not available. Not saving meta data {}'
                .format(name))
            return
        path = self.datastore.path('{}.json'.format(name))
        with open(path, 'w') as file:
            json.dump(data, file)

    def load(self):
        for filename, path in self.datastore.globitems('*.json'):
            name = filename[:-len('.json')]
            with open(path) as file:
                self.data[name] = json.load(file)
