import logging

import yeelight

from prism.light import LightProtocol

_cache = {}


def get_lights():
    raw_lights = yeelight.discover_bulbs()
    logging.debug('yeelight discovered %i lights', len(raw_lights))

    for raw_light in raw_lights:
        name = raw_light['capabilities']['name']
        if name not in _cache:
            _cache[name] = YeelightLight(name, raw_light)

    return list(_cache.values())


def get_light(name):
    if name not in _cache:
        get_lights()  # do nothing with response

    if name in _cache:
        return _cache[name]
    else:
        return None


class YeelightLight(LightProtocol):
    _client = None

    def __init__(self, name, client):
        self._name = name
        self._client = client

    @staticmethod
    def protocol():
        return 'Yeelight.v1'

    def get_name(self):
        return self._name
