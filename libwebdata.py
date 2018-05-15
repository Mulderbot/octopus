#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import hashlib
import base64
import uuid
from Crypto import Random
from Crypto.PublicKey import RSA
import html2text
import re
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pymysql
import requests
import urllib.parse


class libwebdata:
	def __init__(self):
		self.publickey_file = "public_key.pub"
		self.privatekey_file = "private_key.pem"

		return


	### ENCRYPT AND HASH FUNCTIONS ###

	# -- create a salted hash for a word --
	def salted_hash(self, word):
		salt = base64.urlsafe_b64encode(uuid.uuid4().bytes)
		dsalt = salt.decode()

		salt_comb = (word+dsalt).encode('utf-8')

		hashed_w = hashlib.sha256(salt_comb).digest()
		hashed_word = base64.urlsafe_b64encode(hashed_w)

		return hashed_word


	# -- encrypt a word --
	def encrypt_word(self, word):
		fp = open(self.publickey_file, "r")
		publickey = RSA.importKey(fp.read())
		fp.close()

		encrypted_word = publickey.encrypt(word.encode('utf-8'), 32)[0]
		encoded_encrypted_word = base64.b64encode(encrypted_word)

		return encoded_encrypted_word


	# -- decrypt a word --
	def decrypt_word(self, enc_word):
		fp = open(self.privatekey_file, "r")
		privatekey = RSA.importKey(fp.read())
		fp.close()

		decoded_encrypted_word = base64.b64decode(enc_word)
		decrypted_word = privatekey.decrypt(decoded_encrypted_word)

		return decrypted_word


	### DATABASE FUNCTIONS ###

	# -- open database --
	def open_db(self):
		bbdd = pymysql.connect(host = "localhost", user = "juanlu",
					passwd = "", db = "octopus", 
					use_unicode=True, charset="utf8")
		sql = bbdd.cursor()

		return bbdd, sql


	# -- insert into table --
	def insert_table(self, data, table):
		bbdd, sql = self.open_db()

		for i in data:
			query = ("INSERT INTO {0} (").format(table)
			for n in i.keys():
				query += n+","
			query = query[0:-1]

			query += ") VALUES ("

			for n in i.keys():
				query += "'"+str(i[n])+"',"
			query = query[0:-1]

			query += ");"
			print(query)
			sql.execute(query)

		bbdd.commit()

		bbdd.close()

		return


	# -- update word --
	def update_word(self, encrypted_word):
		bbdd, sql = self.open_db()

		query = ("""UPDATE top_words SET count = count + 1 
			WHERE encrypted_word='{0}';""").format(encrypted_word)
		print(query)
		sql.execute(query)
		bbdd.commit()

		bbdd.close()

		return


	# -- update sentiment --
	def update_sentiment(self, sentiment, url):
		bbdd, sql = self.open_db()

		query = ("""UPDATE sentiment SET sentiment={0} 
			WHERE encrypted_word='{1}';""").format(sentiment, url)
		print(query)
		sql.execute(query)
		bbdd.commit()

		bbdd.close()

		return


	# -- get word from top words --
	def get_word(self, encrypted_word):
		bbdd, sql = self.open_db()

		query = ("""SELECT * FROM top_words 
			WHERE encrypted_word='{0}';""").format(encrypted_word)
		print(query)
		sql.execute(query)
		tuplas = sql.fetchall()

		bbdd.close()

		return tuplas


	# -- get url from sentiment --
	def get_url(self, url):
		bbdd, sql = self.open_db()

		query = ("""SELECT * FROM sentiment 
			WHERE url='{0}';""").format(url)
		print(query)
		sql.execute(query)
		tuplas = sql.fetchall()

		bbdd.close()

		return tuplas


	# -- get top words --
	def get_top_words(self):
		bbdd, sql = self.open_db()

		query = "SELECT * FROM top_words ORDER BY count DESC;"
		print(query)
		sql.execute(query)
		tuples = sql.fetchall()

		return tuples


	# -- get urls and sentiment --
	def get_sentiment(self):
		bbdd, sql = self.open_db()

		query = "SELECT * FROM sentiment;"
		print(query)
		sql.execute(query)
		tuples = sql.fetchall()

		return tuples


	### HTML & TEXT FUNCTIONS ###

	# -- strip html and clean  page --
	def clean_page(self, page):
		# -- strip html --
		h = html2text.HTML2Text()
		text = h.handle(page).lower()

		# -- clean text and get words --
		text = re.sub(r'\W+', ' ', text)
		while text.find("  ") >= 0:
			text = re.sub('  ', ' ', text)

		print("TEXT:")
		print(text)

		return text 


	# -- get words from text --
	def get_words(self, text):
		tmpwords = {}
		finalwords = []
		words = []

		# -- count words --
		for i in text.split(' '):
			if i not in tmpwords:
				tmpwords[i] = 1
			else:
				tmpwords[i] += 1

		# -- add to simple array and sort --
		for i in tmpwords.keys():
			finalwords.append([tmpwords[i], i])

		finalwords.sort()
		finalwords.reverse()

		# -- get only the first 100 words or less --
		limit = len(finalwords)
		if limit > 100:
			limit = 100

		for i in range(0, limit):
			words.append(finalwords[i])

		return words


	# -- classificate word in noun, verb or something else --
	def get_word_type(self, word):
		word_type = ""

		word_token = nltk.word_tokenize(word)
		w_type = nltk.pos_tag(word_token)

		if len(w_type) > 0:
			if len(w_type[0]) > 1:
				if w_type[0][1].find("NN") >= 0:
					word_type = "noun"
				if w_type[0][1].find("VB") >= 0:
					word_type = "verb"

		return word_type


	# -- make a tag cloud image --
	def get_word_cloud(self, text):
		# -- create wordcloud from text --
		wordcloud = WordCloud(max_font_size=75).generate(text)
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis("off")
		#plt.figure()
		plt.show()

		return


	### SUPER FUNCTIONS ###

	# -- process web page and insert words --
	def process_search(self, url, page):
		data = []
		data_url = []

		# -- clean page an get words --
		print("PASA POR AQUI! 1")
		text = self.clean_page(page)
		words = self.get_words(text)

		# -- get hashed and encrypted word and get into db --
		for i in words:
			word_hash = self.salted_hash(i[1]).decode()
			encrypted_word = self.encrypt_word(i[1]).decode()

			result = self.get_word(encrypted_word)
			if len(result) == 0:
				data.append({
					'word_hash': word_hash,
					'encrypted_word': encrypted_word,
					'count': i[0]
				})
			else:
				self.update_word(encrypted_word)

		if len(data) > 0:
			self.insert_table(data, "top_words")

		# -- make sentiment analysis --
		sentimet = "positive"
		enctext = urllib.parse.quote_plus(text)
		url = "https://api.wit.ai/message?v=20170307&verbose=true&q="+enctext
		headers = {
			'Authorization': 'Bearer UCRHLJFIYZ34NW67BVY32ITCI6VDSQQW',
			'Content-Type': 'application/json'
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		if 'intent' in result['entities']:
			if 'value' in result['entities']['intent']:
				sentiment = result['entities']['intent']['value']

		# -- store url with sentiment --
		url_hash = self.salted_hash(url).decode()

		result = self.get_url(url)
		if len(result) == 0:
			data_url.append({
				'url_hash': url_hash,
				'url': url,
				'sentiment': sentiment
			})
			self.insert_table(data_url, "sentiment")
		else:
			self.update_sentiment(sentiment, url)

		# ------ create wordcloud -------


		return words
		

	# -- list words and urls on page admin --
	def admin_data(self):
		top_words = []
		sentiment = []

		orig_top_words = self.get_top_words()
		sentiment = self.get_sentiment()

		for i in orig_top_words:
			word = self.decrypt_word(i[1]).decode()
			if self.get_word_type(word) != "":
				top_words.append([word, i[2]])

		return {'words': top_words, 'urls': sentiment}


#if __init__ == "__main__":
#	pass


