# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 00:33:56 2017

@author: Avneesh Srivastava
"""
from flask import Flask, jsonify
import os
import Constants
from flask_compress import Compress
import datetime
from scraper_lib.InstagramScraper import InstagramScraper
#Constants
logger = Constants.LOGGER
port = int(os.getenv("VCAP_APP_PORT") or 5500)
#Flask App
app = Flask(__name__)
#GZIP Compression
Compress(app)
app.constants = Constants
a=InstagramScraper()

#Main Health Check Endpoint
@app.route('/')
def health_check():
	responseObject = dict([('status','OK'),('app_name','Instagram Scraper'),('time',datetime.datetime.now())])
	return jsonify(responseObject)

@app.route('/<username>')
def getCausecode(username):
    if username is not None:
        username = username.strip()
        return jsonify(a.queryInstagram(username))
    else:
        return jsonify(dict[('error','Invalid Username'),('error_code','INVALID_USERNAME')])

if __name__ == '__main__':
    app.run()
