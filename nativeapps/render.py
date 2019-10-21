#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Very basic templating mechanics.

    This is used to render the application lists in each of the tabs.
"""

import os
import json

import nativeapps.io


TEMPLATE = """
     <tr>
        <th scope="row">
            <a href="%s">
                <img style="width: 2em; height: 2em;" src="static/img/%s.png"/>
            </a>
        </th>
        <td>%s</td>
        <td>
            <button class="btn btn-link"
                    data-toggle="collapse"
                    data-target="#collapseID%i">%s</button>
        </td>
    </tr>
    <tr>
        <td colspan="4">
            <div class="collapse" id="collapseID%i">
                <div class="card card-body">
                    %s
                </div>
            </div>
        </td>
    </tr>
""" # link, icon, name, version, metadata, sequence_id, sequence_id, metadata

def handle_list(sequence):
    """
        Given an iterator:
            ["hello", "world"]
        Generate:
            <p>hello</p><p>world</p>
    """
    string = ""
    for value in sequence:
        if isinstance(value, dict):
            string += handle_dict(value)
        else:
            value = str(value)
            string += "<p>%s</p>\n" % (str(value))
    return string

def handle_dict(dictionary):
    """
        Prints HTML-formatted tables.
    """
    string = """
        <table class="table table-sm table-responsive alert alert-dark">
        <thead>
            <tr>
                <th scope="col">Key</th>
                <th scope="col">Value</th>
            </tr>
        </thead>
        <tbody>
    """

    for key, value in dictionary.items():
        if isinstance(value, list) and value:
            value = handle_list(value)
        elif isinstance(value, dict):
            value = handle_dict(value)
        elif isinstance(value, int):
            value = str(value)
        elif isinstance(value, unicode):
            value = value.encode("utf-8")
        string += "<tr><td>{key}</td><td>{value}</td></tr>\n".format(key=key, value=value)

    string += "</tbody></table>"
    return string

def android(url, rootdir):
    """
        Render the HTML for APKs.
    """
    template = ""
    i = 0
    for path in nativeapps.io.ls(rootdir, r".*\.apk$"):
        directory = os.path.dirname(path)
        name, version = os.path.basename(directory).split("-", 1)
        meta = json.load(open(os.path.join(directory, "metadata.json"), "r"))
        app_url = path.decode("utf-8").replace(rootdir, url).encode("utf-8")
        template += TEMPLATE % (app_url, "android",
                                name, i, version, i, handle_dict(meta))
        i += 1
    return template

def ios(url, rootdir):
    """
        Render the HTML for IPAs.

        The two differences from android are:
            * We have to extract the name/version with a slightly different logic
            * The application's link is this weird itms-services:// thing.
    """
    template = ""
    i = 0
    url = "itms-services://?action=download-manifest&url=" + url

    for path in nativeapps.io.ls(rootdir, r".*manifest.plist$"):
        directory = os.path.dirname(path)
        name, version = os.path.basename(directory).split("-", 1)
        meta = json.load(open(os.path.join(directory, "metadata.json"), "r"))
        app_url = path.decode("utf-8").replace(rootdir, url).encode("utf-8")
        template += TEMPLATE % (app_url, "ios",
                                name, i, version, i, handle_dict(meta))
        i += 1
    return template
