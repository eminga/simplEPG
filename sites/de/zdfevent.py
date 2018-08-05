# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, json, helper

def grab(channel, timespan):
	# for olympia this is https://olympia.zdf.de
	eventurl = "https://european-championships.zdf.de"
	# length of the event in days
	eventduration = 11


	tz = pytz.timezone("UTC")
	now = datetime.datetime.now(tz)
	shows = []

	for i in range(eventduration + 1):
		text = helper.download(eventurl + "/feeds/epg-" + str(i))
		if text is None:
			continue
		events = json.loads(text)["epg-" + str(i)]["data"][int(channel)]["shows"]

		for event in events:
			show = {}
			show["start"] = datetime.datetime.fromtimestamp(event["start"], tz)
			if (show["start"] - now).total_seconds() / 3600 > timespan:
				return shows
			show["stop"] = datetime.datetime.fromtimestamp(event["end"], tz)
			title = event["title"]
			category = event["category"]["name"]
			if category in title:
				show["title"] = title
			else:
				show["title"] = category + ": " + title
			show["desc"] = event["text"]
			show["presenter"] = event["presenter"]
			show["url"] = eventurl + event["url"]
			show["icon"] = "https:" + event["image"]

			shows.append(show)
	return shows
