# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 01:05:56 2017

@author: Avneesh Srivastava
"""
from HTMLParser import HTMLParser
import re
import json
import traceback
class ScraperWrapper(HTMLParser):
    '''
        This is the HTML parser where we need to scrape the
        Instagram XHTML response for the repsonse data. 
    '''
    def __init__(self):
        HTMLParser.__init__(self)
        self.inLink = False
        self.dataJson = None
        self.lasttag = None
        self.lastname = None
        self.lastvalue = None
        self.dataIds = None

    def handle_starttag(self, tag, attrs):
        self.inLink = False
        if tag == 'script':
            for name, value in attrs:
                if name == 'src' and  "en_US_Commons" in value:
                    self.dataIds = value
                self.inLink = True
                self.lasttag = tag
            

    def handle_endtag(self, tag):
        if tag == "script":
            self.inlink = False

    def handle_data(self, data):
        if self.lasttag == 'script' and self.inLink and data.strip() and re.search(r'window._sharedData', data) is not None:
            try:
                self.dataJson = json.loads(re.sub(r'\n','', data[data.find('{'):data.rfind('}')+1],flags=re.IGNORECASE))
            except Exception as err:
                self.dataJson = dict([('error', str(err))])
                traceback.print_exception()
            