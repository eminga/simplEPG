# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, re, time, helper

def grab(channel, timespan):
	tz = pytz.timezone("UTC")
	now = datetime.datetime.now(tz)
	shows = []

	laststart = datetime.datetime.min.replace(tzinfo=tz)
	for i in range(1 + timespan // 4):
		timestamp = int(time.time()) + i * 14400
		text = helper.download("https://www.dw.com/epg/data/4765/1/" + str(timestamp) + "000")
		if text is None:
			continue

		channeldata = helper.cut(text, "data-channel-id=\"" + channel + "\"", "data-channel-id")
		if not channeldata:
			try:
				channeldata = text.split("data-channel-id=\"" + channel + "\"")[1]
			except IndexError:
				continue
		sections = helper.split(channeldata, "<div class=\"epgProgram\"", "<div class=\"broadcastlinks\">")

		for section in sections:
			show = {}
			day = helper.cut(section, "data-day=\"", "\"")
			begintime = helper.cut(section, "data-begin-time=\"", "\"")
			endtime = helper.cut(section, "data-end-time=\"", "\"")

			show["start"] = pytz.utc.localize(datetime.datetime.strptime(day + begintime, "%Y-%m-%d%H:%M"))
			if show["start"] <= laststart:
				continue
			if (show["start"] - now).total_seconds() / 3600 > timespan:
				return shows
			laststart = show["start"]

			show["stop"] = pytz.utc.localize(datetime.datetime.strptime(day + endtime, "%Y-%m-%d%H:%M"))
			if show["stop"] < show["start"]:
				show["stop"] += datetime.timedelta(days=1)

			show["title"] = helper.cleanup(helper.cut(section, "<h2 class=\"title\">", "</h2>"))
			url = helper.cut(section, "<a href=\"", "\">")
			if url is not None and url:
				show["url"] = "https://www.dw.com" + url
			description = helper.cleanup(helper.cut(section, "<ul class=\"topics\">", "</ul>"))
			if description is not None and description:
				show["desc"] = description

			try:
				icon = re.search("<img[\s\S]*?/>", section).group(0)
				width = helper.cut(icon, "width=\"", "\"")
				height = helper.cut(icon, "height=\"", "\"")
				src = "https://www.dw.com" + helper.cut(icon, "src=\"", "\"")
				show["icon"] = (src, {"width": width, "height": height})
			except (AttributeError, IndexError):
				pass

			shows.append(show)
	return shows
