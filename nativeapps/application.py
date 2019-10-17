#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import json
import hashlib
import zipfile
import plistlib
import datetime
import time
import distutils.spawn
import tempfile
import subprocess
import shlex
import re
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import biplist
import axmlparserpy.apk # https://github.com/antitree/AxmlParserPY


class InvalidApplicationError(Exception):
    """The binary content is invalid for this application type."""
    pass

class ChecksumError(Exception):
    """The written file doesn't match the contents."""
    pass


class Base(object):

    def validate(self):
        """Ideally, we would validate that the APP file is valid by checking:
            * Expiration date of the certificat used to sign it.
            * Expiration date of the provisioning profile itself.
            * It must be a development application.
            * Has at least one UDID (device) in the list.

            Note: Some of these conditions do not apply to enterprise/wildcard apps.
            Note2: Some of these conditions will vary depending on the platform.
        """
        raise NotImplementedError

    @property
    def metadata(self):
        """
            Return a string (JSON-format, key: value) with all available metadata.
        """
        raise NotImplementedError

    @property
    def raw(self):
        """
            The raw binary data of the application (e.g. the IPA file).
        """
        return self.contents

    @property
    def filename(self):
        """
            The name of the file on disk.
        """
        return self.name + "-" + self.version + "-" + self.buildnumber + \
                "." + self.__class__.__name__.lower()

    def write(self, rootdir):
        """
            Writes files with the following structure:
                <path>/<type>/<name>-<version>-<buildnumber>/<name>-<version>-<buildnumber>.<type>

            Example:
                static/apps/APK/application-1.0-0/application-1.0-0.apk

            This extra dir may seem unnecessary first, but it's used to keep
            things tidy in the filesystem in case we want to store app specific
            metadata. Right now, it's being used exclusively to hold the
            manifest.plist file for iOS/IPA files.

        """
        directory = os.path.join(rootdir,
                                 self.__class__.__name__,
                                 ".".join(self.filename.split(".")[:-1]))

        if not os.path.isdir(directory):
            os.makedirs(directory)

        path_app = os.path.join(directory, self.filename)

        # Get the content's hash
        checksum_contents = hashlib.sha256(self.raw).hexdigest()
        with open(path_app, "wb+") as appfd:
            appfd.write(self.raw)
        ondisk_contents = hashlib.sha256(open(path_app, "rb+").read()).hexdigest()

        # Validate that the written contents are exact,
        # prune them otherwise.
        if checksum_contents != ondisk_contents:
            os.unlink(path)
            raise ChecksumError

        with open(os.path.join(directory, "metadata.json"), "wb+") as metadatafd:
            metadatafd.write(self.metadata.encode("utf-8"))

        return path_app


class IPA(Base):

    def __init__(self, contents):
        super(IPA, self).__init__()
        self.contents = contents

        in_memory = StringIO.StringIO(contents)
        ipa_file = zipfile.ZipFile(in_memory, "r")

        regex_infoplist = re.compile(r".ayload/(.*?\.app)/Info.plist$")
        regex_pprofile = re.compile(r".ayload/(.*?\.app)/embedded.mobileprovision$")
        self.infoplist = None
        self.pprofile = None

        for path in ipa_file.namelist():
            if regex_infoplist.match(path):
                self.infoplist = biplist.readPlistFromString(ipa_file.read(path))
            elif regex_pprofile.match(path):
                contents = ipa_file.read(path)
                start_tag = '<?xml version="1.0" encoding="UTF-8"?>'
                stop_tag = '</plist>'
                start_index = contents.index(start_tag)
                stop_index = contents.index(stop_tag,
                                                  start_index + len(start_tag)) + len(stop_tag)
                plist_data = contents[start_index:stop_index]
                self.pprofile = plistlib.readPlistFromString(plist_data)

            if self.infoplist and self.pprofile:
                break

        if not self.infoplist or not self.pprofile:
            raise InvalidApplicationError


    def _decode_cert(self, binary_data):
        cert = {
            "expiration": None,
            "uid": None,
            "cn": None,
        }
        if not distutils.spawn.find_executable("openssl"):
            logging.debug("Unable to find 'openssl' executable in PATH, cert info will be incomplete.")
            return cert

        with tempfile.NamedTemporaryFile() as temp:
            temp.write(binary_data)
            temp.flush()
            cmd = 'openssl x509 -inform der -text -in %s' % (temp.name)
            out = subprocess.check_output(shlex.split(cmd)).decode("unicode_escape").encode("latin1")

        for line in out.splitlines():
            if "Not After : " in line:
                date = line.split(":", 1)[-1].lstrip()
                cert["expiration"] = datetime.datetime.strptime(date, '%b %d %H:%M:%S %Y %Z').isoformat()
            elif "Subject: UID" in line:
                attrs = {}
                curr = ""
                for match in re.split("([A-Z ]+)=", line):
                    match = match.strip()
                    if re.match("^[A-Z]+$", match):
                        curr = match
                    else:
                        attrs[curr] = match.rstrip(",")
                cert["uid"] = attrs["UID"]
                cert["cn"] = attrs["CN"]

        return cert

    @property
    def metadata(self):

        meta = {}
        for key, value in self.pprofile.items():
            if key == "DeveloperCertificates":
                certs = []
                for cert in value:
                    certs.append(self._decode_cert(cert.data))
                value = certs
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            meta[key] = value

        for key, value in self.infoplist.items():
            meta[key] = value

        for encoding in ["utf-8", "latin1", "utf-16"]:
            try:
                return json.dumps(meta, encoding=encoding)
            except UnicodeDecodeError:
                pass
        return json.dumps(meta, ensure_ascii=False)

    @property
    def name(self):
        # AKA bundle-identifier
        return self.infoplist["CFBundleName"].encode("utf-8")

    @property
    def version(self):
        return self.infoplist["CFBundleShortVersionString"]

    @property
    def buildnumber(self):
        return self.infoplist["CFBundleVersion"]

    def generate_manifest(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>items</key>
        <array>
            <dict>

                <key>assets</key>
                <array>
                    <dict>
                        <key>kind</key>
                        <string>software-package</string>
                        <key>url</key>
                        <string>{{ APPLICATION_URL }}</string>
                    </dict>
                </array>

                <key>metadata</key>
                <dict>
                    <key>bundle-identifier</key>
                    <string>%s</string>
                    <key>bundle-version</key>
                    <string>%s</string>
                    <key>kind</key>
                    <string>software</string>
                    <key>title</key>
                    <string>%s</string>
                </dict>

            </dict>

       </array>
    </dict>
</plist>""" % (self.infoplist["CFBundleName"],
               self.infoplist["CFBundleShortVersionString"],
               self.infoplist["CFBundleName"])

    def write(self, path):
        """
            We overload the 'write' method so we can add the manifest.plist

            Note: the manifest.plist contains a "MACRO" named
            {{ APPLICATION_URL}}. The reason is this file contains a property
            which directly references the server's FQDN wich might change
            between server restarts. We leave it responsability of the
            server itself to dynamically change this string when serving
            the file.
        """
        fullpath = super(IPA, self).write(path)
        directory = os.path.dirname(fullpath)
        manifest = os.path.join(directory, "manifest.plist")
        manifest_contents = self.generate_manifest().encode("utf-8")
        # Generate and write the manifest file
        with open(manifest, "wb+") as manifestfd:
            manifestfd.write(manifest_contents)
        return manifest


class APK(Base):

    def __init__(self, contents):
        super(APK, self).__init__()
        self.contents = contents
        self.apk = axmlparserpy.apk.APK(contents, raw=True)
        if not self.apk.is_valid_apk():
            raise InvalidApplicationError

    @property
    def metadata(self):
        meta = {
            "package": self.apk.get_package(),
            "androidversioncode": self.apk.get_androidversion_code(),
            "androidversionname": self.apk.get_androidversion_name(),
            "activities": self.apk.get_activities(),
            "services": self.apk.get_services(),
            "receivers": self.apk.get_receivers(),
            "permissions": self.apk.get_permissions(),
            "minsdkversion": self.apk.get_min_sdk_version(),
            "targetsdkversion": self.apk.get_target_sdk_version(),
            "libraries": self.apk.get_libraries(),
            "files": self.apk.get_files(),
        }

        for encoding in ["utf-8", "latin1", "utf-16"]:
            try:
                return json.dumps(meta, encoding=encoding)
            except UnicodeDecodeError:
                pass
        return json.dumps(meta, ensure_ascii=False)

    @property
    def name(self):
        return self.apk.get_package().encode("utf-8")

    @property
    def version(self):
        return self.apk.get_androidversion_name()

    @property
    def buildnumber(self):
        return self.apk.get_androidversion_code()


def from_binary(contents):
    try:
        return APK(contents)
    except InvalidApplicationError:
        logging.debug("This application is not a valid APK.")

    try:
        return IPA(contents)
    except InvalidApplicationError:
        logging.debug("This application is not a valid IPA.")

    raise InvalidApplicationError("Unknown application type: must be a valid IPA or APK file.")
