#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import xml.etree.cElementTree as ET, datetime, pytz, importlib, json, sys

# adds the given element to the xml
def add_generic(parent, tag, element, attribute=None, allow_lists=True):
	if allow_lists and type(element) is list:
		for entry in element:
			add_generic(parent, tag, entry, attribute, False)
	elif attribute and type(element) is tuple and element[1]:
		e = ET.SubElement(parent, tag, {attribute: element[1]})
		if type(element[0]) in {str, int, float}:
			e.text = str(element[0])
	elif type(element) is tuple and type(element[1]) is dict:
		e = ET.SubElement(parent, tag, element[1])
		if type(element[0]) in {str, int, float}:
			e.text = str(element[0])
	else:
		e = ET.SubElement(parent, tag)
		if type(element) in {str, int, float}:
			e.text = str(element)

def add_icon(parent, element):
	if type(element) is list:
		for entry in element:
			add_icon(parent, entry)
	elif type(element) is tuple:
		icon = {"src": element[0]}
		if "width" in element[1]:
			icon["width"] = str(element[1]["width"])
		if "height" in element[1]:
			icon["height"] = str(element[1]["height"])
		add_generic(parent, "icon", (None, icon), allow_lists=False)
	else:
		add_generic(parent, "icon", (None, element), "src", False)

def add_subtitles(parent, element):
	if type(element) is list:
		for entry in element:
			add_subtitles(parent, entry)
	else:
		subtitles = ET.SubElement(parent, "subtitles")
		if "type" in element and element["type"] in ("teletext", "onscreen", "deaf-signed"):
			subtitles.set("type", element["type"])
		if "language" in element:
			language = element["language"]
		else:
			language = None
		if "lang" in element:
			add_generic(subtitles, "language", (language, element["lang"]), "lang", False)
		elif language is not None:
			add_generic(subtitles, "language", language, allow_lists=False)

def add_rating(parent, element, star=False):
	if type(element) is list:
		for entry in element:
			add_rating(parent, entry, star)
	else:
		if star:
			rating = ET.SubElement(parent, "star-rating")
		else:
			rating = ET.SubElement(parent, "rating")
		if type(element) is tuple:
			if "system" in element[1]:
				rating.set("system", element[1]["system"])
			add_generic(rating, "value", element[0], allow_lists=False)
			if "icon" in element[1]:
				add_icon(rating, element[1]["icon"])
		else:
			add_generic(rating, "value", element, allow_lists=False)

def add_review(parent, element):
	if type(element) is list:
		for entry in element:
			add_review(parent, entry)
	elif element[1] in ("text", "url"):
		review = ET.SubElement(parent, "review")
		review.text = element[0]
		review.set("type", element[1])
		if len(element) > 2:
			if "source" in element[2]:
				review.set("source", element[2]["source"])
			if "reviewer" in element[2]:
				review.set("reviewer", element[2]["reviewer"])
			if "lang" in element[2]:
				review.set("lang", element[2]["lang"])

def process_show(programme, show):
	add_generic(programme, "title", show["title"], "lang")
	if "sub-title" in show:
		add_generic(programme, "sub-title", show["sub-title"], "lang")
	if "desc" in show:
		add_generic(programme, "desc", show["desc"], "lang")

	if {"director", "actor", "writer", "adapter", "producer", "composer", "editor", "presenter", "commentator", "guest"}.intersection(show):
		credits = ET.SubElement(programme, "credits")
		if "director" in show:
			add_generic(credits, "director", show["director"])
		if "actor" in show:
			add_generic(credits, "actor", show["actor"], "role")
		if "writer" in show:
			add_generic(credits, "writer", show["writer"])
		if "adapter" in show:
			add_generic(credits, "adapter", show["adapter"])
		if "producer" in show:
			add_generic(credits, "producer", show["producer"])
		if "composer" in show:
			add_generic(credits, "composer", show["composer"])
		if "editor" in show:
			add_generic(credits, "editor", show["editor"])
		if "presenter" in show:
			add_generic(credits, "presenter", show["presenter"])
		if "commentator" in show:
			add_generic(credits, "commentator", show["commentator"])
		if "guest" in show:
			add_generic(credits, "guest", show["guest"])

	if "date" in show:
		add_generic(programme, "date", show["date"], allow_lists=False)
	if "category" in show:
		add_generic(programme, "category", show["category"], "lang")
	if "keyword" in show:
		add_generic(programme, "keyword", show["keyword"], "lang")
	if "language" in show:
		add_generic(programme, "language", show["language"], "lang", False)
	if "orig-language" in show:
		add_generic(programme, "orig-language", show["orig-language"], "lang", False)
	if "length" in show:
		length = show["length"]
		if length[1] in ("seconds", "minutes", "hours"):
			add_generic(programme, "length", length, "units", False)
	if "icon" in show:
		add_icon(programme, show["icon"])
	if "url" in show:
		add_generic(programme, "url", show["url"])
	if "country" in show:
		add_generic(programme, "country", show["country"], "lang")
	if "episode-num" in show:
		add_generic(programme, "episode-num", show["episode-num"], "system")

	if {"videopresent", "colour", "aspect", "quality"}.intersection(show):
		video = ET.SubElement(programme, "video")
		if "videopresent" in show:
			add_generic(video, "present", show["videopresent"], allow_lists=False)
		if "colour" in show:
			add_generic(video, "colour", show["colour"], allow_lists=False)
		if "aspect" in show:
			add_generic(video, "aspect", show["aspect"], allow_lists=False)
		if "quality" in show:
			add_generic(video, "quality", show["quality"], allow_lists=False)

	if {"audiopresent", "stereo"}.intersection(show):
		audio = ET.SubElement(programme, "audio")
		if "audiopresent" in show:
			add_generic(audio, "present", show["audiopresent"], allow_lists=False)
		if "stereo" in show:
			add_generic(audio, "stereo", show["stereo"], allow_lists=False)

	if "previously-shown" in show:
		prev = show["previously-shown"]
		if type(prev) is dict:
			attr = {}
			if "start" in prev:
				attr["start"] = prev["start"]
			if "channel" in prev:
				attr["channel"] = prev["channel"]
			add_generic(programme, "previously-shown", (None, attr))
		else:
			add_generic(programme, "previously-shown", None)
	if "premiere" in show:
		add_generic(programme, "premiere", show["premiere"], "lang", False)
	if "last-chance" in show:
		add_generic(programme, "last-chance", show["last-chance"], "lang", False)
	if "new" in show and show["new"]:
		add_generic(programme, "new", None, allow_lists=False)
	if "subtitles" in show:
		add_subtitles(programme, show["subtitles"])
	if "rating" in show:
		add_rating(programme, show["rating"])
	if "star-rating" in show:
		add_rating(programme, show["star-rating"], True)
	if "review" in show:
		add_review(programme, show["review"])


# unfinished
def update_channellist(sitename):
	site = importlib.import_module('sites.' + sitename)
	cl = site.channellist()
	for site in cl:
		print("\t<channel site=\"" + sitename + "\" site_id=\"" + site[0] + "\" xmltv_id=\"" + site[1] + "\">" + site[2] + "</channel>")


# calls the scripts of the specified sites and creates the xmltv file
def create_epg(config):
	now = pytz.utc.localize(datetime.datetime.utcnow())
	timespan_global = int(config.find("timespan_index").text)
	timespan_full_global = int(config.find("timespan_full").text)

	caching_global = config.find("caching").text
	if caching_global in ("on", "yes", "true", "True"):
		caching_global = True
	else:
		caching_global = False

	try:
		timespan_force_global = int(config.find("timespan_force").text)
	except TypeError:
		timespan_force_global = -1

	try:
		with open("cached_epg.json") as fp:
			cache = json.load(fp)
	except IOError:
		cache = {}

	cache_new = {}

	# root element of epg
	tv = ET.Element("tv")
	tv.set("generator-info-name", "simplEPG v0.1")
	tv.set("generator-info-url", "https://github.com/eminga/simplEPG")

	for channel in config.findall("channel"):
		c = ET.SubElement(tv, "channel", id = channel.get("xmltv_id"))
		ET.SubElement(c, "display-name").text = channel.text


	for channel in config.findall("channel"):
		site = importlib.import_module('sites.' + channel.get("site"))
		channelid = channel.get("xmltv_id")
		print(channel.get("site") + ":" + channelid)

		try:
			timespan = int(channel.get("timespan_index"))
		except TypeError:
			timespan = timespan_global

		try:
			timespan_full = int(channel.get("timespan_full"))
		except TypeError:
			timespan_full = timespan_full_global

		try:
			caching = channel.get("caching")
			if caching is not None:
				if caching in ("on", "yes", "true", "True"):
					caching = True
				else:
					caching = False
			else:
				caching = caching_global
		except TypeError:
			caching = caching_global

		try:
			timespan_force = int(channel.get("timespan_force"))
		except TypeError:
			timespan_force = timespan_force_global
		if timespan_force == -1:
			timespan_force = -10000

		try:
			shows = site.grab(channel.get("site_id"), timespan)
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			shows = []
			print("An error occured:")
			print(sys.exc_info())


		if len(shows) > 0:
			# create progress bar if module is available
			try:
				from progress.bar import Bar
			except ImportError:
				class Bar:
					def __init__(self, label, max):
						self.max = max
						self.index = 0

					def next(self):
						self.index += 1

					def update(self):
						pass

					def finish(self):
						print("%s shows added." % self.index)


			bar = Bar("Processing", max=len(shows))


			shows.sort(key = lambda r: r["start"])

			for i in range(len(shows)):
				show = shows[i]
				if "stop" in show:
					stoptime = show["stop"]
				elif i < len(shows) - 1:
					stoptime = shows[i + 1]["start"]
				else:
					break

				# don't store shows that are already finished
				if stoptime < now:
					bar.max -= 1
					continue

				starttime = show["start"]
				# don't store shows that start more than "timespan" hours in the future
				if (starttime - now).total_seconds() / 3600 > timespan:
					break

				url = show.pop("details-url", None)
				if url is not None and len(url) > 0:
					if timespan_full > -1 and (starttime - now).total_seconds() / 3600 <= timespan_full:
						if caching and (starttime - now).total_seconds() / 3600 > timespan_force:
							force = False
							try:
								try:
									details = cache_new[url]
								except KeyError:
									details = cache[url]
								show.update(details)
								cache_new[url] = details
							except KeyError:
								force = True
						else:
							force = True
						if force:
							try:
								details = site.grabdetails(url)
								show.update(details)
								if caching:
									# don't store times in cache
									details.pop("start", None)
									details.pop("stop", None)
									cache_new[url] = details
							except (AttributeError, TypeError):
								pass
				programme = ET.SubElement(tv, "programme", start=starttime.strftime("%Y%m%d%H%M%S %z"), stop=stoptime.strftime("%Y%m%d%H%M%S %z"), channel=channelid)
				process_show(programme, show)
				bar.next()
			bar.max = bar.index
			bar.update()
			bar.finish()
		else:
			print("0 shows found.")
	if len(cache_new) > 0:
		with open("cached_epg.json", "w") as fp:
			cache = json.dump(cache_new, fp) 
	return tv

config = ET.parse("config.xml").getroot()
epg = create_epg(config)
filename = config.find("filename").text
ET.ElementTree(epg).write(filename, encoding="UTF-8", xml_declaration=True)
