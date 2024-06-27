from datetime import datetime
import nltk
nltk.download("popular")
import pandas as pd
import re

from departements import codes
from competences import competences_single, competences_multi
from colonnes import desired_order

df_make_sense = pd.read_csv("df_make_sense.csv", sep=",")

# turning publication into datetime
df_make_sense["date_publication"] = df_make_sense["date_publication"].apply(lambda x: None if pd.isna(x) else datetime.strptime(str(x), "%d/%m/%Y"))

# sorting by publication date (showing newest first)
df_make_sense.sort_values(by="date_publication", ascending=False, ignore_index=True, inplace=True)

# cleaning city
def clean_city(city):
    if "," in city:
        if "France" not in city:
            clean_city = None
        else:
            index = city.index(",")
            clean_city = city[:index].strip()
    else:
        clean_city = city.strip()
    return clean_city
    
df_make_sense["ville"] = df_make_sense["ville"].apply(clean_city)
df_make_sense.dropna(subset=["ville"], inplace=True)

# add code département (int)
df_make_sense["departement"] = df_make_sense["ville"].apply(lambda x: codes[x.lower()] if x.lower() in codes.keys() else 00)

# split salary into multiple columns (min, max and avg)
def clean_salary(salary):
    salary = str(salary)
    if "an" in salary.lower():  # only annual salaries (no hourly/monthly)
        if "-" in salary:
            index = salary.index("-")
            min_salary = salary[:index].strip()
            max_salary = salary[index+1:].strip()

        else:
            min_salary = salary
            max_salary = salary
    else:
        min_salary = None
        max_salary = None
    
    # turn K into 000 and take only digits (no currency etc.)
    if min_salary:
        pattern = r"\d+"
        match = re.search(pattern, min_salary)
        if match:
            min_salary = int(match.group(0))
            if min_salary < 999:
                min_salary *= 1000

        match = re.search(pattern, max_salary)
        if match:
            max_salary = int(match.group(0))
            if max_salary < 999:
                max_salary *= 1000
        
        try:
            avg = int((min_salary + max_salary) / 2)
        except TypeError:
            avg = None
    
    else:
        avg = None

    return min_salary, max_salary, avg

df_make_sense[["salaire_min", "salaire_max", "salaire_avg"]] = df_make_sense["salaire"].apply(clean_salary).apply(pd.Series)

# NAN for nb_employes, index_egalite, repartition_genre
df_make_sense[["nb_employes", "index_egalite", "repartition_genre"]] = None

# concatenate profil & missions and put it in a new column description_job
def concat(text):
    full = str(text["missions"]) + " " + str(text["profil"])
    return full

df_make_sense["description_job"] = df_make_sense.apply(concat, axis=1)
df_make_sense.drop(columns=["missions", "profil"], inplace=True)
df_make_sense.reset_index(drop=True, inplace=True)

# clean up description
df_make_sense["description_job"] = df_make_sense["description_job"].apply(lambda x: x.replace("\n", " ") if x else x)

# competences
def competences(description):

    description_tokens = nltk.word_tokenize(description.lower())
    competences_list = []

    for i in competences_single:
        if i in description_tokens and i not in competences_list:
            competences_list.append(i)

    for i in competences_multi:
        if i in description and i not in competences_list:
            competences_list.append(i)

    if competences_list == []:
        competences_list = None

    return competences_list   

df_make_sense["competences"] = df_make_sense["description_job"].apply(competences)

# NaN for niveau_etudes
df_make_sense[["niveau_etudes"]] = None

# change order of columns
df_make_sense = df_make_sense.reindex(columns=desired_order)

# save as csv
df_make_sense.to_csv("clean_sense.csv", sep=",", encoding="utf-8", index=False)



