"""Prism is a light service built on SMRT framework.

Prism consolidates different light sources into one single API.

Current supported lights:
- Lifx LAN.
- Yeelight LAN.
"""
import json
import logging

from smrt import SMRTApp, app, make_response, request, jsonify, smrt

from prism import lifx_client, yeelight_client

log = logging.getLogger('prism')


class Prism(SMRTApp):
    """Prism is a ``SMRTApp`` that is to be registered with SMRT."""

    def __init__(self):
        """Create and initiate ````Prism`` application."""
        logging.debug('%s spinning up...', self.application_name())

        SMRTApp.__init__(self)

        #self.broadcast('{"type":"hello world","from":"prism"}')

        logging.debug('%s initiated!', self.application_name())

    def status(self):
        """Use ``SMRTApp`` documentation for ``status`` implementation."""
        return {
            'name': self.application_name(),
            'status': 'OK',  # hard coded for now
            'version': '0.0.1'
        }

    @staticmethod
    def application_name():
        """Use ``SMRTApp`` documentation for ``application_name`` implementation."""
        return 'Prism'

    @staticmethod
    def get_lights():
        """Get all ligthts that can be discovered.

        Function will perform a discovery for light sources, and return the
        light in an array. Lights are cached, so if a light "dissapears", it
        will still be returned once discovered.

        :returns: [``LightProtocol``].
        """
        lifx_lights = lifx_client.get_lights()
        yeelight_lights = yeelight_client.get_lights()

        return lifx_lights + yeelight_lights

    @staticmethod
    def get_light(name):
        """Get a light identified by name.

        Function will do discovery, see ``get_lights`` documentation.

        :param name: ``String`` unique identifier.
        :returns: ``LightProtocol`` or ``None``
        """
        lifx_light = lifx_client.get_light(name)

        if lifx_light is not None:
            return lifx_light

        yeelight_light = yeelight_client.get_light(name)

        if yeelight_light is not None:
            return yeelight_light

        return None  # no light found


# create prism and register it with smrt framework
prism = Prism()
app.register_client(prism)


@smrt('/lights',
      produces='application/se.novafaen.prism.lights.v1+json')
def get_lights():
    """Endpoint to get all discoverable, and cached, lights.

    :returns: ``se.novafaen.prism.lights.v1+json``
    """
    lights = prism.get_lights()
    response = {
        'lights': [{'name': l.get_name(), 'protocol': l.protocol()} for l in lights]
    }

    response = make_response(jsonify(response), 200)
    response.headers['Content-Type'] = 'application/se.novafaen.prism.lights.v1+json'
    return response


@smrt('/light/<string:name>',
      produces='application/se.novafaen.prism.light.v1+json')
def get_light(name):
    """Endpoint to get a single light by name.

    :returns: ``se.novafaen.prism.light.v1+json``
    """
    light = prism.get_light(name)

    if light is None:
        body = {
            'status': 'NotFound',
            'message': 'Could not find light \'%s\'' % name
        }
        response = make_response(jsonify(body), 404)
        response.headers['Content-Type'] = 'application/se.novafaen.smrt.error.v1+json'
        return response

    body = {
        'name': light.get_name(),
        'protocol': light.protocol()
    }

    response = make_response(jsonify(body), 200)
    response.headers['Content-Type'] = 'application/se.novafaen.prism.light.v1+json'
    return response


@smrt('/light/<string:name>/state',
      methods=['PUT'],
      consumes='application/se.novafaen.prism.lightstate.v1+json',
      produces='application/se.novafaen.prism.light.v1+json')
def put_light_state(name):
    """Endpoint to update light state, identified by name.

    :body: ``se.novafaen.prism.lightstate.v1+json``
    :returns: ``se.novafaen.prism.light.v1+json``
    """
    light = prism.get_light(name)

    if light is None:
        body = {
            'status': 'NotFound',
            'message': 'Could not find light \'%s\'' % name
        }
        response = make_response(jsonify(body), 404)
        response.headers['Content-Type'] = 'application/se.novafaen.smrt.error.v1+json'
        return response

    logging.debug('setting light "%s" to state %s', name, request.data)

    data = json.loads(request.data)

    light.set_state(data)

    response = make_response(jsonify(''), 204)
    response.headers['Content-Type'] = 'application/se.novafaen.prism.light.v1+json'
    return response


@smrt('/light/<string:name>/state/power/on',
      methods=['PUT'],
      produces='application/se.novafaen.prism.light.v1+json')
def put_power_on(name):
    """Endpoint to turn on light, identified by name.

    :returns: ``application/se.novafaen.prism.light.v1+json``
    """
    return _power(name, True)


@smrt('/light/<string:name>/state/power/off',
      methods=['PUT'],
      produces='application/se.novafaen.prism.light.v1+json')
def put_power_off(name):
    """Endpoint to turn off light, identified by name.

    :returns: ``application/se.novafaen.prism.light.v1+json``
    """
    return _power(name, False)


def _power(name, on_off):
    light = prism.get_light(name)

    if light is None:
        body = {
            'status': 'NotFound',
            'message': 'Could not find light \'%s\'' % name
        }
        response = make_response(jsonify(body), 404)
        response.headers['Content-Type'] = 'application/se.novafaen.smrt.error.v1+json'
        return response

    logging.debug('[prism] setting light "%s" power to %s', name, on_off)

    light.set_power(on_off)

    response = make_response(jsonify(''), 204)
    response.headers['Content-Type'] = 'application/se.novafaen.prism.light.v1+json'
    return response
