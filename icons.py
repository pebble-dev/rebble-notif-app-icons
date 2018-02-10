from gevent import monkey; monkey.patch_all()
import io

from flask import Flask, request, abort, send_file
from PIL import Image
import requests

app = Flask(__name__)


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