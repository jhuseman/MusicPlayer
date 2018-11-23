#! /bin/bash

export executable=MusicPlayer.py
export workingdir=/home/pi/MusicPlayer
export service_name=MusicPlayer
export service_description="Runs the Music player script on startup, \nto play music!"
export runuser=pi

export REPLACE_VAR_PROVIDES=$service_name
export REPLACE_VAR_EXECUTABLE=$executable
export REPLACE_VAR_WORKINGDIR=$workingdir
export REPLACE_VAR_SCRIPTDIR=$(pwd)
export REPLACE_VAR_RUNAS=$runuser
export REPLACE_VAR_DESCRIPTION=$(echo $service_description | sed 's/\\/\\\\/g' | sed 's/\\\\n/\\n#                    /g' | sed 's/|/\\|/g')

cd ./init.d

cat ./Template \
 | sed "s|~~SETUP_REPLACE_VAR_PROVIDES~~|$REPLACE_VAR_PROVIDES|g" \
 | sed "s|~~SETUP_REPLACE_VAR_EXECUTABLE~~|$REPLACE_VAR_EXECUTABLE|g" \
 | sed "s|~~SETUP_REPLACE_VAR_WORKINGDIR~~|$REPLACE_VAR_WORKINGDIR|g" \
 | sed "s|~~SETUP_REPLACE_VAR_SCRIPTDIR~~|$REPLACE_VAR_SCRIPTDIR|g" \
 | sed "s|~~SETUP_REPLACE_VAR_RUNAS~~|$REPLACE_VAR_RUNAS|g" \
 | sed "s|~~SETUP_REPLACE_VAR_DESCRIPTION~~|$REPLACE_VAR_DESCRIPTION|g" \
 > ./$service_name

sudo cp ./$service_name /etc/init.d/
sudo chmod 755 /etc/init.d/$service_name
sudo update-rc.d $service_name defaults

cd ..
