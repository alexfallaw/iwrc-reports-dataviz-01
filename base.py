import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

proj_data = pd.read_csv('sample_data.csv')

# group based on project type
# resulting DF has two cols: funding type, project count

fund_grps = proj_data.groupby('Funding Type', as_index=False, dropna=False).size()
fund_grps.rename(columns={'size': 'Project Count'}, inplace=True)

# sort descending by project count
fund_grps = fund_grps.sort_values(by='Project Count', ascending=False)

print(fund_grps.to_string())

# two subplots: bar chart of funding types #, pie chart of funding types %

fig = plt.figure(figsize=(12, 6))

# BAR GRAPH
# create graph with x = funding type, y = project count

with plt.style.context('seaborn-v0_8-pastel'):
  ax1 = fig.add_subplot(1, 2, 1)
  ax1.bar(fund_grps['Funding Type'], fund_grps['Project Count'])
  ax1.set_title("Projects by Funding Type")

# PIE CHART
# create pie chart with funding type %, labels = funding type

with plt.style.context('seaborn-v0_8-dark-palette'):
  ax2 = fig.add_subplot(1, 2, 2)
  ax2.pie(fund_grps['Project Count'], labels=fund_grps['Funding Type'], autopct='%1.1f%%', startangle=140)
  ax2.set_title("Project Distribution by Funding Type")

plt.show()

print(plt.style.available)
