from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys  # to be able to exit the program in case of errors, using sys.exit() to stop the program


"""loop through all pages that include job offers"""

base_url = "https://jobs.makesense.org/fr/s/jobs/all?s=Data%20Analyst&sortBy=createdAt"
page_number = 1
urls_to_scrape = []

while True:
    if page_number == 1:
        url = base_url
    else:
        url = f"{base_url}&items_page={page_number}"

    navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'  
    html = requests.get(url, headers={'User-Agent': navigator})

    soup = BeautifulSoup(html.text, "html.parser")

    if '<div class="nothingtoshow"' in str(soup):
        break

    else:
        page_number += 1
        urls_to_scrape.append(url)


"""creating a dataframe with multiple columns: url of each job offer, title, employer, sense, type of contract"""

details_list = []

for item in urls_to_scrape:
    url = item

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

    for job in jobs:
        match = re.search(pattern, str(job))

        # url
        try:
            url = "https://jobs.makesense.org/" + match.group(1)
        except AttributeError:
            sys.exit("can't find job urls")


        # job title
        try:
            name = job.find("h3", {"class": "content__title"}).text.strip()
        except AttributeError:
            name = None

        # Nom entreprise
        organization_reference = job.find("div", {"class": "meta"}).text.strip()

        # Description entreprise
        company_description = job.find("p", {"class": "content__project-mission"}).text.strip()

        # details
        details = str(job.find_all("div", {"class": "meta"}))

        # impact (why this job "makes sense")
        try:
            dpattern = r"</span>(.*?)<!"
            match = re.search(dpattern, details, re.DOTALL)
            impact = match.group(1).strip()
        except AttributeError:
            impact = None
    
        # Type de contrat
        try:
            cpattern = r"<!-- -->((?:(?![<>]).)*?)<!-- -->"
            match = re.search(cpattern, details, re.DOTALL)
            contract_type = match.group(1).strip()
        except AttributeError:
            contract_type = None
    
        # Localisation
        try:
            lpattern = r"</svg>((?:(?![<>]).)*?)</address>"
            match = re.search(lpattern, details, re.DOTALL)
            city = match.group(1).strip()
        except AttributeError:
            city = None
    

        # all job details
        detail = {"url": url,
                "organization_reference": organization_reference,
                "name": name,
                "company_description": company_description,
                "impact": impact,
                "contract_type": contract_type,
                "city": city}
        details_list.append(detail)

df_details = pd.DataFrame(details_list, columns=["url",
                                                 "organization_reference",
                                                 "name",
                                                 "company_description",
                                                 "impact",
                                                 "contract_type",
                                                 "city"])


"""accessing infos from each page"""

additional_list = []

for value in df_details["url"].values:
    
    url = value

    navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'  
    html = requests.get(url, headers={'User-Agent': navigator})

    soup = BeautifulSoup(html.text, "html.parser")

    section = soup.find("section", {"class": "meta section--style-default"})

    # publication date
    date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
    match = re.search(date_pattern, str(section))
    try:
        publication_date = match.group()
    except AttributeError:
        publication_date = None
    
    # salaire
    salaire_pattern = r"</svg>(\s*\d[\s\S]*?\s*)</div>"
    match = re.search(salaire_pattern, str(section), re.DOTALL)

    if 'title id="coffee"' in str(section):
        try:
            salaire = match.group(1).strip()
        except AttributeError:
            salaire = None
    else:
        salaire = None

    # début du contrat
    debut_pattern = r"Début\s*:\s*((?:(?![\n]).)*?)\n"
    match = re.search(debut_pattern, str(section), re.DOTALL)
    try:
        start_date = match.group(1)
    except AttributeError:
        start_date = None
    
    # missions
    try:
        missions = soup.find("main", {"class": "job__main-content"}).text
    except AttributeError:
        missions = None

    # profil
    try:
        profil = soup.find("div", {"class": "job__main-content"}).text
    except AttributeError:
        profil = None
    

    additional = {"url": url,
                  "publication_date": publication_date,
                  "salaire": salaire,
                  "start_date": start_date,
                  "missions": missions,
                  "profil": profil}
    additional_list.append(additional)

df_additional = pd.DataFrame(additional_list, columns=["url", "publication_date", "salaire", "start_date", "missions", "profil"])

df_make_sense = pd.merge(df_details, df_additional, on="url")

# save as csv
df_make_sense.to_csv("df_make_sense.csv", sep=",", encoding="utf-8", index=False)