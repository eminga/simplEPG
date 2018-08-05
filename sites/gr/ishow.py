# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, re, helper

def grab(channel, timespan):
	tz = pytz.timezone("Europe/Athens")
	now = datetime.datetime.now(tz)
	shows = []
	a = 0
	if now.time().hour < 4:
		a = -1
	for i in range(a, 6):
		date = now + datetime.timedelta(days=i)
		text = helper.download("http://ishow.gr/showTodayChannelProgramm.asp?cid=" + channel + "&gotoDay=" + str(i))
		if text is None:
			continue

		sections = helper.split(text, "<tr id=\"progTr", "</tr>")
		laststart = datetime.datetime.min.replace(tzinfo=tz)
		for section in sections:
			show = {}

			temp = re.search("<td class=\"progTd progTdTime\".*?>(\d\d):(\d\d)", section)
			show["start"] = date.replace(hour=int(temp.group(1)), minute=int(temp.group(2)), second=0, microsecond=0)
			if show["start"] < laststart:
				date += datetime.timedelta(days=1)
				show["start"] += datetime.timedelta(days=1)

			if (show["start"] - now).total_seconds() / 3600 > timespan:
				lastshow = True
			else:
				lastshow = False

			laststart = show["start"]

			title = re.search("<div class=\"grandTitle\".*>(.+)</div>", section)			
			show["title"] = helper.cleanup(title.group(1))

			subtitle = helper.cut(section, "<div class=\"subTitle\">", "</div>")
			if subtitle is not None and subtitle:
				show["sub-title"] = helper.cleanup(subtitle)

			temp = re.search("<div class=\"grandTitle\">.*?href=\"(.*?)\"", section)
			if temp is not None:
				show["details-url"] = "http://ishow.gr" + temp.group(1)

			shows.append(show)
			if lastshow:
				return shows
	return shows


def grabdetails(url):
	text = helper.download(url)
	if text is None:
		return None
	show = {}
	description = helper.cut(text, "<meta property=\"og:description\" content=\"", "/>")
	temp = re.search("<meta property=\"og:description\" content=\"(.*?)(?:\"/>|<)", text)						
	if temp is not None:
		description = temp.group(1)
		if description:
			show["desc"] = helper.cleanup(description)
	return show

# doesn't capture all channels yet
def channellist():
	text = helper.download("http://www.ishow.gr/tvNow.asp")
	channels = helper.split(text, "<b><a style=\"color:#E1D8BE\"", "</a>")
	result = []
	for channel in channels:
		temp = re.search("\?cid=(.*?)\">(.*)</a>", channel)
		result.append((temp.group(1), temp.group(2), temp.group(2)))
	result.sort(key = lambda r: int(r[0]))
	return result
