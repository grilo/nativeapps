#!/usr/bin/env python

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

def dict_to_table(dictionary):
    """
        This could use some decent refactoring.

        Recursive function which handles pure strings, lists and dicts.
        Prints them in HTML-formatted tables.
    """
    string = """<table class="table table-responsive-lg alert alert-dark">"""
    string += """
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
            new_values = ""
            if isinstance(value[0], dict):
                for d in value:
                    new_values += dict_to_table(d)
            else:
                new_values += "".join(["<p>" + str(v) + "</p>" for v in value])
            value = new_values
        elif isinstance(value, dict):
            value = dict_to_table(value)
        string += "<tr>"
        string += "<td>" + key + "</td>"
        string += "<td>" + str(value) + "</td>"
        string += "</tr>"
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
        dictionary = json.loads(open(os.path.join(directory, "metadata.json"), "rb+").read())
        template += tpl % (path.replace(rootdir, url), "android", name, i, version, i, dict_to_table(dictionary))
        i += 1
    return template

def ios(url, rootdir):
    template = ""
    i = 0
    url = "itms-services://?action=download-manifest&url=" + url

    for path, name, version in listfiles(rootdir, "manifest.plist"):
        directory = os.path.dirname(path)
        dictionary = json.loads(open(os.path.join(directory, "metadata.json"), "rb+").read())
        name, version = os.path.basename(directory).split("-", 1)
        template += tpl % (path.replace(rootdir, url), "ios", name, i, version, i, dict_to_table(dictionary))
        i += 1
    return template
