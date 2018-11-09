class LightProtocol:
    _name = None
    _client = None

    @staticmethod
    def protocol():
        raise NotImplementedError('Client is missing "protocol" function implementation')

    def get_name(self):
        raise NotImplementedError('Client is missing "get_name" function implementation')

    def set_state(self, state):
        return self._client.set_state(state)

    def set_power(self, on_off):
        state = {
            'power': on_off
        }
        return self._client.set_state(state)

    def __str__(self):
        return '<Light name="%s" protocol="%s">' % (self._name, self._client.protocol())


class LightState:
    power = None
    duration = None
    brightness = None
    color = None
    kelvin = None

    def __str(self):
        return '<LightState power="%s" duration="%i" brightness="%f" color="%s" kelvin="%i">' % \
               (self.power, self.duration, self.brightness, self.color, self.kelvin)
