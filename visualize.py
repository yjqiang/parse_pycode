import seaborn
import matplotlib.pyplot as plt
import pandas as pd

import utils


dictionary = utils.open_json('data/extract_comment_and_class/used_api.json')['statistics']
dictionary = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))  # 根据 value 对 dict 进行 sort
dictionary = dict(list(dictionary.items())[:500])

df = pd.DataFrame(dictionary.items(), columns=['ApiName', 'Count'])

print(df)

height = 1000
width = 30
fig, ax = plt.subplots(figsize=(height, width))
seaborn.barplot(x='ApiName', y='Count', data=df)
plt.show()
