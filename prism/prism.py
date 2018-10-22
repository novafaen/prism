import logging

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

    def add_light(self, light_json):
        pass

    @staticmethod
    def get_lights():
        lifx_lights = lifx_client.get_lights()
        yeelight_lights = yeelight_client.get_lights()

        return lifx_lights + yeelight_lights

    @staticmethod
    def get_light(name):
        lifx_light = lifx_client.get_light(name)

        if lifx_client.get_light(name) is not None:
            return lifx_light

        yeelight_light = yeelight_client.get_light(name)

        return yeelight_light


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
    response.headers['Content-Type'] = 'application/se.novafaen.smrt.light.v1+json'
    return response


@app.route('/light/<string:name>', methods=['GET'])
def get_light(name):
    light = app_light.get_light(name)

    if light is not None:
        code = 200
        body = {
            'name': light.get_name(),
            'protocol': light.protocol()
        }
        content_type = 'application/se.novafaen.smrt.light.v1+json'
    else:
        code = 404
        body = {
            'status': 'NotFound',
            'message': 'Could not find light \'%s\'' % name
        }
        content_type = 'application/se.novafaen.smrt.error.v1+json'

    response = make_response(jsonify(body), code)
    response.headers['Content-Type'] = content_type
    return response
