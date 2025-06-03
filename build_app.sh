#!/bin/bash

# Create app bundle structure
mkdir -p "UI Inspector.app/Contents/MacOS"
mkdir -p "UI Inspector.app/Contents/Resources"

# Copy files
cp Info.plist "UI Inspector.app/Contents/"
cp mac_ui_inspector.py "UI Inspector.app/Contents/MacOS/main.py"
chmod +x "UI Inspector.app/Contents/MacOS/main.py"

# Sign the app
codesign --force --deep --sign - --entitlements entitlements.plist "UI Inspector.app" 