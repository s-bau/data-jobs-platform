from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys  # to be able to exit the program in case of errors, using sys.exit() to stop the program


"""creating a dataframe with multiple columns: url of each job offer, title, employer, sense, type of contract"""

# sorting by date "cratedAT"
url = "https://jobs.makesense.org/fr/s/jobs/all?s=Data%20Analyst&sortBy=createdAt"

# in case the site is protected
navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'  
html = requests.get(url, headers={'User-Agent': navigator})

soup = BeautifulSoup(html.text, "html.parser")

# error handling: status code must be 200 (request worked)
if html.status_code != 200:
    sys.exit("could not access url, check request")

# finding all jobs listed on the page
soup = BeautifulSoup(html.text, "html.parser")
jobs = soup.find_all("div", {"class": "job"})

# error handling in case jobs is empty
if len(jobs) == 0:
    sys.exit("no jobs found, check your find_all")

# looping through jobs and saving each url, title in a df
pattern = r'href="(.*?)"'

details_list = []

for job in jobs:
    match = re.search(pattern, str(job))

    # url
    try:
        url = "https://jobs.makesense.org/" + match.group(1)
    except AttributeError:
        sys.exit("can't find job urls")


    # title
    try:
        title = job.find("h3", {"class": "content__title"}).text.strip()
    except AttributeError:
        title = None

    # employer
    employer = job.find("div", {"class": "meta"}).text.strip()

    # employer info
    info = job.find("p", {"class": "content__project-mission"}).text.strip()

    # details
    details = str(job.find_all("div", {"class": "meta"}))

    # sense
    try:
        dpattern = r"</span>(.*?)<!"
        match = re.search(dpattern, details, re.DOTALL)
        sense = match.group(1).strip()
    except AttributeError:
        sense = None
    
    # type of contract
    try:
        cpattern = r"<!-- -->((?:(?![<>]).)*?)<!-- -->"
        match = re.search(cpattern, details, re.DOTALL)
        contract = match.group(1).strip()
    except AttributeError:
        contract = None
    
    # location
    try:
        lpattern = r"</svg>((?:(?![<>]).)*?)</address>"
        match = re.search(lpattern, details, re.DOTALL)
        location = match.group(1).strip()
    except AttributeError:
        location = None
    

    # all job details
    detail = {"url": url,
              "title": title,
              "employer": employer,
              "info": info,
              "sense": sense,
              "contract": contract,
              "location": location}
    details_list.append(detail)

df_details = pd.DataFrame(details_list, columns=["url", "title", "employer", "info", "sense", "contract", "location"])