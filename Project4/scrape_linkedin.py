#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 10:55:02 2018

@author: neilcabrera
"""

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# Web Driver Parameters
_URL = "https://sg.linkedin.com/jobs/search?keywords=Data+Scientist&location=Singapore&locationId=sg%3A0"
_WEBDRIVER_PATH = "/Users/neilcabrera/Downloads/chromedriver"
_PAGE_LOAD_TIMEOUT = 5

# Web Scraping Parameters
_TARGET_NO_OF_JOBS = 100
#_JOB_RESULTS_ELEMENT_ID = 'resultsCol'
#_JOB_LINK_SEARCH_PARAM1 = '/pagead/clk'
#_JOB_LINK_SEARCH_PARAM2 = 'fccid'
#
#_JOB_CONTAINER_ID = 'vjs-container'
#_JOB_HEADER_ID = 'vjs-header'
#_JOB_CONTENT_ID = 'vjs-content'

_JOB_PANEL_TIMEOUT = 5

#_PAGINATION_CLASS_NAME = 'pagination'
#_PAGINATION_NEXT_PAGE_SEARCH_TEXT = 'Next'
#
#_POP_UP_ID = 'popover-x'

# Create Data Structures for Jobs
job_titles = []
job_headers = []
job_content = []
  
# Create webdriver and get the URL
driver = webdriver.Chrome(executable_path=_WEBDRIVER_PATH)
driver.get(_URL)

# Wait for the Page to Load
time.sleep(_PAGE_LOAD_TIMEOUT)

# Sign-in first
links = driver.find_elements_by_tag_name('a')
for link in links:
    if link.get_attribute('class') == 'nav-item__link' and link.text == 'Sign in':
        sign_in_page = link
        sign_in_page.click()
            
        # Wait for the Page to Load
        time.sleep(_PAGE_LOAD_TIMEOUT)
        username = driver.find_element_by_id('session_key-login')
        driver.execute_script("arguments[0].setAttribute('value','cabrera.neil@gmail.com')", username)
        password = driver.find_element_by_id('session_password-login')
        driver.execute_script("arguments[0].setAttribute('value','Jm112183')", password)
        login = driver.find_element_by_id('btn-primary')
        login.click()
        break

while len(job_titles) <= _TARGET_NO_OF_JOBS:
    result_links = driver.find_elements_by_xpath("//li[contains(@class, 'occludable-update card-list__item jobs-search-two-pane__search-result-item ember-view')]")
    
    for result_link in result_links:
        job_title_links = result_link.find_elements_by_tag_name('li')
        for job_title_link in job_title_links:
            if job_title_link.get_attribute('class') == 'job-title-link':
                if (len(job_title_link.text) != 0):
                    job_titles.append(job_title_link.text)
                    
                    try:
                        # Open a new window to load the job details                    
                        sub_driver = webdriver.Chrome(executable_path=_WEBDRIVER_PATH)
                        sub_driver.get(job_title_link.get_attribute('href'))
    
                        # Wait for the Page to Load
                        time.sleep(_PAGE_LOAD_TIMEOUT)
                        
                        header = sub_driver.find_element_by_class_name('content')
                        job_headers.append(header.text)
                        
                        content = sub_driver.find_element_by_class_name('summary')
                        job_content.append(content.text)
                        
                        sub_driver.close()
                    except NoSuchElementException:
                        sub_driver.close()
                        
                        # Open a new window to load the job details                    
                        sub_driver = webdriver.Chrome(executable_path=_WEBDRIVER_PATH)
                        sub_driver.get(job_title_link.get_attribute('href'))
    
                        # Wait for the Page to Load
                        time.sleep(_PAGE_LOAD_TIMEOUT)
                        
                        header = sub_driver.find_element_by_class_name('content')
                        job_headers.append(header.text)
                        
                        content = sub_driver.find_element_by_class_name('summary')
                        job_content.append(content.text)
                        
                        sub_driver.close()
                        

    links = driver.find_elements_by_tag_name('a')
    for link in links:
        if link.get_attribute('class') == 'next-prev-container next-btn':
            next_page = link
            next_page.click()
            time.sleep(_PAGE_LOAD_TIMEOUT)

driver.close()