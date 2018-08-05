# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, re, helper

def grab(channel, timespan):
	tz = pytz.timezone("Europe/Berlin")
	now = datetime.datetime.now(tz)
	shows = []
	a = 0
	if now.time().hour < 7:
		a = -1
	for i in range(a, 14):
		date = now + datetime.timedelta(days=i)
		datestring = "%s.%s.%s" % (date.day, date.month, date.year)
		text = helper.download("http://programm.ard.de/TV/Programm/Sender?datum=" + date.strftime("%d.%m.%Y") + "&hour=0&sender=" + channel)
		if text is None:
			continue

		sections = helper.split(text, "<li class=\"eid", "</li>")
		laststart = datetime.datetime.min.replace(tzinfo=tz)
		for section in sections:
			show = {}
			temp = re.search("<span class=\"date[\s\S]*?(\d\d):(\d\d)", section)
			show["start"] = date.replace(hour=int(temp.group(1)), minute=int(temp.group(2)), second=0, microsecond=0)
			if show["start"] < laststart:
				date += datetime.timedelta(days=1)
				show["start"] += datetime.timedelta(days=1)

			if (show["start"] - now).total_seconds() / 3600 > timespan:
				lastshow = True
			else:
				lastshow = False

			laststart = show["start"]

			show["title"] = helper.cleanup(re.search("<span class=\"title[\s\S]*?>\s*([^<]*?)[\t\n]", section).group(1))
			temp = re.search("<span class=\"subtitle[\s\S]*?>\s*([^<]*?)[\t\n]", section)
			if temp is not None:
				subtitle = temp.group(1)
				if subtitle:
					show["sub-title"] = helper.cleanup(subtitle)

			temp = re.search("<a class=\"sendungslink[\s\S]*?href=\"(.*?)\"", section)
			if temp is not None:
				show["details-url"] = "http://programm.ard.de" + temp.group(1)
			shows.append(show)
			if lastshow:
				return shows
	return shows


def grabdetails(url):
	text = helper.download(url)
	if text is None:
		return None
	show = {}
	description = helper.cut(text, "<meta name=\"description\" content=\"", "\" />")
	if description is not None:
		show["desc"] = helper.cleanup(description)
	return show


def channellist():
	text = helper.download("http://programm.ard.de/")
	channels = helper.split(text, "Tagesprogramm::", "</a>")
	result = []
	for channel in channels:
		temp = re.search("Tagesprogramm::(.*?)\".*\?sender\=-?(.*?)\&", channel)
		result.append((temp.group(2), temp.group(1), temp.group(1)))
	return result
