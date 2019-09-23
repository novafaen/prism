"""Light module contains interfaces to be implemented by light protocols.

When adding support for a new protocol or vendor, this impl
"""

import logging as loggr
import time

log = loggr.getLogger('smrt')


class LightState:
    """Light state, make sure values are ok before sending them to the client."""

    _power = None
    _duration = None
    _brightness = None
    _color = None
    _kelvin = None

    def __init__(self, power=None, duration=None, brightness=None, color=None, kelvin=None):
        """Initialize ``Lightstate``.

        See ``Lightstate.set`` implementation.
        """
        self.set(power=power, duration=duration, brightness=brightness, color=color, kelvin=kelvin)

    def set(self, power=None, duration=None, brightness=None, color=None, kelvin=None):
        """Set state.

        Will also check input for types and bounds.
        :param power: ``Boolean``
        :param duration: ``Integer`` seconds
        :param brightness: ``Integer`` percentage 0-100
        :param color: ``[Integer, Integer, Integer]`` values 0-256
        :param kelvin: ``Integer`` 2500-9000
        """
        self._set_power(power)
        self._set_duration(duration)
        self._set_brightness(brightness)
        self._set_color(color)
        self._set_kelvin(kelvin)

    def _set_power(self, power):
        if power is not None:
            if isinstance(power, bool):
                self._power = power
            else:
                raise TypeError('Light power must be either True or False, got="%s"' % power)

    def _set_duration(self, duration):
        if duration is not None:
            if isinstance(duration, int) and 0 <= duration <= 3600:
                self._duration = duration
            else:
                raise TypeError('Light duration must be between 0-3600, got="%s"' % duration)

    def _set_brightness(self, brightness):
        if brightness is not None:
            if isinstance(brightness, int) and 0 <= brightness <= 100:
                self._brightness = brightness
            else:
                raise TypeError('Light brightness must be between 0-100, got="%s"' % brightness)

    def _set_color(self, color):
        if color is not None:
            if isinstance(color, list) and len(color) == 3 and \
                    0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255:
                self._color = color
            else:
                raise TypeError('Light color must be array of length 3, with values 0-255, got="%s"' % color)

    def _set_kelvin(self, kelvin):
        if kelvin is not None:
            if isinstance(kelvin, int) and 2500 <= kelvin <= 9000:
                self._kelvin = kelvin
            else:
                raise TypeError('Light kelvin must be between 2500-9000, got="%s"' % kelvin)

    def update(self, state):
        """Update state from another ``LightState``.

        :param state: ``LightState`` to update with.
        """
        self._set_power(state.power())
        self._set_duration(state.duration())
        self._set_brightness(state.brightness())
        self._set_color(state.color())
        self._set_kelvin(state.kelvin())

    def power(self):
        """Get power.

        :returns: ``Boolean`` power
        """
        return self._power

    def duration(self):
        """Get duration.

        :returns: ``Integer`` duration
        """
        return self._duration

    def brightness(self):
        """Get brightness.

        :returns: ``Integer`` brightness
        """
        return self._brightness

    def color(self):
        """Get color.

        :returns: ``[Integer, Integer, Integer]`` color
        """
        return self._color

    def kelvin(self):
        """Get kelvin.

        :returns: ``Integer`` kelvin
        """
        return self._kelvin

    def json(self):
        """Return state as json representation.

        :returns: ``Directory`` light state
        """
        return {
            'power': self._power,
            'duration': self._duration,
            'brightness': self._brightness,
            'color': self._color,
            'kelvin': self._kelvin
        }

    def __repr__(self):
        """Return string representation.

        :returns: ``String`` representation.
        """
        return '<LightState power={} duration={} ' \
               'brightness={} color={} kelvin={}>'.format(
                    self._power, self._duration, self._brightness,
                    self._color, self._kelvin)


class LightProtocol:
    """Interface for light clients, i.e. vendors or protocols."""

    _name = None
    _client = None
    _last_seen = None
    _last_state = None

    def __init__(self, state=None):
        """Create and initialize ``LightProtocol``."""
        self._last_seen = int(time.time())  # seen when created
        self._last_state = state if state is not None else LightState()

    @staticmethod
    def protocol():
        """Return name of protocol.

        :returns: protocol name as ``String``
        """
        raise NotImplementedError('Client is missing "protocol" function implementation')

    def get_name(self):
        """Return name of light source.

        :returns: name as ``String``
        """
        raise NotImplementedError('Client is missing "get_name" function implementation')

    def set_state(self, state):
        """Set state for light source.

        :param state: ``LightState`` new state for light
        :returns: new state
        """
        if not isinstance(state, LightState):
            return RuntimeError('Invalid state, must implement LightState class')

        successful = self._set_state(state)
        log.debug('change state successful=%s', successful)

        if successful:
            self._last_seen = int(time.time())

        self._last_state.update(state)

        return successful

    def update_state(self, state):
        """Update state and last seen attributes."""
        self._last_seen = int(time.time())
        self._last_state.update(state)

    def get_state(self):
        """Get last known state.

        :returns: ``LightState`` object.
        """
        return self._last_state

    def _set_state(self, state):
        """See ``LightProtocol.set_state`` documentation."""
        raise NotImplementedError('Client is missing "_set_state" function implementation')

    def set_power(self, on_off):
        """Set power state for light source.

        :param on_off: ``Boolean`` as power on or off
        :returns: new state
        """
        state = {
            'power': on_off
        }
        return self.set_state(state)

    def json(self):
        """Return json representation of light, i.e. ``Dict``.

        :returns: ``Dict`` json representation.
        """
        return {
            'name': self._name,
            'protocol': self.protocol(),
            'last_seen': self._last_seen,
            'state': self._last_state.json()
        }

    def __repr__(self):
        """Return string representation.

        :returns: ``String``
        """
        return '<Light name="{._name}" protocol="{.protocol()}" ' \
               'last_seen={._last_seen}>'.format(self)
