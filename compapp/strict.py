from .base import itervars


class MixinStrict(object):

    def __setattr__(self, name, value):
        if name.startswith('_'):
            pass
        elif name not in self.__attrnames():
            raise AttributeError(
                "{self.__class__.__name__} object has no attribute {name}"
                .format(**locals()))
        super(MixinStrict, self).__setattr__(name, value)

    def __attrnames(self):
        try:
            return self.__attrnames_cached
        except AttributeError:
            pass

        names = self.paramnames()
        names.extend(name for name, _ in itervars(self.__class__))
        names = set(names)

        self.__attrnames_cached = names
        return names
