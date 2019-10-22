#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Input/Ouput functions
"""

import logging
import os
import re
import hashlib
import distutils.spawn
import tempfile
import subprocess
import shlex


class ChecksumError(Exception):
    """The written file doesn't match the contents."""
    pass


def ls(rootdir, pattern):
    """
        Return a list of files which match <regex>.
    """

    regex = re.compile(pattern)

    for root, _, files in os.walk(rootdir):
        for filename in files:
            path = os.path.join(root, filename)
            if regex.match(path):
                yield path

def readfile(path):
    with open(path, "rb") as filedescriptor:
        return filedescriptor.read()

def writefile(path, contents, overwrite=True):
    """
        Writes files and do checksum validation of the written contents.
    """

    if os.path.isfile(path) and not overwrite:
        raise IOError

    directory = os.path.dirname(path)
    if not os.path.isdir(directory):
        logging.debug("Creating directory: %s", directory)
        os.makedirs(directory)

    # Get the content's hash
    checksum_contents = hashlib.sha256(contents).hexdigest()
    with open(path, "wb") as filedescriptor:
        filedescriptor.write(contents)
        filedescriptor.flush()

    ondisk_contents = hashlib.sha256(open(path, "rb").read()).hexdigest()

    # Validate that the written contents are exact,
    # prune them otherwise.
    if checksum_contents != ondisk_contents:
        os.unlink(path)
        raise ChecksumError

    return path

def which(binary):
    """
        Returns True if binary is in PATH, otherwise False.
    """
    return distutils.spawn.find_executable(binary)


def cert_decode(binary_certificate):
    if which("openssl"):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(binary_certificate)
            temp.flush()
            cmd = 'openssl x509 -inform der -text -in %s' % (temp.name)
            raw_out = subprocess.check_output(shlex.split(cmd))
            return raw_out.decode("unicode_escape").encode("latin1")
    return None
