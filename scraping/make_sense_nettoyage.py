from datetime import datetime
import pandas as pd


df_make_sense = pd.read_csv("df_make_sense.csv")

# turning publication into datetime
df_make_sense["publication"] = df_make_sense["publication"].apply(lambda x: None if pd.isna(x) else datetime.strptime(str(x), "%d/%m/%Y"))

# sorting by publication date (showing newest first)
df_make_sense.sort_values(by="publication", ascending=False, ignore_index=True, inplace=True)

print(df_make_sense.iloc[0,:])


