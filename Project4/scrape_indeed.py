#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 22:39:41 2018

@author: neilcabrera
"""
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# Web Driver Parameters
_URL = "https://www.indeed.com.sg/jobs?q=data+scientist&l=Singapore"
_WEBDRIVER_PATH = "/Users/cabre/OneDrive/Downloads/chromedriver.exe"
_PAGE_LOAD_TIMEOUT = 5

# Web Scraping Parameters
_JOB_RESULTS_ELEMENT_ID = 'resultsCol'
_JOB_LINK_SEARCH_PARAM1 = '/pagead/clk'
_JOB_LINK_SEARCH_PARAM2 = 'fccid'

_JOB_CONTAINER_ID = 'vjs-container'
_JOB_HEADER_ID = 'vjs-header'
_JOB_CONTENT_ID = 'vjs-content'

_JOB_PANEL_TIMEOUT = 5

_END_OF_RESULTS = False
_PAGINATION_CLASS_NAME = 'pagination'
_PAGINATION_NEXT_PAGE_SEARCH_TEXT = 'Next'

_POP_UP_ID = 'popover-x'

# Create Data Structures for Jobs
job_titles = []
job_headers = []
job_content = []

# Create function to capture info from the job panel
def get_info_from_job_panel(containerId, headerId, contentId, timeout):
    time.sleep(timeout)
    summary = driver.find_element_by_id(containerId)
                    
    header = summary.find_element_by_id(headerId)
    job_headers.append(header.text)
                    
    content = summary.find_element_by_id(contentId)
    job_content.append(content.text)
  
# Create webdriver and get the URL
driver = webdriver.Chrome(executable_path=_WEBDRIVER_PATH)
driver.get(_URL)

# Wait for the Page to Load
time.sleep(_PAGE_LOAD_TIMEOUT)

while not _END_OF_RESULTS:
    result_colmn = driver.find_element_by_id(_JOB_RESULTS_ELEMENT_ID)
    result_links = result_colmn.find_elements_by_tag_name('a')
    
    for link in result_links:
        if (len(link.text) != 0):
            if link.get_attribute('href').find(_JOB_LINK_SEARCH_PARAM1) != -1 or link.get_attribute('href').find(_JOB_LINK_SEARCH_PARAM2) != -1:
                job_titles.append(link.text)
                link.click()
                
                try:
                    get_info_from_job_panel(_JOB_CONTAINER_ID, _JOB_HEADER_ID, _JOB_CONTENT_ID, _JOB_PANEL_TIMEOUT)
                except NoSuchElementException:
                    # Retry if the first attempt fails
                    get_info_from_job_panel(_JOB_CONTAINER_ID, _JOB_HEADER_ID, _JOB_CONTENT_ID, _JOB_PANEL_TIMEOUT)
    
    pagination = driver.find_element_by_class_name(_PAGINATION_CLASS_NAME)
    pages = pagination.find_elements_by_tag_name('a')
    
    for page in pages:
        if page.text.find(_PAGINATION_NEXT_PAGE_SEARCH_TEXT) != -1:
            page.click()
            time.sleep(_PAGE_LOAD_TIMEOUT)
            
            # Check if there is a pop up after loading the next page
            # If there is, close it first before proceeding to parse the next results
            try:
                pop_up = driver.find_element_by_id(_POP_UP_ID)
                close_pop_up = pop_up.find_element_by_tag_name('a')
                close_pop_up.click()
            except NoSuchElementException:
                pass
        else:
            _END_OF_RESULTS = True

driver.close()