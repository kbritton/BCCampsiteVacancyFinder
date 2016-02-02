#!/bin/bash

PLIST="com.kenbritton.check_campsites.plist"
USER_AGENT_DIR="$HOME/Library/LaunchAgents/"
USER_AGENT_PLIST="$USER_AGENT_DIR/$PLIST"

cp $PLIST $USER_AGENT_DIR
launchctl unload $USER_AGENT_PLIST
launchctl load $USER_AGENT_PLIST
