#!/usr/bin/env python

import pytest
import os

import nativeapps.application


def test_ipa_from_binary():
    expected = """<?xml version="1.0" encoding="UTF-8"?>
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
				<string>helloworld</string>
				<key>bundle-version</key>
				<string>1.0</string>
				<key>kind</key>
				<string>software</string>
				<key>title</key>
				<string>helloworld</string>
			</dict>
		</dict>
	</array>
</dict>
</plist>"""
    testfile = os.path.join("tests", "filetest.ipa")
    ipa = nativeapps.application.from_binary(open(testfile, "rb+").read())
    out = ipa.generate_manifest()

    print ipa.metadata

    assert out == expected
