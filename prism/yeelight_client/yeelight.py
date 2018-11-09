import logging

import yeelight
from yeelight import Bulb

from prism.light import LightProtocol, LightState

_cache = {}


def get_lights():
    raw_lights = yeelight.discover_bulbs()
    logging.debug('yeelight discovered %i lights', len(raw_lights))

    for raw_light in raw_lights:
        name = raw_light['capabilities']['name']
        if name not in _cache:
            _cache[name] = YeelightLight(name, Bulb(raw_light['ip']))

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

    def set_state(self, data):
        response = True

        state = YeelightState(data)

        if state.color is not None:
            action_response = self._client.send_command('set_rgb', [state.color, 'smooth', state.duration])
            response &= action_response['result'] == ['ok']

        if state.kelvin is not None:
            action_response = self._client.send_command('set_ct_abx', [state.kelvin, 'smooth', state.duration])
            response &= action_response['result'] == ['ok']

        # brightness second to last to avoid flickering/transient effects
        if state.brightness is not None:
            action_response = self._client.send_command('set_bright', [state.brightness, 'smooth', state.duration])
            response &= action_response['result'] == ['ok']

        # power should always be last, to avoid flicker/transient effects
        if state.power is not None:
            action_response = self._client.send_command('set_power', [state.power, 'smooth', state.duration])
            response &= action_response['result'] == ['ok']

        return response


class YeelightState(LightState):
    def __init__(self, data):
        if 'power' in data:
            self.power = 'on' if data['power'] else 'off'

        self.duration = int(data['duration']) * 1000 if 'duration' in data else 30

        if 'brightness' in data:
            self.brightness = float(format(data['brightness'] * 100, '.2f'))

        if 'color' in data:
            self.color = 16777215  # TODO: always white, fix

        if 'kelvin' is not None:
            self.kelvin = data['kelvin']
