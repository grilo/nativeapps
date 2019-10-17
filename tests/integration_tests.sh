#!/usr/bin/env bash

set -eu
set -o pipefail

appsdir="../nativeapps/storeapps"

function exists() {
    local filename="$1"
    [ -f "$filename" ] && echo "[OK] Exists: $filename" && return
    echo "[NOK] Unable to find file: $filename" && exit 1
}

function notexists() {
    local filename="$1"
    [ ! -f "$filename" ] && echo "[OK] Not exists: $filename" && return
    echo "[NOK] Exists: $filename" && exit 1
}

function contains() {
    local string="$1"
    local pattern="$2"
    echo "$string" | grep -q "$pattern" && echo "[OK] String contains: $pattern" && return
    echo "[NOK] Missing: $pattern" && exit 1
}

function notcontains() {
    local string="$1"
    local pattern="$2"
    echo "$string" | grep -v -q "$pattern" && echo "[OK] String doesn't contain: $pattern" && return
    echo "[NOK] Contains: $pattern" && exit 1
}

echo "Testing upload IPA..."
curl -s -X PUT -T filetest.ipa localhost:10000/application > /dev/null
exists "$appsdir/IPA/helloworld-1.0-1.0/helloworld-1.0-1.0.ipa"
exists "$appsdir/IPA/helloworld-1.0-1.0/manifest.plist"

echo -e "\nTesting upload APK..."
curl -s -X PUT -T filetest.apk localhost:10000/application > /dev/null
exists "$appsdir/APK/com.google.android.diskusage-4.0.2-4002/com.google.android.diskusage-4.0.2-4002.apk"

echo -e "\nTesting index page..."
indexpage=$(curl -s -X GET localhost:10000/)
contains "$indexpage" "com.google.android.diskusage-4.0.2-4002.apk"
contains "$indexpage" "itms-services.*helloworld-1.0-1.0/manifest.plist"

echo -e "\nDownloading manifest.plist"
manifest_url=$(echo "$indexpage" | grep "itms-services" | sed -e 's/.*url=//g' -e 's/">//g')
manifest=$(curl -s -X GET $manifest_url)
contains "$manifest" "helloworld-1.0-1.0.ipa"

echo -e "\nDownloading IPA..."
ipa_url=$(echo "$manifest" | grep "helloworld-1.0-1.0.ipa" | sed -e 's/.*<string>//g' -e 's/<\/string>.*//g')
curl -s -X GET $ipa_url > downloadedipa
exists "downloadedipa"
rm downloadedipa

echo -e "\nDownloading APK..."
apk_url=$(echo "$indexpage" | grep "localhost:1000.*4002.apk" | sed -e 's/.*href="//g' -e 's/".*//g')
curl -s -X GET $apk_url > downloadedapk
exists "downloadedapk"
rm downloadedapk

echo -e "\nTesting delete IPA..."
curl -s -X DELETE localhost:10000/application/helloworld-1.0-1.0.ipa > /dev/null
notexists "$appsdir/IPA/helloworld-1.0-1.0/helloworld-1.0-1.0.ipa"
notexists "$appsdir/IPA/helloworld-1.0-1.0/manifest.plist"

echo -e "\nTesting delete APK..."
curl -s -X DELETE localhost:10000/application/com.google.android.diskusage-4.0.2-4002.apk > /dev/null
notexists "$appsdir/APK/com.google.android.diskusage-4.0.2-4002/com.google.android.diskusage-4.0.2-4002.apk"

echo -e "\nTesting index page..."
indexpage=$(curl -s -X GET localhost:10000/)
notcontains "$indexpage" "com.google.android.diskusage-4.0.2-4002.apk"
notcontains "$indexpage" "itms-services.*helloworld-1.0-1.0/manifest.plist"

echo -e "\n"
