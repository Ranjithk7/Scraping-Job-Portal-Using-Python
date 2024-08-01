import csv
import bs4
from urllib.request import urlopen as uReq
import requests
from datetime import datetime
from time import sleep
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

ua = UserAgent()
user_agent = ua.random
headers = {
   'User-Agent': user_agent,
   'Accept-Language': 'en-US,en;q=0.5',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Encoding': 'gzip, deflate',
   'DNT': '1',
   'Connection': 'keep-alive',
   'Upgrade-Insecure-Requests': '1',
}

params = {
   'v': '3.2.1', # chrome version
   'lang': 'en-US' # browser language
}

data = {
   'timezoneId': 'America/Los_Angeles',
   'screen_resolution': '1920x1080',
   'browser_plugins': 'Shockwave Flash|Java',
}

def get_url(position, location):
    template = "https://in.indeed.com/jobs?q={}&l={}"
    url = template.format(position, location)
    return url

def get_Response(url):
    response = requests.get(
       url,
       headers=headers,
       params=params,
       data=data
    )
    return response

def get_Record(job):
    atag = job.h2.a
    job_title = atag.text
    job_url = "https://in.indeed.com" + atag.get("href")
    company_name = job.find("span", {"class": "css-63koeb eu4oa1w0"}).text
    job_loc = job.find("div", {"class": "css-1p0sjhy eu4oa1w0"}).text
    date = job.find("span", {"class": "css-qvloho eu4oa1w0"}).text
    post_date = ''
    post = list(date.split(" "))
    post1 = post[0]

    if post1[:int(len(post1)/2)] == post1[int(len(post1)/2):]:
        post_date = date[int(len(post1)/2):]
    elif 'Active' in date:
        post_date = date[8:]
    try:
        job_summary = job.find("div", "css-9446fg eu4oa1w0").text
    except AttributeError:
        job_summary = ''
    try:
        salary = job.find("div", {"class": "css-5zy3wz"}).text
        if "year" not in salary:
            salary = ''
    except AttributeError:
        salary = ''

    record = (job_title, company_name, job_loc, post_date,job_summary, salary, job_url)
    return record

def main(position, location):
    records = []
    url = get_url(position, location)
    while True:
        response = get_Response(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all("div", "job_seen_beacon")

        for job in jobs:
            record = get_Record(job)
            records.append(record)
        
        try :
            url = "https://in.indeed.com" + soup.find('a', {"aria-label": "Next Page"}).get("href")
        except AttributeError:
            break

        with open('results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['JobTitle', 'Company', 'Location', 'PostDate', 'Summary', 'Salary', 'JobUrl'])
            writer.writerows(records)

main('java developer', 'chennai')
        
