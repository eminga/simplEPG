import datetime, pytz, re, helper

def grab(channel, timespan):
	tz = pytz.timezone("UTC")
	now = datetime.datetime.now(tz)
	shows = []

	text = helper.download("http://m.tvtoday.de/programm/standard/sender/" + channel + ".html")
	sections = helper.split(text, "<li class=\"tv", "</li>")
	for section in sections:
		show = {}

		start = helper.cut(section, "data-start-time=\"", "\"")
		show["start"] = datetime.datetime.fromtimestamp(int(start), tz)

		if (show["start"] - now).total_seconds() / 3600 > timespan:
			break

		stop = helper.cut(section, "data-end-time=\"", "\"")
		show["stop"] = datetime.datetime.fromtimestamp(int(stop), tz)

		if show["stop"] < now:
			continue

		show["title"] = helper.cleanup(helper.cut(section, "<span class=\"tv-tip-heading\">", "</span>"))
		category = helper.cleanup(helper.cut(section, "<span class=\"genre\">", "</span>"))

		if ", " in category:
			category, produced = category.split(", ")
			temp = re.search("(?P<country>\S*)\s*(?P<year>\d{4})", produced)
			if temp is None:
				show["country"] = produced.split("/")
			else:
				show["date"] = temp.group("year")
				if temp.group("country"):
					show["country"] = temp.group("country").split("/")
		if category:
			show["category"] = category
		temp = re.search("<a href=\"(.*?)\" class=\"info-holder\">", section)
		if temp is not None:
			show["details-url"] = "http://m.tvtoday.de" + temp.group(1)

		shows.append(show)
	return shows


def grabdetails(url):
	text = helper.download(url)
	if text is None:
		return None
	show = {}

	description = helper.cut(text, "<div class=\"article-text\">", "</div>")
	description = description.split("<div")[0]
	description = helper.cleanup(description)
	if description is not None and description:
		show["desc"] = description

	director = helper.cut(text, "<dt>Regie:</dt>", "</dd>")
	director = helper.cleanup(director)
	if director is not None and director:
		show["director"] = director.split("; ")

	presenter = helper.cut(text, "<dt>Moderation:</dt>", "</dd>")
	presenter = helper.cleanup(presenter)
	if presenter is not None and presenter:
		show["presenter"] = presenter.split(", ")

	temp = helper.cut(text, "<span>Darsteller</span>", "</dl>")
	actors = []
	if temp is not None:
		temp = temp.split("</dd>")
		for x in temp:
			try:
				actor, role = x.split("<dd>")
				actors.append((helper.cleanup(actor), helper.cleanup(role)))
			except ValueError:
				pass
	if len(actors) > 0:
		show["actor"] = actors

	return show


def channellist():
	text = helper.download("http://m.tvtoday.de/sender")
	text = helper.cut(text, "<div class=\"component channels all-channels\">", "</ul>")
	channels = helper.split(text, "<li>", "</li>")
	result = []
	for channel in channels:
		temp = re.search("<a href=\".*\/(.*)\.html\" title=\"(.*?)\"", channel)
		result.append((temp.group(1), temp.group(2), temp.group(2)))
	return result
