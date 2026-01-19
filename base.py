import pandas as pd

df3 = pd.DataFrame({"X": ["B", "A", "B", "A", "B"], "Y": [1, 4, 3, 2, 5], "Z": [11, 14, 13, 12, 15]})

print(df3["Y"].agg(['sum']))