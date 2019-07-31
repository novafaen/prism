"""YeeLight vendor/protocol implementation.

Uses third party library yeelight, see https://gitlab.com/stavros/python-yeelight
"""

import logging

import yeelight
from yeelight import Bulb

from prism.light import LightProtocol

_cache = {}

log = logging.getLogger('prism')


def get_lights():
    """Discover lights on Local Area Network.

    :returns: ``[LightProtocol]``
    """
    raw_lights = yeelight.discover_bulbs()
    log.debug('yeelight discovered %i lights', len(raw_lights))

    for raw_light in raw_lights:
        name = raw_light['capabilities']['name']
        if name not in _cache:
            _cache[name] = YeelightLight(name, Bulb(raw_light['ip']))

    return list(_cache.values())


def get_light(name):
    """Discover single light identified by name.

    :returns: ``LightProtocol`` or ``None``
    """
    if name not in _cache:
        get_lights()  # do nothing with response

    if name in _cache:
        return _cache[name]
    else:
        return None


class YeelightLight(LightProtocol):
    """YeeLight implementation for LightProtocol."""

    _client = None

    def __init__(self, name, client):
        """Create and inialize YeelightLight.

        :param name: name of light, should be unique
        :param client: third party client
        """
        LightProtocol.__init__(self)
        self._name = name
        self._client = client

    @staticmethod
    def protocol():
        """See ``LightProtocol.protocol`` documentation."""
        return 'Yeelight.v1'

    def get_name(self):
        """See ``LightProtocol.get_name`` documentation."""
        return self._name

    def _set_state(self, state):
        """See ``LightProtocol.set_state`` documentation."""
        successful = True

        # minimum 1 second transision, looks better that way!
        duration = _to_yeelight_duration(state.duration())

        color = 16777215  # TODO: always white, fix #state.color()

        if color is not None:
            action_response = self._client.send_command('set_rgb', [color, 'smooth', duration])
            successful &= action_response['result'] == ['ok']

        kelvin = state.kelvin()

        if kelvin is not None:
            action_response = self._client.send_command('set_ct_abx', [kelvin, 'smooth', duration])
            successful &= action_response['result'] == ['ok']

        brightness = _to_yeelight_brightness(state.brightness())

        # brightness second to last to avoid flickering/transient effects
        if brightness is not None:
            action_response = self._client.send_command('set_bright', [brightness, 'smooth', duration])
            successful &= action_response['result'] == ['ok']

        power = _to_yeelight_power(state.power())

        # power should always be last, to avoid flicker/transient effects
        if power is not None:
            action_response = self._client.send_command('set_power', [power, 'smooth', duration])
            successful &= action_response['result'] == ['ok']

        return successful


def _to_yeelight_duration(duration):
    return duration * 1000 if duration is not None else 60


def _to_yeelight_brightness(brightness):
    return float(format(brightness, '.2f')) if brightness is not None else None


def _to_yeelight_power(power):
    if power is None:
        return None
    return 'on' if power else 'off'
