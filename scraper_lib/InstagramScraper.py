# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 00:41:25 2017

@author: Avneesh Srivastava
"""
import Constants
from scraper_lib.ScraperWrapper import ScraperWrapper
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import os
import requests
import re
import json
class InstagramScraper:
    logger = None
    constants = None
    def __init__(self):
        self.constants = Constants
        self.logger = self.constants.LOGGER
        self.logger.info("Instagram Scraper Initialized")
        
    def getProxy(self):
        '''
            If the user is behind a corporate network then we can read
            the proxy properties from the environment and use it to 
            make HTTP Requests.
        '''
        proxy = dict([('http',  os.getenv('HTTP_PROXY', os.getenv('http_proxy', ''))),('https',  os.getenv('HTTPS_PROXY', os.getenv('https_proxy', '')))])
        self.logger.info(('Proxy Configuration: %s')%(proxy))
        return proxy
    
    def getPossibleQueryURLs(self, parser):
        '''
            Create possible Query URLs for querying further. 
            This part is mainly for pagination related purpose.
            Ideal process is - scraping the instagram response data
            for the given username, extract the JS file and search for possible
            query IDs and send it further with end cursor for querying the next page of data
            until there is no next page available.
        '''
        possible_query_urls = []
        self.logger.info('Creating possible query URLs for fetching next batch of data.')
        if parser.dataJson is not None:
            if parser.dataJson['entry_data']['ProfilePage'][0]['user']['media']['page_info']['has_next_page']:
                user_search_id = parser.dataJson['entry_data']['ProfilePage'][0]['user']['id']
                self.logger.debug(('Instagram User Data ID = %s')%(user_search_id))
                end_cursor = parser.dataJson['entry_data']['ProfilePage'][0]['user']['media']['page_info']['end_cursor']
                self.logger.debug(('End Cursor ID = %s')%(end_cursor))
                query_url = ('%s%s')%(self.constants.INSTAGRAM_BASE_URL, parser.dataIds)
                response_text = requests.get(query_url, proxies = self.getProxy()).text
                query_ids = (re.findall("(?<=queryId:\")[0-9]{17,17}", response_text))
                for query_id in query_ids:
                    possible_query_urls.append(('%s/graphql/query/?query_id=%s&id=%s&first=12&after=%s')%(self.constants.INSTAGRAM_BASE_URL, query_id, user_search_id, end_cursor))
                self.logger.info(("Possible Query URLS = %s")%(len(possible_query_urls)))
        return possible_query_urls
        
    
    def queryInstagram(self, username):
        '''
            Query Instagram for a particular username. Ideally, in a perfect 
            case scenario the user sends us a particular username for which 
            we scrape instagram response for valid JSON data.
        '''
        self.logger.info(("Querying Instagram for Username: %s")%(username))
        url_usersearch = ('%s/%s')%(self.constants.INSTAGRAM_BASE_URL, username)
        https_request = requests.get(url_usersearch, verify = False, proxies = self.getProxy())
        if https_request.status_code == 200:
            parser = ScraperWrapper()
            parser.feed(https_request.text)
            parser.close()
            user_instagram_data = parser.dataJson['entry_data']['ProfilePage'][0]['user']
            user_instagram_data['query_urls'] = self.getPossibleQueryURLs(parser)
        else:
            #Error Code Update
            if https_request.status_code == 404:
                error_code = 'USERNAME_NOT_FOUND'
                error = 'Failed to fetch user information. The username does not exist.'
            else:
                error_code = 'SERVER_COMMUNICATION_ERROR'
                error = 'Failed to communicate with Instagram server'
            #Error JSON
            user_instagram_data = dict([('error',error),('error_code', error_code),('url', url_usersearch),('status_code', https_request.status_code),('response', https_request.text)])
        return user_instagram_data
    
    def getNextSetOfData(self, query_urls):
        self.logger.info(("Querying data for the next page, total query URLs = %s")%(len(query_urls)))
        response_object = None
        pool = ThreadPoolExecutor(max_workers=10)
        if len(query_urls) > 0:
            futures = []
            for query_url in query_urls:
                futures.append(pool.submit(requests.get, query_url, verify = False, proxies = self.getProxy()))
            results = [r.result() for r in as_completed(futures)]
            for https_request in results:
#                https_request = requests.get(query_url, verify = False, proxies = self.getProxy())
                if https_request.status_code == 200:
                    json_object = json.loads(https_request.text)
                    if 'data' in json_object and 'user' in json_object['data'] and json_object['data']['user'] is not None:
                        if json_object['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] is True:
                            query_url = query_url.split('&after=')
                            query_url[len(query_url)-1] = json_object['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                            query_url = '&after='.join(map(str,query_url))
                            json_object['query_urls'] = [query_url]
                        response_object =  json_object
                        break;
        return response_object;
                        
        
                
        
