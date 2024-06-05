from bs4 import BeautifulSoup
import pandas as pd
import requests

# sorting by date
url = "https://jobs.makesense.org/fr/s/jobs/all?s=Data%20Analyst&sortBy=createdAt"
html = requests.get(url)

soup = BeautifulSoup(html.text, "html.parser")

jobs = soup.find_all("div", {"class": "job__container"})

print(jobs[0])

