import requests
import pandas as pd
import matplotlib as plt
url = "https://dummyjson.com/products"
response = requests.get(url)
print(response.status_code)
df = pd.DataFrame(response.json())
# print(df.describe())
# print(df.head(5))
# df.plot(kind='bar', x='Product', y='Sales')
# plt.show()

df.to_excel("sales_repot.xlsx", index=False)

