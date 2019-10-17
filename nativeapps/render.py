#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json


tpl = """
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
        <table class="table table-responsive-lg alert alert-dark">
        <thead>
            <tr>
                <th scope="col">Key</th>
                <th scope="col">Value</th>
            </tr>
        </thead>
        <tbody>
    """

    for key, value in dictionary.items():
        if isinstance(value, list) and len(value) > 0:
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

def listfiles(rootdir, terminator):
    for root, dirs, files in os.walk(rootdir):
        for filename in files:
            path = os.path.join(root, filename)
            name = filename.split("-", 1)[0]
            version = ".".join(filename.split("-", 1)[-1].split(".")[:-1])
            if path.endswith(terminator):
                yield path, name, version

def android(url, rootdir):
    template = ""
    i = 0
    for path, name, version in listfiles(rootdir, ".apk"):
        directory = os.path.dirname(path)
        meta = json.load(open(os.path.join(directory, "metadata.json"), "rb+"))
        template += tpl % (path.replace(rootdir, url), "android",
                           name, i, version, i, handle_dict(meta))
        i += 1
    return template

def ios(url, rootdir):
    template = ""
    i = 0
    url = "itms-services://?action=download-manifest&url=" + url

    for path, name, version in listfiles(rootdir, "manifest.plist"):
        directory = os.path.dirname(path)
        meta = json.load(open(os.path.join(directory, "metadata.json"), "rb+"))

        name, version = os.path.basename(directory).split("-", 1)
        app_url = path.decode("utf-8").replace(rootdir, url).encode("utf-8")
        template += tpl % (app_url, "ios",
                           name, i, version, i, handle_dict(meta))
        i += 1
    return template
