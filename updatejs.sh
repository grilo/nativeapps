#!/usr/bin/env bash

set -eu
set -o pipefail

echo "########################"
echo "DOES NOT WORK"
echo "Download places files with incorrect version in the dest directory"
echo "Also missing jquery download"
echo "Also missing popper download"
echo "########################"
exit 1

echo "Downloading latest bootstrap release..."
curl -s https://api.github.com/repos/twbs/bootstrap/releases/latest \
    | grep "browser_download_url.*\-dist.zip" \
    | cut -d : -f 2,3 \
    | tr -d \" \
    | xargs curl -s -L > bootstrap.zip

echo "Extracting contents to tmpdir..."
[ ! -d tmpdir ] || rm -fr tmpdir
unzip -q -o bootstrap.zip -d tmpdir
rm bootstrap.zip

echo "Copying css..."
filename="bootstrap.min.css"
cp "$(find tmpdir -type f -name "$filename")" "nativeapps/static/css/$filename"
echo "Copying js..."
filename="bootstrap.min.js"
cp "$(find tmpdir -type f -name "$filename")" "nativeapps/static/js/$filename"

echo "Cleaning up tmpdir..."
#rm -fr tmpdir
echo "Bootstrap updated"
