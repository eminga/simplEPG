# simplEPG
*This software is in early development, don't expect anything to work.*

simpleEPG is an EPG crawler and generator which outputs a valid [XMLTV](https://github.com/XMLTV/xmltv) file.

## Usage
Add the channels you want to crawl (see sites/xx/yyy.xml) to the `config.xml` and run `simplepg.py` afterwards.

## Requirements
Python 2.7 or 3.x

Non-standard modules: pytz, six, progress.bar (optional)

Modules in the standard library: datetime, importlib, json, re, socket, ssl, sys, time, xml.etree.ElementTree
