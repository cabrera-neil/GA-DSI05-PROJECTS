#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 10:55:02 2018

@author: neilcabrera
"""

import time
import sqlite3
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

# Web Driver Parameters
URLs = ["http://sg.startupjobs.asia/sg/job/search?w=jobs&q=data+scientist&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=data+analyst&l=Anywhere&t=any#searchResult=",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=machine+learning&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=business+intelligence&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=data+engineer&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=data+architect&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=business+data&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=artificial+intelligence&l=Anywhere&t=any#searchResult",
         "http://sg.startupjobs.asia/sg/job/search?w=jobs&q=deep+learning&l=Anywhere&t=any#searchResult"]
JOB_WEBSITE = 'http://sg.startupjobs.asia'
JOB_COUNTRY = 'SG'
WEBDRIVER_PATH = "/Users/neilcabrera/Downloads/chromedriver"
PAGE_LOAD_TIMEOUT = 3

# Database Parameters
DATABASE_NAME = 'project-04-starter-test.db'

# Web Scraping Parameters
# Limit to 1k results for each query
TARGET_NO_OF_JOBS = 1000

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
    sql = ''' INSERT INTO jobs(job_title, company, company_address, country, employment_type, job_category, job_level, salary_from, salary_to, job_role, job_requirements, website, url)
              VALUES(?,?,?, ?,?,?, ?,?,?, ?,?,?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, job)
    return cur.lastrowid

def scrape_website(url, conn):
    _CURRENT_NO_OF_JOBS = 0
    
    # Create webdriver and get the URL
    driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH)
    driver.get(URLs[0])
    
    # Wait for the Page to Load
    time.sleep(PAGE_LOAD_TIMEOUT)
    
    while _CURRENT_NO_OF_JOBS <= TARGET_NO_OF_JOBS:
        
        search_result_soup = BeautifulSoup(driver.page_source, 'lxml')
        result_links = search_result_soup.findAll('div', class_='SingleJob')
        
        # Check if there are results, if 0, break the loop
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
            job_url = ''
            
            job_title_link = result_link.find('span', class_='JobRole')
            job_title_link = job_title_link.find('a')
            
            # Get all the Job Header Information and URL
            job_url = job_title_link.get('href')
            job_title = job_title_link.text
            job_company = result_link.find('span', class_='CompanyName').text
            job_company_address = result_link.find('span', class_='CountryName').text
            job_employment_type = result_link.find('div', class_='jobtypehome').text
            job_category = result_link.find('div', class_='jobcategoryhome').text
            
            # Open a new window to load the job details                    
            sub_driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH)
            sub_driver.get(JOB_WEBSITE + job_url)
            
            # Wait for the Page to Load
            time.sleep(PAGE_LOAD_TIMEOUT)
            
            job_details_soup = BeautifulSoup(sub_driver.page_source, 'lxml')
            job_body = job_details_soup.find('div', class_='jobBody')
            
            # Parse Job Body of Text
            job_body_text = job_body.text
            job_body_text = job_body_text.replace('\n', ' ')
            job_body_text = job_body_text.replace('\t', ' ')
            
            # Get jobs with Responsibilities, Requirements and Salary
            if job_body_text.find('Responsibilities') != -1:
                if job_body_text.find('Requirements') != -1:
                    if job_body_text.find('Salary') != -1:
                        job_role = re.findall('Responsibilities.*Requirements', job_body_text)[0]
                        job_role = job_role.replace('Responsibilities', '')
                        job_role = job_role.replace('Requirements', '')
                        job_role = str.strip(job_role)
                        
                        job_requirements = re.findall('Requirements.*Salary', job_body_text)[0]
                        job_requirements = job_requirements.replace('Requirements', '')
                        job_requirements = job_requirements.replace('Salary', '')
                        job_requirements = str.strip(job_requirements)
                        
                        job_salary_from = re.findall('Salary.*', job_body_text)[0]
                        job_salary_from = job_salary_from.replace('Salary', '')
                        job_salary_from = str.strip(job_salary_from)
            else:
                # If Responsibilities are missing, proceed with at least Requirements and Salary present
                if job_body_text.find('Requirements') != -1 and job_body_text.find('Salary') != -1:
                    job_requirements = re.findall('Requirements.*Salary', job_body_text)[0]
                    job_requirements = job_requirements.replace('Requirements', '')
                    job_requirements = job_requirements.replace('Salary', '')
                    job_requirements = str.strip(job_requirements)
                    
                    job_salary_from = re.findall('Salary.*', job_body_text)[0]
                    job_salary_from = job_salary_from.replace('Salary', '')
                    job_salary_from = str.strip(job_salary_from)
                else:
                    sub_driver.close()
                    break
            
            if job_salary_from.find('-') != -1:
                job_salary_to = job_salary_from.split('-')[1]
                job_salary_to = str.strip(job_salary_to)
                
                job_salary_from = job_salary_from.split('-')[0]
                job_salary_from = str.strip(job_salary_from)
            
            # Write Data to the Database
            with conn:
                job = (job_title, job_company, job_company_address, job_country, job_employment_type, job_category, 
                       job_level, job_salary_from, job_salary_to, job_role, job_requirements, job_website, 
                       job_url);
                create_job(conn, job)        
            
            _CURRENT_NO_OF_JOBS += 1
                
            sub_driver.close()
    
        try:
            # Move to the next page
            next_page = driver.find_element_by_xpath("//li[contains(@class, 'next')]")
            next_page = next_page.find_element_by_tag_name('a')
            next_page.click()
            # Wait for the Page to Load
            time.sleep(PAGE_LOAD_TIMEOUT)
        except NoSuchElementException:
            print('Reached end of the search result...')
            break
    
    driver.close()

conn = create_connection(DATABASE_NAME)
for url in URLs:
    scrape_website(url, conn)