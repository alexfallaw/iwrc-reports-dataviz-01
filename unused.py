import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dataviz import clean_currency


proj_data = pd.read_csv('data/projects.csv')

# make subset of data with only relevant columns
proj_data = proj_data[['Project ID', 'Funding Type', 'Funding Amount']]

# clean funding amount column
proj_data['Funding Amount'] = proj_data['Funding Amount'].apply(clean_currency)

# group based on project type
# resulting DF has three cols: funding type, project count, funding amount sum

fund_grps = proj_data.groupby('Funding Type', as_index=False, dropna=False).agg(
    **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
)

#print sum of funding amounts for each funding type
print(fund_grps)

# sort descending by project count
fund_grps = fund_grps.sort_values(by='Project Count', ascending=False)

print(fund_grps.info())

# three subplots: bar chart of funding types #, pie chart of funding types %, bar chart of funding amounts by funding type

fig = plt.figure(figsize=(12, 12))

# BAR GRAPH
# create graph with x = funding type, y = project count
# x label: Funding Type
# y label: # of Projects
# y tick marks go from 0 to 25 in increments of 5
# put number on top of each bar

ax1 = fig.add_subplot(2, 2, 1)
ax1.bar(fund_grps['Funding Type'], fund_grps['Project Count'])
ax1.set_title("Projects by Funding Type")
ax1.set_xlabel("Funding Type")
ax1.set_ylabel("Number of Projects")
ax1.tick_params(axis='x', labelsize=8)
ax1.set_ylim(0, 25)
ax1.yaxis.set_major_locator(plt.MultipleLocator(5))
for i, v in enumerate(fund_grps['Project Count']):
  ax1.text(i, v + 1, str(v), ha='center', va='bottom')

# PIE CHART
# create pie chart with funding type %, labels = funding type

ax2 = fig.add_subplot(2, 2, 2)
ax2.pie(fund_grps['Project Count'], labels=fund_grps['Funding Type'], autopct='%1.1f%%', startangle=140)
ax2.set_title("Project Distribution by Funding Type")

# BAR GRAPH
# create graph with x = funding type, y = funding amount
# x label: Funding Type
# y label: Funding Amount
# put number on top of each bar
# y axis formatted as currency in units of 1.XM
# y tick marks go from 0 to 3,000,000 in increments of 500,000

ax3 = fig.add_subplot(2, 2, 4)
ax3.bar(fund_grps['Funding Type'], fund_grps['Funding Amount'])
ax3.set_title("Funding Amount by Funding Type")
ax3.set_xlabel("Funding Type")
ax3.set_ylabel("Funding Amount")
ax3.tick_params(axis='x', labelsize=8)
ax3.set_ylim(0, 3000000)
ax3.yaxis.set_major_locator(plt.MultipleLocator(500000))
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:.1f}M".format(x/1000000)))
for i, v in enumerate(fund_grps['Funding Amount']):
  ax3.text(i, v + max(fund_grps['Funding Amount']) * 0.01, "${:,.0f}".format(v), ha='center', va='bottom')

plt.show()


cat_data = pd.read_csv('data/category_data.csv')

# ----- CATEGORY VISUALIZATIONS PT. 1 -----
# Subplots (from cat_data):
# 1. bar chart, 'Category' vs. 'Count'
# Subplots (from proj_data):
# 1. bar chart, grouped by 'WRRI Science Priority', count of projects in each priority
# Figure arrangement:
# 1 row, 3 columns (first subplot on left, first subplot legend in middle, second subplot on right)
# all subplots should use legends instead of direct labels

cat_bar_fig = plt.figure(figsize=(24, 12))

# Subplot 1: Category vs. Count
# title: Category Usage
# y label: # of Projects Using Category
# x labels: none (use legend instead)
# legend: each category
# put number on top of each bar
# put percentages just below top of bar
ax1 = cat_bar_fig.add_subplot(1, 1, 1)
colors1 = plt.cm.Set3(range(len(cat_data)))
bars1 = ax1.bar(cat_data['Category'], cat_data['Count'], color=colors1)
ax1.set_xticks([])
ax1.set_title('Category Usage')
ax1.set_ylabel('# of Projects Using Category')
ax1.legend(bars1, cat_data['Category'], title='Categories', loc='upper right')
for i, v in enumerate(cat_data['Count']):
  ax1.text(i, v + 0.125, str(v), ha='center', va='bottom')
  percentage = (v / cat_data['Count'].sum()) * 100
  ax1.text(i, v - 0.25, f'{percentage:.1f}%', ha='center', va='top')


# Subplot 2: WRRI Science Priority vs. Project Count
# title: WRRI Science Priority vs. Project Count
# y label: # of Projects
# x labels: none (use legend instead)
# legend: each category
# put number on top of each bar
# put percentages just below top of bar
wrri_counts = proj_data['WRRI Science Priority'].value_counts()
ax2 = cat_bar_fig.add_subplot(1, 3, 2)
colors2 = plt.cm.Pastel1(range(len(wrri_counts)))
bars2 = ax2.bar(wrri_counts.index, wrri_counts.values, color=colors2)
ax2.set_title('WRRI Science Priority vs. Project Count')
ax2.set_xticks([])
ax2.set_ylabel('# of Projects')
ax2.legend(bars2, wrri_counts.index, title='WRRI Science Priorities', loc='upper right')
for i, v in enumerate(wrri_counts.values):
  ax2.text(i, v + 0.125, str(v), ha='center', va='bottom')
  percentage = (v / wrri_counts.sum()) * 100
  ax2.text(i, v - 0.25, f'{percentage:.1f}%', ha='center', va='top')

plt.tight_layout()
cat_bar_fig.savefig('saved_figs/category_bar_visualizations.png')