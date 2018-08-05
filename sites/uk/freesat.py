# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, json, helper

def grab(channel, timespan):
	tz = pytz.timezone("UTC")
	now = datetime.datetime.now(tz)
	shows = []
	for i in range(9):
		text = helper.download("https://www.freesat.co.uk/tv-guide/api/" + str(i) + "/?channel=" + channel)
		if text is None:
			continue
		events = json.loads(text)[0]["event"]

		for event in events:
			show = {}
			show["start"] = datetime.datetime.fromtimestamp(event["startTime"], tz)
			if (show["start"] - now).total_seconds() / 3600 > timespan:
				return shows
			show["stop"] = show["start"] + datetime.timedelta(seconds=event["duration"])
			show["title"] = event["name"]
			show["desc"] = event["description"]
			if "episodeNo" in event:
				show["episode-num"] = (event["episodeNo"], "onscreen")

			shows.append(show)
	return shows

def channellist():
	text = helper.download("https://www.freesat.co.uk/tv-guide/api/")
	channels = json.loads(text)
	result = []
	for channel in channels:
		result.append((channel["channelid"], channel["channelname"], channel["channelname"]))
	return result
