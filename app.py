#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPClient
import libwebdata


lwd = libwebdata.libwebdata()


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("static/index.html", title="Web Search Test")


class SearchHandler(tornado.web.RequestHandler):
	def fetch_url(self, url):
		http_client = HTTPClient()
		response = http_client.fetch(url)

		return response.body

	def get(self):
		url = self.get_query_argument("s")
		page = self.fetch_url(url)

		fp = open("test.html", "wb")
		fp.write(page)
		fp.close()

		words = lwd.process_search(url, page)
		#data = {'url': url, 'words': words}

		#self.render("static/search.html", title="Web Search Results", items=data)
		self.write("?")


class AdminHandler(tornado.web.RequestHandler):
	def get(self):
		data = lwd.admin_data()
		self.render("static/admin.html", title="Admin Search Results", items=data)



app = tornado.web.Application([
	(r"/", MainHandler),
	(r"/search.html", SearchHandler),
	(r"/admin.html", AdminHandler)
	], debug=True)

if __name__ == "__main__":
	app.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
