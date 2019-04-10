#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 10:55:02 2018

@author: neilcabrera
"""

import time
import sqlite3
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

# Web Driver Parameters
URL = 'https://www.mycareersfuture.sg/search?search={}&sortBy=new_posting_date&page={}"'
SEARCH_PARAMS = ['data%20scientist',
                 'data%20analyst',
                 'deep%20learning',
                 'data%20engineer',
                 'data%20architect',
                 'artificial%20intelligence',
                 'machine%20learning',
                 'python',
                 'R%20SAS',
                 'business%20intelligence',
                 'business%20data']

JOB_WEBSITE = 'https://www.mycareersfuture.sg/'
JOB_COUNTRY = 'SG'
WEBDRIVER_PATH = "/Users/cabre/OneDrive/Downloads/chromedriver.exe"
PAGE_LOAD_TIMEOUT = 4

# Database Parameters
DATABASE_NAME = 'project-04-starter.db'

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print('SQL Lite Error encountered!')
 
    return None

def create_job(conn, job):
    """
    Create a new job into the jobs table
    :param conn:
    :param job:
    :return: job id
    """
    sql = ''' INSERT INTO jobs(job_title, company, company_address, country, employment_type, job_category, job_level, salary_from, salary_to, job_role, job_requirements, website, job_tags, url)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, job)
    return cur.lastrowid

def scrape_website(url, search_param, conn):
    _PAGE_NO = 0
    
    # Option to make the Browser Headless
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    # Create webdriver and get the URL
    driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, options = options)
    driver.get(url.format(search_param, _PAGE_NO))
    
    # Wait for the Page to Load
    time.sleep(PAGE_LOAD_TIMEOUT)
    
    # Keep Looping until Forced Out of Loop
    while True:
        print('Search Parameter: {}, Processing Page No.:{}'.format(search_param.replace('%20', ' '), _PAGE_NO))
        
        result_links = driver.find_elements_by_xpath("//div[contains(@id, 'job-card')]")
        
        # Check if there are results, if 0, break the loop
        if len(result_links) == 0:
            # Wait for the Page to Load and Retry
            time.sleep(PAGE_LOAD_TIMEOUT)
            result_links = driver.find_elements_by_xpath("//div[contains(@id, 'job-card')]")
        
        # Check again 2nd time
        if len(result_links) == 0:
            break
        
        for result_link in result_links:
            # Initialise Data for Database Insertion
            job_title = ''
            job_company = ''
            job_company_address = ''
            job_country = JOB_COUNTRY
            job_employment_type = ''
            job_category = ''
            job_level = ''
            job_salary_from = '$0'
            job_salary_to = '$0'
            job_role = ''
            job_requirements = ''
            job_website = JOB_WEBSITE
            job_tag = search_param.replace('%20', ' ')
            job_url = ''
            
            job_title_link = result_link.find_element_by_tag_name('a')
            
            # Open a new window to load the job details                    
            sub_driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, chrome_options = options)
            job_url = job_title_link.get_attribute('href')
            sub_driver.get(job_url)
            
            # Wait for the Page to Load
            time.sleep(PAGE_LOAD_TIMEOUT)
                
            try:
                # Get all the Header Information of the Job
                job_title = sub_driver.find_element_by_id('job_title').text
                
                try:
                    job_company = sub_driver.find_element_by_name('company').text
                except NoSuchElementException:
                    print('Missing Company for job title: ' + job_title)
                    
                try:
                    job_company_address = sub_driver.find_element_by_id('address').text
                except NoSuchElementException:
                    print('Missing Company Address for job title: ' + job_title)
                
                try:
                    job_employment_type = sub_driver.find_element_by_id('employment_type').text
                except NoSuchElementException:
                    print('Missing Employment Type for job title: ' + job_title)
                
                try:
                    job_category = sub_driver.find_element_by_id('job-categories').text
                except NoSuchElementException:
                    print('Missing Employment Category for job title: ' + job_title)
                
                try:
                    job_level = sub_driver.find_element_by_id('seniority').text
                except NoSuchElementException:
                    print('Missing Job Level for job title: ' + job_title)
                
                try:
                    salary_range = sub_driver.find_element_by_xpath("//span[contains(@class, 'salary_range')]")
                    if len(salary_range.find_elements_by_tag_name('span')) == 3:
                        job_salary_from = salary_range.find_elements_by_tag_name('span')[0].text
                        job_salary_to = salary_range.find_elements_by_tag_name('span')[1].text
                except NoSuchElementException:
                    print('Missing Salary occured for job title:' + job_title)
                
                # Get all the Detail Information of the Job
                try:
                    job_role = sub_driver.find_element_by_id('job_description').text
                except NoSuchElementException:
                    print('Missing Job Description for job title: ' + job_title)
                
                try:
                    job_requirements = sub_driver.find_element_by_id('requirements').text
                except NoSuchElementException:
                    print('Missing Job Requirements for job title: ' + job_title)
                    
                # Write Data to the Database
                with conn:
                    job = (job_title, job_company, job_company_address, job_country, job_employment_type, job_category, 
                           job_level, job_salary_from, job_salary_to, job_role, job_requirements, job_website, 
                           job_tag, job_url);
                    create_job(conn, job)
                
            except NoSuchElementException: #Retry again for the 2nd time
                    print('Unknown occured for job title:' + job_title_link.text)
                
            sub_driver.close()
    
        # Move to the next page
        _PAGE_NO += 1
        driver.get(url.format(search_param, _PAGE_NO))
        # Wait for the Page to Load
        time.sleep(PAGE_LOAD_TIMEOUT)
    
    driver.close()

conn = create_connection(DATABASE_NAME)
for search_param in SEARCH_PARAMS:
    scrape_website(URL, search_param, conn)