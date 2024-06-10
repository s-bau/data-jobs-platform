from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import sys  # to be able to exit the program in case of errors, using sys.exit() to stop the program

from make_sense import df_details


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
        publication = match.group()
    except AttributeError:
        publication = None
    
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
        debut = match.group(1)
    except AttributeError:
        debut = None
    
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
                  "publication": publication,
                  "salaire": salaire,
                  "debut": debut,
                  "missions": missions,
                  "profil": profil}
    additional_list.append(additional)

df_additional = pd.DataFrame(additional_list, columns=["url", "publication", "salaire", "debut", "missions", "profil"])

df_make_sense = pd.merge(df_details, df_additional, on="url")

# save as csv
df_make_sense.to_csv("df_make_sense.csv", sep=",", encoding="utf-8", index=False)
