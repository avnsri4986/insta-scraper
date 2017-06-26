# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 00:33:56 2017

@author: Avneesh Srivastava
"""
from flask import Flask, jsonify, request
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
    
@app.route('/query_next', methods=['POST'])
def getNextMedia():
    response_msg = {}
    try:
        if request.json is not None:
            json_object = request.json
            if 'query_urls' in json_object:
                query_urls = json_object['query_urls']
                response_msg = a.getNextSetOfData(query_urls)
                if response_msg is None:
                    response_msg = dict([('error','Failed to communicate with Query URLS'),('error_code','QUERY_URL_COMMUNICATION_ERROR')])
            else:
                response_msg = dict([('error','Query URLs not present'),('error_code','QUERY_URL_ABSENT')])
    except Exception as err:
        response_msg = dict([('error',str(err)),('error_code','JSON_PARSE_ERROR')])
    return jsonify(response_msg)
        

if __name__ == '__main__':
    app.run(threaded=True)
