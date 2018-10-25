import colorsys
import logging

from lifxlan import LifxLAN

from prism.light import LightProtocol, LightState

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

    def set_state(self, state_data):
        state = LifxState(state_data)

        if state.color is not None:
            self._client.set_color(state.color, duration=state.duration)

        if state.kelvin is not None:
            self._client.set_colortemp(state.kelvin, duration=state.duration)

        # brightness second to last to avoid flickering/transient effects
        if state.brightness is not None:
            self._client.set_brightness(state.brightness, duration=state.duration)

        # power should always be last, to avoid flicker/transient effects
        if state.power is not None:
            self._client.set_power(state.power, duration=state.duration)

        return None  # TODO: third party library does not give success or fail status


class LifxState(LightState):
    def __init__(self, data):
        if 'power' in data:
            self.power = True if data['power'] else False

        self.duration = int(data['duration']) * 1000 if 'duration' in data else 0

        if 'brightness' in data:
            self.brightness = int(65535 * float(data['brightness']))

        if 'color' in data:
            red, green, blue = data['color'][0] / 255, data['color'][1] / 255, data['color'][2] / 255
            kelvin = data['kelvin'] if 'kelvin' in data else 0
            (hue, saturation, brightness) = colorsys.rgb_to_hsv(red, green, blue)
            self.color = [hue * 65535, saturation * 65535, brightness * 65535, kelvin]  # last one is kelvin

        if 'kelvin' in data and 'color' not in data:  # if color is defined, kelvin is already set
            self.kelvin = data['kelvin']
