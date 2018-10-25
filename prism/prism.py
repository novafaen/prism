import logging, json

from smrt import SMRTApp, app, make_response, request, jsonify, produces, consumes
from prism import lifx_client, yeelight_client


class Prism(SMRTApp):
    def __init__(self):
        logging.debug('Prism spinning up...')

        # initiation goes here

        logging.debug('Prism initiated!')

    def status(self):
        return {
            'name': 'Prism',
            'status': 'OK',
            'version': '0.0.1'
        }

    @staticmethod
    def client_name():
        return 'Prism'

    @staticmethod
    def get_lights():
        lifx_lights = lifx_client.get_lights()
        yeelight_lights = yeelight_client.get_lights()

        return lifx_lights + yeelight_lights

    @staticmethod
    def get_light(name):
        lifx_light = lifx_client.get_light(name)

        if lifx_light is not None:
            return lifx_light

        yeelight_light = yeelight_client.get_light(name)

        if yeelight_light is not None:
            return yeelight_light

        return None  # no light found


# create prism and register it with smrt
app_light = Prism()

app.register_client(app_light)


@app.route('/lights', methods=['GET'])
@produces('application/se.novafaen.prism.lights.v1+json')
def get_lights():
    lights = app_light.get_lights()
    response = {
        'lights': [{'name': l.get_name(), 'protocol': l.protocol()} for l in lights]
    }

    response = make_response(jsonify(response), 200)
    response.headers['Content-Type'] = 'application/se.novafaen.prism.lights.v1+json'
    return response


@app.route('/light/<string:name>', methods=['GET'])
@produces('application/se.novafaen.prism.light.v1+json')
def get_light(name):
    light = app_light.get_light(name)

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


@app.route('/light/<string:name>/state', methods=['PUT'])
@consumes('application/se.novafaen.prism.lightstate.v1+json')
@produces('application/se.novafaen.prism.light.v1+json')
def post_light_state(name):
    light = app_light.get_light(name)

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
