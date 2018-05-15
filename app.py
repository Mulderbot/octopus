#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPClient
import libwebdata


lwd = libwebdata.libwebdata()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/index.html", title="Web Search Test")


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        url = self.get_query_argument("s")
        words = lwd.process_search(url)
        data = {'url': url, 'words': words}

       	self.render("static/search.html", title="Web Search Results", items=data)


class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        data = lwd.admin_data()
        self.render("static/admin.html", title="Admin Search Results", items=data)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}


app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/search.html", SearchHandler),
    (r"/admin.html", AdminHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': './static'}),
    ], debug=True, **settings)

if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
