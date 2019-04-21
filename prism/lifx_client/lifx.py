"""Lifx vendor/protocol implementation.

Uses third party library LifxLAN, see https://github.com/mclarkk/lifxlan
"""

import colorsys
import logging

from lifxlan import LifxLAN

from prism.light import LightProtocol

_lifxlan = LifxLAN()
_cache = {}

log = logging.getLogger('prism')


def get_lights():
    """Discover lights on Local Area Network.

    :returns: ``[LightProtocol]``
    """
    _lifxlan.devices = None  # forces a refresh
    _lifxlan.num_lights = None
    try:
        raw_lights = _lifxlan.get_devices()  # get devices
    except OSError as err:
        log.warning('could not get lifx lights: %s', err)
        return []

    log.debug('discovered %i lifx lights', len(raw_lights))

    for raw_light in raw_lights:
        name = raw_light.get_label()
        if name not in _cache:
            _cache[name] = LifxLight(name, raw_light)

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


class LifxLight(LightProtocol):
    """Lifx implementation for LightProtocol."""

    _client = None

    def __init__(self, name, client):
        """Create and inialize LiftLight.

        :param name: name of light, should be unique
        :param client: third party client
        """
        self._name = name
        self._client = client

    @staticmethod
    def protocol():
        """See ``LightProtocol.protocol`` documentation."""
        return 'Lifx.v1'

    def get_name(self):
        """See ``LightProtocol.get_name`` documentation."""
        return self._name

    def is_on(self):
        """Get if light in on or off.

        :returns: power state
        """
        return self._client.get_power()

    def set_state(self, state):
        """See ``LightProtocol.set_state`` documentation."""
        duration = _to_lifx_duration(state.duration())

        color = state.color()
        kelvin = state.kelvin()

        if color is not None:
            self._client.set_color(_to_lifx_color(color, kelvin), duration=duration)

        if kelvin is not None:
            self._client.set_colortemp(kelvin, duration=duration)

        brightness = state.brightness()

        # brightness second to last to avoid flickering/transient effects
        if brightness is not None:
            self._client.set_brightness(_to_lifx_brightness(brightness), duration=duration)

        power = state.power()

        # power should always be last, to avoid flicker/transient effects
        if power is not None:
            self._client.set_power(power, duration=duration)

        return None  # TODO: third party library does not give success or fail status


def _to_lifx_duration(duration):
    return duration if duration is not None else 0


def _to_lifx_brightness(brightness):
    return int(65535 * (float(brightness) / 100.0)) if brightness is not None else 0


def _to_lifx_color(color, kelvin):
    red, green, blue = color[0] / 255, color[1] / 255, color[2] / 255
    (hue, saturation, brightness) = colorsys.rgb_to_hsv(red, green, blue)
    kelvin = kelvin if kelvin is not None else 0

    return [hue * 65535, saturation * 65535, brightness * 65535, kelvin]
