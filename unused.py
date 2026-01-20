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