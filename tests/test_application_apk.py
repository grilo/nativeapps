#!/usr/bin/env python

import pytest
import os

import nativeapps.application


def test_apk_from_file():
    expected = "com.google.android.diskusage-4.0.2-4002.apk"
    testfile = os.path.join("tests", "filetest.apk")
    apk = nativeapps.application.from_binary(open(testfile, "rb+").read())
    print apk.metadata

    assert apk.filename == expected
