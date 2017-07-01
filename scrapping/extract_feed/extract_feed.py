import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib2
import json
import datetime
import csv
import time

access_token = ""

def testFacebookFeedData(id, access_token):
	base = "https://graph.facebook.com/v2.9"
	node = "/" + id
	parameters = "/?access_token=%s" % access_token
	url = base + node + parameters

	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	data = json.loads(response.read())

	print json.dumps(data, indent = 4, sort_keys = True)

testFacebookFeedData("me", access_token)

def requestData(url):
	req = urllib2.Request(url)
	success = False
	while success is False:
		try:
			response = urllib2.urlopen(req)
			if response.getcode() == 200:
				success = True
		except Exception, e:
			print e
			time.sleep(5)

			print "Error For URL {0} : {1}".format(url, datetime.datetime.now())

	return response.read()

def getFacebookFeedData(id, access_token, num_feed = 1):
	base = "https://graph.facebook.com/v2.9"
	node = "/" + id
	parameters = "?fields=feed{message,story,created_time,reactions.limit(500){name,pic_large},likes{name,pic_large},type}&access_token=%s" % (access_token)
	url = base + node + parameters

	data = json.loads(requestData(url))
	# print json.dumps(data, indent = 4, sort_keys = True)
	return data

# getFacebookFeedData("me", access_token, 1)

def processFacebookFeedReaction(feed):
	reactions = 0
	has_next_like_page = True

	try:
		feed_reactions_data = feed["reactions"]["data"]
		feed_reactions_paging = feed["reactions"]

		# while has_next_like_page:
		# 	for data in feed_reactions_data:
		# 		reactions += 1

		# 	if "paging" in feed_reactions_paging.keys() and "next" in feed_reactions_paging["paging"].keys():
		# 		print "---------- Getting Reaction Paging ----------"
		# 		feed_reactions_data = json.loads(requestData(feed_reactions_paging["paging"]["next"]))
		# 		feed_reactions_paging = feed_reactions_data
		# 		feed_reactions_data = feed_reactions_data["data"]
		# 	else:
		# 		has_next_like_page = False

		# return reactions
		reactions =  len(feed_reactions_data)
	except Exception, e:
		reactions = 0

	return reactions

def processFacebookFeedData(feed):
	feed_id = feed["id"]
	feed_created = feed["created_time"]
	feed_story = "" if "story" not in feed.keys() else feed["story"].encode('utf-8')
	feed_message = "" if "message" not in feed.keys() else feed["message"].encode('utf-8')
	feed_type = feed["type"]

	print feed_story
	print feed_message

	feed_reactions = processFacebookFeedReaction(feed)
	# feed_reactions = 0
	print feed_reactions

	return (feed_id, feed_created, feed_type, feed_reactions)
	

def scrapFacebookFeedData(id, access_token):
	with open("facebookFeed.csv", "wb") as file:
		w = csv.writer(file)
		w.writerow(["id", "created_time", "type", "reactions"])

		has_next_page = True
		data_processed = 0
		scrape_start_time = datetime.datetime.now()

		print "Scraping Facebook Feed Page: %s" % (scrape_start_time)
		feed_data = getFacebookFeedData(id, access_token)

		feeds = feed_data["feed"]["data"]
		feed_paging = feed_data["feed"]

		while has_next_page:
			for feed in feeds:
				w.writerow(processFacebookFeedData(feed))
				data_processed += 1
				if data_processed % 1000 == 0:
					print "Feed Processed: %s" %(data_processed)

				print "------------------------------------------------"


			if "paging" in feed_paging.keys() and "next" in feed_paging["paging"].keys():
				print "---------- Getting Next Feed Page ----------"
				feeds = json.loads(requestData(feed_paging["paging"]["next"]))
				feed_paging = feeds
				feeds = feeds["data"]
			else:
				has_next_page = False

	print "Feed Processed In : %s" % (datetime.datetime.now() - scrape_start_time)

# scrapFacebookFeedData("me", access_token)
			
def plotFacebookFeedData():
	x = []
	y = []

	with open('facebookFeed.csv', 'r') as file:
		plots = csv.reader(file, delimiter = ',')
		for row in plots:
			x.append(datetime.datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S+0000"))			
			y.append(int(row[3]))

	fig = plt.figure()
	ax1 = fig.add_subplot(1, 1, 1, axisbg='white')
	ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%dT%H:%M:%S+0000"))
	ax1.plot(x, y, 'c', linewidth=1, label = "My Feed Line")

	plt.title('Facebook Feed Likes Over Years')
	plt.xlabel('Till Today -------->')
	plt.ylabel("Number Of Likes -------->")
	fig.autofmt_xdate(rotation=90)
	fig.tight_layout()
	plt.show()
plotFacebookFeedData()
