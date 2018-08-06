# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import datetime, pytz, re, helper

def grab(channel, timespan):
	tz = pytz.timezone("Europe/Athens")
	now = datetime.datetime.now(tz)
	charset = "windows-1253"
	shows = []
	a = 0
	if now.time().hour < 7:
		a = -1
	for i in range(a, 14):
		date = now + datetime.timedelta(days=i)
		text = helper.download("http://program.ert.gr/Ert1/index.asp?id=" + channel + "&pdate=" + date.strftime("%d/%m/%Y"), encoding=charset)
		if text is None:
			continue

		sections = helper.split(text, "<td width=\"50\" align=\"center\" class=\"table\">", "</tr></table>")
		laststart = datetime.datetime.min.replace(tzinfo=tz)
		for section in sections:
			show = {}

			temp = re.search("(\d\d):(\d\d)", section)
			show["start"] = date.replace(hour=int(temp.group(1)), minute=int(temp.group(2)), second=0, microsecond=0)
			if show["start"] < laststart:
				date += datetime.timedelta(days=1)
				show["start"] += datetime.timedelta(days=1)

			if (show["start"] - now).total_seconds() / 3600 > timespan:
				lastshow = True
			else:
				lastshow = False

			laststart = show["start"]

			temp = re.search("<a class=\"black\".*href=\"(.*)\">(.*)</a>", section)

			show["title"] = temp.group(2)

			subtitle = helper.cut(section, "<td width=\"3\"></td><td><font color=\"#6e6868\">", "</font>")
			if subtitle is not None and subtitle:
				show["sub-title"] = subtitle

			link = temp.group(1)
			if link[0] == "/":
				link = "http://program.ert.gr" + link
			if link:
				show["details-url"] = link

			shows.append(show)
			if lastshow:
				return shows
	return shows


def grabdetails(url):
	charset = "windows-1253"
	text = helper.download(url, encoding=charset)
	if text is None:
		return None
	show = {}
	temp = helper.split(text, "<div align=\"justify\" class=\"black\">", "</div>")
	description = ""
	for d in temp:
		description += d
	if description:
		show["desc"] = helper.cleanup(description)
	director = re.search("Σκηνοθεσία</b>: (.*?)(?:\n|<br>)", text)
	if director is not None:
		show["director"] = helper.cleanup(director.group(1))
	presenter = re.search("Παρουσίαση</b>: (.*?)(?:\n|<br>)", text)
	if presenter is not None:
		show["presenter"] = helper.cleanup(presenter.group(1))
	producer = re.search("Οργάνωση παραγωγής: (.*?)(?:\n|<br>)", text)
	if producer is not None:
		show["producer"] = helper.cleanup(producer.group(1))
	writer = re.search("Αρχισυνταξία: (.*?)(?:\n|<br>)", text)
	if writer is not None:
		show["writer"] = helper.cleanup(writer.group(1))
	return show
