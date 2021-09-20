#!/bin/bash
tox -c tox.ini -- --apikey="$1" --infura-id="$2"