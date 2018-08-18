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
		text = helper.download("http://www.zdf.de/live-tv?airtimeDate=" + date.strftime("%Y-%m-%d"))
		if text is None:
			continue

		text = helper.cut(text, "<section class=\"b-epg-timeline timeline-" + channel, "</section>")

		sections = helper.split(text, "<li", "</li>")
		laststart = datetime.datetime.min.replace(tzinfo=tz)
		for section in sections:
			show = {}

			temp = helper.cut(section, "<span class=\"time\">", "</span>")
			temp = re.search("(\d\d):(\d\d) - (\d\d):(\d\d)", temp)	
			show["start"] = date.replace(hour=int(temp.group(1)), minute=int(temp.group(2)), second=0, microsecond=0)
			if show["start"] < laststart:
				date += datetime.timedelta(days=1)
				show["start"] += datetime.timedelta(days=1)

			if (show["start"] - now).total_seconds() / 3600 > timespan:
				return shows

			laststart = show["start"]
			show["stop"] = date.replace(hour=int(temp.group(3)), minute=int(temp.group(4)), second=0, microsecond=0)
			if show["stop"] < show["start"]:
				show["stop"] += datetime.timedelta(days=1)
			temp = re.search("<span class=\"overlay-link-category\">(.*?)<span class=\"visuallyhidden\">:</span></span>\s*(?:<.*>)*\s*(.*?)\s*?</a>", section)
			if temp.group(1):
				show["title"] = helper.cleanup(temp.group(1) + " - " + temp.group(2))
			else:
				show["title"] = helper.cleanup(temp.group(2))

			temp = re.search("contentUrl\": \"(.*)\"", section)
			if temp is not None:
				show["details-url"] = "http://www.zdf.de" + temp.group(1)

			shows.append(show)
	return shows


def grabdetails(url):
	text = helper.download(url)
	if text is None:
		return None
	show = {}
	subtitle = helper.cut(text, "<h3 class=\"overlay-subtitle\">", "</h3>")
	if subtitle is not None and subtitle:
		show["sub-title"] = helper.cleanup(subtitle)

	description = helper.cut(text, "<p class=\"overlay-text\">", "</p>")
	if description is not None and description:
		show["desc"] = helper.cleanup(description)

	if text.find("Untertitel für Hörgeschädigte") != -1:
		show["subtitles"] = True
	return show
