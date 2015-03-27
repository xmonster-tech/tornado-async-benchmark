#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
import time

import tornado.ioloop
import tornado.web


EXECUTOR = ThreadPoolExecutor(max_workers=128)


def unblock(f):

	@tornado.web.asynchronous
	@wraps(f)
	def wrapper(*args, **kwargs):
		self = args[0]

		def callback(future):
			self.write(future.result())
			self.finish()

		EXECUTOR.submit(
			partial(f, *args, **kwargs)
		).add_done_callback(
			lambda future: tornado.ioloop.IOLoop.instance().add_callback(
				partial(callback, future)))

	return wrapper


class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.write("Hello, world %s" % time.time())


class SleepHandler(tornado.web.RequestHandler):

	@unblock
	def get(self, n):
		print "Awake! %s" % time.time()
		wastetime(100000)
		return "Awake! %s" % time.time()

class NormalSleepHandler(tornado.web.RequestHandler):

	def get(self, n):
		print "Awake! %s" % time.time()
		wastetime(100000)
		self.finish("hahahah")

class SleepAsyncHandler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	def get(self, n):

		def callback(future):
			self.write(future.result())
			self.finish()

		EXECUTOR.submit(
			partial(self.get_, n)
		).add_done_callback(
			lambda future: tornado.ioloop.IOLoop.instance().add_callback(
				partial(callback, future)))

	def get_(self, n):
		print "Awake! %s" % time.time()
		time.sleep(float(n))

		return "Awake! %s" % time.time()

def wastetime(i):
	res = 1
	for x in xrange(i):
		print x
		res *= i
	return res

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/sleep/(\d+)", SleepHandler),
	(r"/sleep_async/(\d+)", SleepAsyncHandler),
    (r"/s/(\d+)", NormalSleepHandler),
])


if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
