from datetime import datetime
import pandas as pd


df_make_sense = pd.read_csv("df_make_sense.csv")

# turning publication into datetime
df_make_sense["publication_date"] = df_make_sense["publication_date"].apply(lambda x: None if pd.isna(x) else datetime.strptime(str(x), "%d/%m/%Y"))

# sorting by publication date (showing newest first)
df_make_sense.sort_values(by="publication_date", ascending=False, ignore_index=True, inplace=True)

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
    
df_make_sense["city"] = df_make_sense["city"].apply(clean_city)
df_make_sense.dropna(subset=["city"], inplace=True)

# split salary into multiple columns
# def clean_salary(salary):
#     salary = str(salary)
#     if "-" in salary:
#         index = salary.index("-")
#         min_salary = salary[:index].strip()
#         max_salary = salary[index+1:].strip()
    
#     else:
#         min_salary = salary
#         max_salary = salary
    
#     return [min_salary, max_salary]

# df_make_sense["min_salary"] = df_make_sense["salaire"].apply(clean_salary)[0]
# df_make_sense["max_salary"] = df_make_sense["salaire"].apply(clean_salary)[1]
# print(df_make_sense["min_salary"].value_counts())


# drop all rows where publication date is older than 3 months
#print(df_make_sense["publication_date"].value_counts())


