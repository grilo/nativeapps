#!/usr/bin/env python

"""
    Back and front for mobile applications.

    Of interest is the static folder which contains the stuff
    we serve to the client, with some of it being templated out.
"""

import logging
import os
import shutil

import flask
from flask import request

import nativeapps.application
import nativeapps.render



APP = flask.Flask(__name__, static_url_path='/static')

@APP.route("/", methods=['GET'])
def index():
    """
        Serve the main (and only) page: index.html

        We also inject our model in the initial response, preventing
        unnecessary communication between client and server.
    """

    storeapps = APP.config["storage"]
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    html = open(html_path, "r").read()

    html = html.replace("{{ android_applications }}",
                        nativeapps.render.android(
                            request.host_url + "application", storeapps))

    html = html.replace("{{ ios_applications }}",
                        nativeapps.render.ios(
                            request.host_url + "application", storeapps))
    return html, 200

@APP.route("/application/IPA/<app>/manifest.plist", methods=["GET"])
def serve_manifest(app):
    """
        Quirks of the iOS/IPA platform.

        For an iDevice to install the application, it must be served a special
        itms-services:// link which, in turn, points to a manifest file which,
        in turn, points to the actual application.

        The manifest file unfortunately requires the FQDN of the server, so
        we dynamically generate it every time it's requested to make sure
        that even if the server has a different name it still works.

        The info can't be set at startup time exclusively since we have to
        account for factors such as reverse proxies.
    """
    storeapps = APP.config["storage"]
    manifest = os.path.join(storeapps, "IPA", app, "manifest.plist")
    app_url = request.host_url + "application/IPA/" + app + "/" + app + ".ipa"
    if not os.path.isfile(manifest):
        return "File not found", 404
    logging.debug("Serving manifest with application url: %s", app_url)
    return open(manifest).read().replace("{{ APPLICATION_URL }}", app_url)

@APP.route("/application/<path:filename>", methods=["GET"])
def serve_application(filename):
    """
        Servers an existing application.

        The path must be complete, e.g.: APK/android-1.0/android-1.0.apk
    """
    return flask.send_from_directory("storeapps", filename)

@APP.route("/application", methods=["PUT", "POST"])
def upload():
    """
        Upload an application to the server.

        For PUT vs POST: https://stackoverflow.com/questions/6273560

        We also allow POST to add support for HTML forms.
    """
    storeapps = APP.config["storage"]
    binary = request.data

    # Add compatibility with POST requests
    if 'file' in request.files:
        binary = request.files['file'].read()

    logging.debug("Received file with size: %i", len(binary))

    try:
        app = nativeapps.application.from_binary(binary)
        filepath = app.write(storeapps)
        return "written: " + filepath, 201 # 201 CREATED
    except nativeapps.application.InvalidApplicationError as exception:
        return exception, 400

@APP.route("/application/<path:filename>", methods=["DELETE"])
def delete(filename):
    """
        Remove one of the stored applications.

        The full path isn't required since we only handle the actual filename.

        In fact, a request such as "DELETE /application/IPA/android-1.0.apk"
        would actually work (and delete the android APK). Not the most correct
        behavior, but simplifies logic alot.
    """
    storeapps = APP.config["storage"]
    extension = os.path.basename(filename).split(".")[-1].upper()
    dirname = ".".join(os.path.basename(filename).split(".")[:-1])
    directory = os.path.join(storeapps, extension, dirname)

    if os.path.isdir(directory):
        shutil.rmtree(directory)
        if os.path.isdir(directory):
            return "Unable to remove application (check server logs): %s" % (filename), 500
        return "Removed: %s" % (filename), 200

    return "File not found: %s" % (filename), 404


def run(host, port, threaded, debug, storage): # pragma: no cover
    """
        Launch the werkzeug application.
    """

    log_format = '%(asctime)s::%(levelname)s::%(module)s::%(message)s'
    logging.basicConfig(format=log_format)

    if debug:
        APP.debug = True
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Running in verbose mode.")
    else:
        logging.getLogger().setLevel(logging.INFO)

    APP.config["storage"] = storage
    APP.run(host, port, threaded)
