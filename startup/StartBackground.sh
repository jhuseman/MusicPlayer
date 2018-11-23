#! /bin/bash

export working_dir=$1
export screen_name=$2
export script_name=$3

cd $working_dir
screen -dmS $screen_name ./$script_name

