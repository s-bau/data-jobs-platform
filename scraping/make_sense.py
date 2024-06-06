from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys  # to be able to exit the program in case of errors, using sys.exit() to stop the program


"""creating a dataframe with 1 column: url of each job offer"""

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

# looping through joubs and saving each url in a df
pattern = r'href="(.*?)"'

url_list = []

for job in jobs:
    match = re.search(pattern, str(job))

    # error handling: in case of problems finding the link
    try:
        url = "https://jobs.makesense.org/" + match.group(1)
    except AttributeError:
        sys.exit("can't find job urls")

    url_list.append(url)

df_url = pd.DataFrame(url_list, columns=["url"])
