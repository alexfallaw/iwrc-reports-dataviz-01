import pandas as pd

c = {
  "colA": [7, 5, 2, 2, 4],
  "colB": [9, 40, 3, 9, 67]
}

tableC = pd.DataFrame(c)

x = tableC["colA", "colB"].mode()[1]

print(x)