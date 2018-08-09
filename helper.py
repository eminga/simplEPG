# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 eminga
# Licensed under MIT License

import re, six
from time import sleep
from socket import timeout
from ssl import SSLError
from six.moves import urllib
from six.moves.html_parser import HTMLParser

def split(text, begin, end):
	result = []
	i = 0
	while True:
		i = text.find(begin, i)
		if i == -1:
			return result
		j = text.find(end, i)
		if j== -1:
			return result
		result.append(text[i:j+len(end)])
		i = j + len(end)
	return result

def cut(text, begin, end):
	i = text.find(begin)
	if i == -1:
		return None
	i += len(begin)
	j = text.find(end, i)
	if j == -1:
		return None
	return text[i:j]

def cleanup(text):
	if text is not None and text:
		h = HTMLParser()
		text = h.unescape(text)
		text = re.sub("<[\s\S]*?>", "", text)
		text = re.sub("\t", " ", text)
		text = re.sub("\s*$", "", text)
		text = re.sub("^\s*", "", text)
		text = re.sub(" {2,}", " ", text)
		text = re.sub("\n{2,}", "\n", text)
	return text

def check_robots(url):
	parsed = urllib.parse.urlparse(url)
	robotsurl = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
	try:
		rp = robots_cache[robotsurl]
	except KeyError:
		rp = urllib.robotparser.RobotFileParser()
		rp.set_url(robotsurl)
		try:
			rp.read()
		except (urllib.error.URLError, timeout, SSLError):
			rp = None
		robots_cache[robotsurl] = rp
	if rp is None:
		return True
	return rp.can_fetch("simplEPG/0.1", url)

robots_cache = {}

def download(url, encoding=None, useragent="simplEPG/0.1", ignore_robots=False, attempts=3):
	if not ignore_robots and not check_robots(url):
		print("Error: The site's robots.txt doesn't allow crawling.")
		return None
	request = urllib.request.Request(url, headers = {"User-Agent": useragent})
	try:
		response = urllib.request.urlopen(request, timeout=10)
	except (urllib.error.URLError, timeout, SSLError) as e:
		print("\nAn error occurred when trying to open " + url)
		print(e)
		if attempts > 1:
			print("Trying again in 10 seconds. " + str(attempts - 1) + " attempts left.")
		else:
			return None
		sleep(10)
		return download(url, encoding, useragent, ignore_robots, attempts - 1)

	# try to get encoding from http header if not explicitly specified	
	if encoding is None:
		if six.PY3:
			enc = response.headers.get_content_charset()
		else:
			enc = response.headers.getparam("charset")
		if enc:
			encoding = enc
		else:
			encoding = "utf-8"

	result = response.read().decode(encoding, "ignore")

	return result
