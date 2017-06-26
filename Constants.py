# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 00:27:49 2017

@author: Avneesh Srivastava
"""
import logging

#Instgram related Properties
INSTAGRAM_BASE_URL = 'https://www.instagram.com'
INSTAGRAM_QUERY_URL= 'graphql/query?query_id={0}&tag_name={1}&first=100&after={2}'
INSTAGRAM_QUERY_BY_HASHTAG='https://www.instagram.com/explore/tags/{0}'

#Logger
FORMAT = '%(asctime)-0s : [%(filename)s L%(lineno)d] - %(funcName)s() %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging