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

SPECIAL_APPLE_APPS = set((
  "com.Apple.Magnifier",
  "com.apple.AppStore",
  "com.apple.Bridge",
  "com.apple.DocumentsApp",
  "com.apple.Fitness",
  "com.apple.Health",
  "com.apple.Home",
  "com.apple.Keynote",
  "com.apple.Maps",
  "com.apple.MobileAddressBook",
  "com.apple.MobileSMS",
  "com.apple.MobileStore",
  "com.apple.Music",
  "com.apple.Numbers",
  "com.apple.Pages",
  "com.apple.Passbook",
  "com.apple.Photo-Booth",
  "com.apple.Playgrounds",
  "com.apple.Preferences",
  "com.apple.Translate",
  "com.apple.VoiceMemos",
  "com.apple.calculator",
  "com.apple.camera",
  "com.apple.clips",
  "com.apple.compass",
  "com.apple.facetime",
  "com.apple.findmy",
  "com.apple.iBooks",
  "com.apple.iCloudDriveApp",
  "com.apple.iMovie",
  "com.apple.measure",
  "com.apple.mobilecal",
  "com.apple.mobilegarageband",
  "com.apple.mobilemail",
  "com.apple.mobilenotes",
  "com.apple.mobilephone",
  "com.apple.mobilesafari",
  "com.apple.mobileslideshow",
  "com.apple.mobiletimer",
  "com.apple.news",
  "com.apple.podcasts",
  "com.apple.reminders",
  "com.apple.shortcuts",
  "com.apple.stocks",
  "com.apple.store.Jolly",
  "com.apple.tips",
  "com.apple.tv",
  "com.apple.weather"
))

app = Flask(__name__)

if environ.get('HONEYCOMB_KEY'):
     beeline.init(writekey=environ['HONEYCOMB_KEY'], dataset='rws', service_name='notif-app-icons')
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
    if bundle_id in SPECIAL_APPLE_APPS:
        response = requests.get(f"https://storage.googleapis.com/ios-standard-icons/{bundle_id}.jpeg", stream=True)
        response.raise_for_status()
        return send_file(response.raw, mimetype='image/jpeg', cache_timeout=2592000)
    country = request.args.get('country')
    url = get_apple_image_url(bundle_id, country)
    f = io.BytesIO()
    rescale_image(url, size, f)
    return send_file(f, mimetype='image/jpeg', cache_timeout=2592000)  # 30 days


@app.route('/')
def index():
    return 'hi'


@app.route('/heartbeat')
@app.route('/notif-app-icons/heartbeat')
def heartbeat():
    return 'ok'
