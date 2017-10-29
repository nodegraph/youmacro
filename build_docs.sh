#!/bin/bash
sphinx-apidoc -f -o sphinx/source .
sphinx-build -b html sphinx/source sphinx/build


