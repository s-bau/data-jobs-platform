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


        # Nom emploi
        try:
            nom_emploi = job.find("h3", {"class": "content__title"}).text.strip()
        except AttributeError:
            nom_emploi = None

        # Nom entreprise
        nom_entreprise = job.find("div", {"class": "meta"}).text.strip()

        # Description entreprise
        description_cie = job.find("p", {"class": "content__project-mission"}).text.strip()

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
            contrat = match.group(1).strip()
        except AttributeError:
            contrat = None
    
        # Localisation
        try:
            lpattern = r"</svg>((?:(?![<>]).)*?)</address>"
            match = re.search(lpattern, details, re.DOTALL)
            ville = match.group(1).strip()
        except AttributeError:
            ville = None
    

        # all job details
        detail = {"url": url,
                  "nom_entreprise": nom_entreprise,
                  "nom_emploi": nom_emploi,
                  "description_cie": description_cie,
                  "impact": impact,
                  "contrat": contrat,
                  "ville": ville}
        details_list.append(detail)

df_details = pd.DataFrame(details_list, columns=["url",
                                                 "nom_entreprise",
                                                 "nom_emploi",
                                                 "description_cie",
                                                 "impact",
                                                 "contrat",
                                                 "ville"])


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
        date_publication = match.group()
    except AttributeError:
        date_publication = None
    
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
    
    # function to find secteur, teletravail and niveau_experience
    def infos(tag, text):
        if tag in text:
            start_index = text.find(tag)
            text = text[start_index:]

            try:
                pattern = r"</svg>([\s\S]*?)</div>"
                match = re.search(pattern, text, re.DOTALL)
                match = match.group(1).strip()
            except AttributeError:
                match = None
        else:
            match = None
        
        return match
    
    secteur = infos('title id="tag"', str(section))
    teletravail = infos('title id="monitor', str(section))
    niveau_experience = infos('title id="bar-chart"', str(section))

    # # début du contrat
    # debut_pattern = r"Début\s*:\s*((?:(?![\n]).)*?)\n"
    # match = re.search(debut_pattern, str(section), re.DOTALL)
    # try:
    #     start_date = match.group(1)
    # except AttributeError:
    #     start_date = None
    
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
                  "date_publication": date_publication,
                  "salaire": salaire,
                  "secteur": secteur,
                  "teletravail": teletravail,
                  "niveau_experience": niveau_experience,
                  # "start_date": start_date,
                  "missions": missions,
                  "profil": profil}
    additional_list.append(additional)

df_additional = pd.DataFrame(additional_list, columns=["url",
                                                       "date_publication",
                                                       "salaire",
                                                       "secteur",
                                                       "teletravail",
                                                       "niveau_experience",
                                                       # "start_date",
                                                       "missions",
                                                       "profil"])

df_make_sense = pd.merge(df_details, df_additional, on="url")

# save as csv
df_make_sense.to_csv("df_make_sense.csv", sep=",", encoding="utf-8", index=False)