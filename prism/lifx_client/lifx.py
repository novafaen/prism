import logging

from lifxlan import LifxLAN

from prism.light import LightProtocol

_lifxlan = LifxLAN()
_cache = {}


def get_lights():
    _lifxlan.devices = None  # forces a refresh
    _lifxlan.num_lights = None
    raw_lights = _lifxlan.get_devices()  # get devices
    logging.debug('lifx discovered %i lights', len(raw_lights))

    for raw_light in raw_lights:
        name = raw_light.get_label()
        if name not in _cache:
            _cache[name] = LifxLight(name, raw_light)

    return list(_cache.values())


def get_light(name):
    if name not in _cache:
        get_lights()  # do nothing with response

    if name in _cache:
        return _cache[name]
    else:
        return None


class LifxLight(LightProtocol):
    _client = None

    def __init__(self, name, client):
        self._name = name
        self._client = client

    @staticmethod
    def protocol():
        return 'Lifx.v1'

    def get_name(self):
        return self._name
