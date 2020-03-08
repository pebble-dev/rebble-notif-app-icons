try:
    import google.auth.exceptions
    try:
        import googleclouddebugger
        googleclouddebugger.enable(module='notif-app-icons')
    except (ImportError, google.auth.exceptions.DefaultCredentialsError):
        print("Couldn't start cloud debugger")
except ImportError:
    print("Couldn't import google exceptions")

import io
from os import environ

import beeline
from beeline.middleware.flask import HoneyMiddleware
from flask import Flask, request, abort, send_file
from PIL import Image
import requests

app = Flask(__name__)

if environ.get('HONEYCOMB_KEY'):
     beeline.init(writekey=environ['HONEYCOMB_KEY'], dataset='rws', service_name='lp')
     HoneyMiddleware(app, db_events=True)


def get_apple_image_url(bundle_id, country):
    response = requests.get('https://itunes.apple.com/lookup', params={'bundleId': bundle_id, 'country': country})
    response.raise_for_status()
    results = response.json()['results']
    if len(results) == 0:
        abort(404)
    return results[0]['artworkUrl512']


def rescale_image(original_url, size, out_f):
    response = requests.get(original_url)
    response.raise_for_status()
    with io.BytesIO(response.content) as in_f:
        image = Image.open(in_f)
        if size < image.width and size < image.height:
            image.thumbnail((size, size), Image.ANTIALIAS)
        image.save(out_f, 'JPEG')
    out_f.seek(0)
    return out_f


@app.route('/ios/<string:bundle_id>/<int:size>.jpg')
def image(bundle_id, size):
    country = request.args.get('country')
    url = get_apple_image_url(bundle_id, country)
    f = io.BytesIO()
    rescale_image(url, size, f)
    return send_file(f, mimetype='image/jpeg', cache_timeout=2592000)  # 30 days


@app.route('/')
def index():
    return 'hi'


@app.route('/heartbeat')
def heartbeat():
    return 'ok'
