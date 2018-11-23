#! /bin/bash

export screen_name=$1

screen -S $screen_name -X stuff ^C
