"""Light module contains interfaces to be implemented by light protocols.

When adding support for a new protocol or vendor, this impl
"""


class LightProtocol:
    """Interface for light clients, i.e. vendors or protocols."""

    _name = None
    _client = None

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

        return self._client.set_state(state)

    def set_power(self, on_off):
        """Set power state for light source.

        :param on_off: ``Boolean`` as power on or off
        :returns: new state
        """
        state = {
            'power': on_off
        }
        return self.set_state(state)

    def __str__(self):
        """Return string representation.

        :returns: ``String``
        """
        return '<Light name="%s" protocol="%s">' % (self._name, self.protocol())


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
        if power is not None:
            if isinstance(power, bool):
                self._power = power
            else:
                raise TypeError('Light power must be either True or False, got="%s"' % power)

        if duration is not None:
            if isinstance(duration, int) and 0 <= duration <= 3600:
                self._duration = duration
            else:
                raise TypeError('Light duration must be between 0-3600, got="%s"' % duration)

        if brightness is not None:
            if isinstance(brightness, int) and 0 <= brightness <= 100:
                self._brightness = brightness
            else:
                raise TypeError('Light brightness must be between 0-100, got="%s"' % brightness)

        if color is not None:
            if isinstance(color, list) and len(color) == 3 and \
                    0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255:
                self._color = color
            else:
                raise TypeError('Light color must be array of length 3, with values 0-255, got="%s"' % color)

        if kelvin is not None:
            if isinstance(kelvin, int) and 2500 <= kelvin <= 9000:
                self._kelvin = kelvin
            else:
                raise TypeError('Light kelvin must be between 2500-9000, got="%s"' % kelvin)

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

    def __str__(self):
        """Return string representation.

        :returns: ``String`` representation
        """
        return '<LightState power="%s" duration="%i" brightness="%f" color="%s" kelvin="%i">' % \
               (self._power, self._duration, self._brightness, self._color, self._kelvin)
