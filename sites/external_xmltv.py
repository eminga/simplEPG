# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import xml.etree.cElementTree as ET

def grab(channel, timespan):
	try:
		path, channelid = channel.rsplit(".xml:", 1)
		path += ".xml"
	except ValueError:
		path, channelid = channel.rsplit(":", 1)
	xml = ET.parse(path).getroot()
	return xml.findall("./programme[@channel='" + channelid + "']")
