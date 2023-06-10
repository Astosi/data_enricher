from abc import abstractmethod, ABC
from collections import OrderedDict


class ICache(ABC):
    @abstractmethod
    def add(self, key, value):
        pass

    @abstractmethod
    def get(self, key):
        pass


class LeiLookupCache(ICache):
    """
    A simple cache implementation using OrderedDict.
    """
    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.cache = OrderedDict()

    def add(self, key, value):
        if len(self.cache) >= self.cache_size:
            self.cache.popitem(last=False)
        self.cache[key] = value

    def get(self, key):
        return self.cache.get(key)
