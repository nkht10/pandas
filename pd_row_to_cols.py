import pandas as pd


df = pd.read_csv('sample.csv', na_values=0)

#df.info()

#df["row_index"] = df.index

#print(df['CT3'].head(10))

dropColumnList = ['Year','Industry_aggregation_NZSIOC','Industry_code_NZSIOC','Industry_name_NZSIOC','Units','Variable_code','Variable_name','Variable_category','Value','Industry_code_ANZSIC06']

df.drop(dropColumnList, axis=1, inplace=True)


#df.columns 

cols = ['MST'] + [list(df.columns).index(item) for item in df.columns if item != 'MST']

df.columns = cols

df_transpose = df.head(100).melt(id_vars=['MST'], var_name = "Field", value_name = 'Field_Value').dropna().sort_values('MST')




# print(df_transpose)

df_transpose.info()



df_transpose.to_excel('sample.xlsx')
