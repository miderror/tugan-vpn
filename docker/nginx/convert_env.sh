#!/bin/sh

export ALLOWED_HOSTS=$(echo $ALLOWED_HOSTS | tr ',' ' ' | xargs)
