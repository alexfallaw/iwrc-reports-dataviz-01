import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import numpy as np
import textwrap

# utility function to clean currency strings
def clean_currency(x):
  if isinstance(x, str):
    return float(x.replace('$', '').replace(',', '').strip())
  
  return float(x)

# utility function to put new lines in a string
def wrap_label(label, width=15):
  return '\n'.join(textwrap.wrap(label, width=width))

xls = pd.ExcelFile('data\\Sample Data.xlsx')

for sheet in xls.sheet_names:
  df = pd.read_excel('data\\Sample Data.xlsx', sheet_name=sheet)
  df.to_csv(f'data\\{sheet}.csv', index=False)

proj_data = pd.read_csv('data\\projects_data.csv')
prod_data = pd.read_csv('data\\products_data.csv')
award_data = pd.read_csv('data\\awards_data.csv')


# clean funding amount column from proj_data
proj_data['Funding Amount'] = proj_data['Funding Amount'].apply(clean_currency)

# normalize values to all caps in 'Focus Category 1', 'Focus Category 2', 'Focus Category 3' columns from proj_data
for col in ['Focus Category 1', 'Focus Category 2', 'Focus Category 3']:
  proj_data[col] = proj_data[col].str.upper().str.strip()

# remove rows with 'inProgress' or 'inReview' in 'Product Stage' column from prod_data
prod_data = prod_data[~prod_data['Product Stage'].isin(['inProgress', 'inReview'])]


# new DF (from proj_data):
# use columns 'Undergraduates Supported by WRRA $', 'Masters Students Supported by WRRA $', 'PhD Students Supported by WRRA $', 'Postdocs Supported by WRRA $', 'Students Supported by Non-Federal (Matching) Funds'
# sum these columns to create dataframe with columns: 'Student Type', 'Student Count'
# student type values: 'Undergraduate', 'Masters', 'PhD', 'Postdoc', 'Non-Federal'
# student count values: sum of respective columns
student_cols = [
  'Undergraduates Supported by WRRA $',
  'Masters Students Supported by WRRA $',
  'PhD Students Supported by WRRA $',
  'Postdocs Supported by WRRA $',
  'Students Supported by Non-Federal (Matching) Funds'
]
student_types = ['Undergraduate', 'Masters', 'PhD', 'Postdoc', 'Non-Federal']
student_counts = []
for col in student_cols:
  total = proj_data[col].sum()
  student_counts.append(total)
stu_data = pd.DataFrame({
  'Student Type': student_types,
  'Student Count': student_counts
})


# new DF (from proj_data):
# group by 'WRRI Science Priority'
# aggregate to get count of projects and sum of 'Funding Amount' in each priority
# sort by project count descending
science_grps = proj_data.groupby('WRRI Science Priority', as_index=False, dropna=True).agg(
  **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
).sort_values('Project Count', ascending=False)

# change each priority name to add line breaks for better visualization
science_grps['WRRI Science Priority'] = science_grps['WRRI Science Priority'].apply(wrap_label)

print(science_grps.to_string())

# new DF (from proj_data):
# group by "PI Affiliated Organization"
# aggregate to get count of projects and sum of 'Funding Amount' in each institut
# sort by funding amount ascending
inst_grps = proj_data.groupby('PI Affiliated Organization', as_index=False, dropna=True).agg(
  **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
).sort_values('Funding Amount', ascending=True)

# rename 'PI Afilliated Organization' to 'Institution'
inst_grps.rename(columns={'PI Affiliated Organization': 'Institution'}, inplace=True)

# remove 'Basil's Harvest' and 'National Great Rivers Research & Education Center' rows
inst_grps = inst_grps[~inst_grps['Institution'].isin(["Basil's Harvest", "National Great Rivers Research & Education Center"])]


# add line breaks to institution for better visualization
inst_grps['Institution'] = inst_grps['Institution'].apply(wrap_label)

print(inst_grps.to_string())


# # new DF (from proj_data and proj_data 2):
# # group each by "PI Affiliated Organization" and aggregate for count of projects and sum of 'Funding Amount'
# # combine into 1 dataframe with columns 'Institution A' 'Count A' 'Funding Amount A' 'Insitution B' 'Count B' 'Funding Amount B'
# inst_grps_a = proj_data.groupby('PI Affiliated Organization', as_index=False, dropna=True).agg(
#   **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
# )
# inst_grps_b = proj_data_2.groupby('PI Affiliated Organization', as_index=False, dropna=True).agg(
#   **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
# )

# inst_grps_a = inst_grps_a.rename(columns={
#   'PI Affiliated Organization': 'Institution A',
#   'Project Count': 'Count A',
#   'Funding Amount': 'Funding Amount A'
# })
# inst_grps_b = inst_grps_b.rename(columns={
#   'PI Affiliated Organization': 'Institution B',
#   'Project Count': 'Count B',
#   'Funding Amount': 'Funding Amount B'
# })

# inst_compare = pd.merge(
#   inst_grps_a,
#   inst_grps_b,
#   left_on='Institution A',
#   right_on='Institution B',
#   how='outer'
# )
# inst_compare['Funding Amount Diff'] = (
#   inst_compare['Funding Amount B'].fillna(0) - inst_compare['Funding Amount A'].fillna(0)
# )

# print(inst_compare.to_string())

# ----- INSTITUTION VISUALIZATIONS -----
# Subplots (from inst_grps):
# 1. bar chart, 'Institution' vs 'Funding Amount'
# Additional info to display:
# 1. the relative lengths of the bars in figure 1
# Figure arrangement:
# 1 rows, 2 columns
# subplot in first column, take up 2/3 of figure space
# additional info in second column, take up 1/3 of figure space

inst_fig = plt.figure(figsize=(12, 8))
inst_gs = inst_fig.add_gridspec(1, 2, width_ratios=[2, 1])

# set up section scaling
min_1 = 0
max_1 = 32500
incr_1 = 2500.0
units_1 = (max_1 - min_1) / incr_1

# min_1 = 0
# max_1 = 22500
# incr_1 = 25000.0
# units_1 = (max_1 - min_1) / incr_1

min_2 = 225000
max_2 = 325000
incr_2 = 25000.0
units_2 = (max_2 - min_2) / incr_2

min_3 = 1350000
max_3 = 1550000
incr_3 = 50000.0
units_3 = (max_3 - min_3) / incr_3

# Subplot 1: Institutions by Funding Provided
# y label: Funding Amount
# x label: none
# arrange institutions in ascending order
# The largest amount will reach the 3rd section, the second largest amount will reach the 2nd section, and the remaining institutions will all go in the 1st section
# put amount on top of each bar

# split y axes
# make each tick increment the same visual length:
#   bottom has 7 increments (0-35k by 5k), middle has 1 increment (250-300k by 50k),
#   top has 2 increments (1.3-1.5M by 0.1M) -> height ratios [2, 1, 7]
inst_left_gs = inst_gs[0].subgridspec(3, 1, height_ratios=[units_3, units_2, units_1], hspace=0.05)
ax_top = inst_fig.add_subplot(inst_left_gs[0])
ax_mid = inst_fig.add_subplot(inst_left_gs[1], sharex=ax_top)
ax_bot = inst_fig.add_subplot(inst_left_gs[2], sharex=ax_top)

# plot bars on each axis
x = np.arange(len(inst_grps))
for ax in (ax_top, ax_mid, ax_bot):
  ax.bar(x, inst_grps['Funding Amount'])

# first section
# formatting: currency, 1XK
ax_bot.set_ylim(min_1, max_1)
ax_bot.set_yticks(np.arange(min_1, max_1 + 1, incr_1))
ax_bot.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v/1e3:.0f}K'))


for index, label in enumerate(ax_bot.yaxis.get_ticklabels()):
  if index % 2 != 0:
    label.set_visible(False)


# second section
# range: 250 thousand to 300 thousand
# tick increments: 50 thousand
# formatting: currency, 1XXK
ax_mid.set_ylim(min_2, max_2)
ax_mid.set_yticks(np.arange(min_2, max_2 + 1, incr_2))
ax_mid.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v/1e3:.0f}K'))

for index, label in enumerate(ax_mid.yaxis.get_ticklabels()):
  if index % 2 != 1:
    label.set_visible(False)

# third section
# range: 1.3 million to 1.5 million
# tick increments: 0.1 million
# formatting: currency, 1.XM
ax_top.set_ylim(min_3, max_3)
ax_top.set_yticks(np.arange(min_3, max_3 + 1, incr_3))
ax_top.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v/1e6:.1f}M'))

for index, label in enumerate(ax_top.yaxis.get_ticklabels()):
  if index % 2 != 1:
    label.set_visible(False)

# only show ticks on bottom axis
ax_bot.set_xticks(x)
ax_bot.set_xticklabels(inst_grps['Institution'], fontsize=8)
plt.setp(ax_top.get_xticklabels(), visible=False)
plt.setp(ax_mid.get_xticklabels(), visible=False)

# put funding amount on top of each bar
# formatting for values <100K: 1.XK
# formatting for values >100k and <1M: 1XXK
# formatting for values >1M: 1.XXM
def format_funding_label(value):
  if value < 10000:
    return f'${value/1e3:.2f}K'
  if value < 100000:
    return f'${value/1e3:.1f}K'
  if value < 1000000:
    return f'${value/1e3:.0f}K'
  return f'${value/1e6:.2f}M'

for i, amount in enumerate(inst_grps['Funding Amount']):
  if amount <= ax_bot.get_ylim()[1]:
    ax = ax_bot
  elif amount <= ax_mid.get_ylim()[1]:
    ax = ax_mid
  else:
    ax = ax_top
  ylim = ax.get_ylim()
  y_offset = 0.02 * (ylim[1] - ylim[0])
  ax.text(i, amount + y_offset, format_funding_label(amount), ha='center', va='bottom', fontsize=10, clip_on=False)

# put project count below each bar
for i, (count, amount) in enumerate(zip(inst_grps['Project Count'], inst_grps['Funding Amount'])):
  if amount <= ax_bot.get_ylim()[1]:
    ax = ax_bot
  elif amount <= ax_mid.get_ylim()[1]:
    ax = ax_mid
  else:
    ax = ax_top
  ylim = ax.get_ylim()
  y_offset = 0.02 * (ylim[1] - ylim[0])
  ax.text(i, amount - y_offset, f'{count}\nprojects', ha='center', va='top', fontsize=10, color='white', clip_on=False)

# Additional info to display:
# The relative lengths of the bars in figure 4, with the total height of the chart as "1"
# strip newline characters from institution names for clarity, list number to 5 decimal places
TOTAL_UNITS = units_1 + units_2 + units_3  # corresponds to y = 1,500,000

def broken_axis_height_units(value):
  if value <= max_1:
    return (value / incr_1)
  if value <= max_2:
    # Full bottom segment + middle partial 
    return units_1 + ((value - min_2) / incr_2)
  # value in top segment
  # Full bottom + middle + top partial
  return units_1 + units_2 + ((value - min_3) / incr_3)

info_text = f"Relative Lengths of Funding Amount Bars ({max_3} = 1.0):\n"
for inst, amount in zip(inst_grps['Institution'], inst_grps['Funding Amount']):
  inst_long = inst.replace('\n', ' ')
  rel_length = broken_axis_height_units(amount) / TOTAL_UNITS
  info_text += f"{inst_long}: {rel_length:.5f}\n"

info_text += f"Distance between tick marks: {(1 / TOTAL_UNITS):.5f}\nTotal number of tick marks: {TOTAL_UNITS:.0f}"

ax_info = inst_fig.add_subplot(inst_gs[1])
ax_info.axis('off')
ax_info.text(0.0, 0.5, info_text, fontsize=10, verticalalignment='center')


plt.tight_layout()
inst_fig.savefig('saved_figs/institution_visualizations.png')

# ----- INSTITUTION VISUALIZATIONS ALT -----
# Subplots (from inst_grps):
# 1. bar chart, 'Institution' vs 'Funding Amount'
# Additional info to display:
# 1. the relative lengths of the bars in figure 1
# Figure arrangement:
# 1 rows, 2 columns
# subplot in first column, take up 2/3 of figure space
# additional info in second column, take up 1/3 of figure space
inst_fig = plt.figure(figsize=(12, 8))
inst_gs = inst_fig.add_gridspec(1, 2, width_ratios=[2, 1])

# set up section scaling
min_1 = 0
max_1 = 325000
incr_1 = 25000.0
units_1 = (max_1 - min_1) / incr_1

min_2 = 1375000
max_2 = 1500000
incr_2 = 25000.0
units_2 = (max_2 - min_2) / incr_2

# Subplot 1: Institutions by Funding Provided
# y label: Funding Amount
# x label: none
# arrange institutions in ascending order
# put amount on top of each bar

# split y axes with matching tick scaling in each section
inst_left_gs = inst_gs[0].subgridspec(2, 1, height_ratios=[units_2, units_1], hspace=0.05)
ax_top = inst_fig.add_subplot(inst_left_gs[0])
ax_bot = inst_fig.add_subplot(inst_left_gs[1], sharex=ax_top)

x = np.arange(len(inst_grps))
for ax in (ax_top, ax_bot):
  ax.bar(x, inst_grps['Funding Amount'])

# first section (0 - 500k)
ax_bot.set_ylim(min_1, max_1)
ax_bot.set_yticks(np.arange(min_1, max_1 + 1, incr_1))
ax_bot.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v/1e3:.0f}K'))

for index, label in enumerate(ax_bot.yaxis.get_ticklabels()):
  if index % 2 != 0:
    label.set_visible(False)

# second section (1.0M - 1.5M)
ax_top.set_ylim(min_2, max_2)
ax_top.set_yticks(np.arange(min_2, max_2 + 1, incr_2))
ax_top.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v/1e6:.2f}M'))

for index, label in enumerate(ax_top.yaxis.get_ticklabels()):
  if index % 2 != 1:
    label.set_visible(False)

# only show ticks on bottom axis
ax_bot.set_xticks(x)
ax_bot.set_xticklabels(inst_grps['Institution'], fontsize=8)
plt.setp(ax_top.get_xticklabels(), visible=False)

# put funding amount on top of each bar
for i, amount in enumerate(inst_grps['Funding Amount']):
  if amount <= ax_bot.get_ylim()[1]:
    ax = ax_bot
  else:
    ax = ax_top
  ylim = ax.get_ylim()
  y_offset = 0.02 * (ylim[1] - ylim[0])
  ax.text(i, amount + y_offset, format_funding_label(amount), ha='center', va='bottom', fontsize=8, clip_on=False)


# Additional info to display:
# The relative lengths of the bars in figure 4, with the total height of the chart as "1"
# strip newline characters from institution names for clarity, list number to 5 decimal places
TOTAL_UNITS = units_1 + units_2  # corresponds to y = 1,500,000 with split scaling

def broken_axis_height_units_alt(value):
  if value <= max_1:
    return value / incr_1
  # value in top segment
  return units_1 + ((value - min_2) / incr_2)

info_text = f"Relative Lengths of Funding Amount Bars ({max_2} = 1.0):\n"
for inst, amount in zip(inst_grps['Institution'], inst_grps['Funding Amount']):
  inst_long = inst.replace('\n', ' ')
  rel_length = broken_axis_height_units_alt(amount) / TOTAL_UNITS
  info_text += f"{inst_long}: {rel_length:.5f}\n"

info_text += f"Distance between tick marks: {(1 / TOTAL_UNITS):.5f}\nTotal number of tick marks: {TOTAL_UNITS:.0f}"

ax_info = inst_fig.add_subplot(inst_gs[1])
ax_info.axis('off')
ax_info.text(0.0, 0.5, info_text, fontsize=10, verticalalignment='center')

plt.tight_layout()
inst_fig.savefig('saved_figs/institution_visualizations_alt.png')


# ----- FUNDING VISUALIZATIONS -----
# Subplots (from proj_data):
# 1. bar chart, 'Funding Type' vs. # of projects
# 2. bar chart, 'Funding Type' vs. 'Funding Amount'
# 3. bar chart, 'Funding Type' vs. average 'Funding Amount'
# Additional info to display:
# 1. total number of projects (sum of counts from first subplot)
# 2. total funding amount (sum of 'Funding Amount' column)
# 3. average funding amount (average of 'Funding Amount' column)
# Figure arrangement:
# 2 rows, 2 columns (first two subplots on top row, third subplot on bottom left, additional info on bottom right)

funding_fig = plt.figure(figsize=(12, 8))

# Subplot 1: Funding Type vs. Project Count
# sort by project count descending
# y label: # of Projects
# y tick marks go from 0 to 25 in increments of 5
# put number on top of each bar
ax1 = funding_fig.add_subplot(2, 2, 1)
funding_type_counts = proj_data['Funding Type'].value_counts()
ax1.bar(funding_type_counts.index, funding_type_counts.values)
ax1.set_title('Funding Type vs. Project Count')
ax1.tick_params(axis='x', labelsize=8)
ax1.set_ylabel('# of Projects')
ax1.set_ylim(0, 25)
for i, (category, count) in enumerate(funding_type_counts.items()):
  ax1.text(i, count + 0.125, str(count), ha='center', va='bottom')

# Subplot 2: Funding Type vs. Total Funding Amount
# sort by total funding amount descending
# y label: Total Funding Amount
# put number on top of each bar
# y axis formatted as currency in units of 1.XM
# y tick marks go from 0 to 3,000,000 in increments of 500,000
ax2 = funding_fig.add_subplot(2, 2, 2)
funding_amounts = proj_data.groupby('Funding Type')['Funding Amount'].sum().sort_values(ascending=False)
ax2.bar(funding_amounts.index, funding_amounts.values)
ax2.set_title('Funding Type vs. Total Funding Amount')
ax2.tick_params(axis='x', labelsize=8)
ax2.set_ylabel('Total Funding Amount')
ax2.set_ylim(0, 3000000)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
for i, (category, amount) in enumerate(funding_amounts.items()):
  ax2.text(i, amount + 25000, f'${amount/1e6:.1f}M', ha='center', va='bottom')

# Subplot 3: Funding Type vs. Average Funding Per Project
# sort by average funding amount descending
# y label: Average Funding Per Project
# put number on top of each bar
# if number is > 235000, put number just below top of bar instead and make it white
# y axis formatted as currency in units of 1.XK
ax3 = funding_fig.add_subplot(2, 2, 3)
funding_averages = proj_data.groupby('Funding Type')['Funding Amount'].mean().sort_values(ascending=False)
ax3.bar(funding_averages.index, funding_averages.values)
ax3.set_title('Funding Type vs. Average Funding Per Project')
ax3.tick_params(axis='x', labelsize=8)
ax3.set_ylabel('Average Funding Per Project')
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.1f}K'))
for i, (category, avg_amount) in enumerate(funding_averages.items()):
  if avg_amount > 235000:
    ax3.text(i, avg_amount - 5000, f'${avg_amount/1e3:.1f}K', ha='center', va='top', color='white')
  else:
    ax3.text(i, avg_amount + 2500, f'${avg_amount/1e3:.1f}K', ha='center', va='bottom')

# Additional info to display:
# 1. total number of projects (sum of counts from first subplot)
# 2. total funding amount (sum of 'Funding Amount' column)
# 3. average funding amount (average of 'Funding Amount' column)

funding_info = {
  'total_projects': len(proj_data),
  'total_funding': proj_data['Funding Amount'].sum(),
  'average_funding': proj_data['Funding Amount'].mean()
}
info_text = (f"Total Projects: {funding_info['total_projects']}\n"
             f"Total Funding Amount: ${funding_info['total_funding']:,.2f}\n"
             f"Average Funding Per Project: ${funding_info['average_funding']:,.2f}")
ax4 = funding_fig.add_subplot(2, 2, 4)
ax4.axis('off')
ax4.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')

plt.tight_layout()
funding_fig.savefig('saved_figs/funding_visualizations.png')


# ----- STUDENT VISUALIZATIONS -----
# Subplots (from stu_data):
# 1. bar chart, 'Student Type' vs. 'Student Count'
# Additional info to display:
# 1. total number of students supported by WRRA $ (sum of 'Student Count' excluding 'Non-Federal')
# 2. total number of students supported (sum of all 'Student Count' values)
# Figure arrangement:
# 1 row, 2 columns (first subplot on left, additional info on right)

student_fig = plt.figure(figsize=(10, 5))

# Subplot 1: Student Type vs. Student Count
ax1 = student_fig.add_subplot(1, 2, 1)
ax1.bar(stu_data['Student Type'], stu_data['Student Count'])
ax1.set_title('Student Type vs. Student Count')
ax1.tick_params(axis='x', labelsize=8)
ax1.set_ylabel('Student Count')
for i, v in enumerate(stu_data['Student Count']):
  ax1.text(i, v + 0.125, str(v), ha='center', va='bottom')

# Additional info to display:
# 1. total number of students supported by WRRA $ (sum of 'Student Count' excluding 'Non-Federal')
# 2. total number of students supported (sum of all 'Student Count' values)
total_wrra_students = stu_data[stu_data['Student Type'] != 'Non-Federal']['Student Count'].sum()
total_students = stu_data['Student Count'].sum()
info_text = (f"Total Students Supported by WRRA Funding: {total_wrra_students}\n"
             f"Total Students Supported: {total_students}")
ax3 = student_fig.add_subplot(1, 2, 2)
ax3.axis('off')
ax3.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')

plt.tight_layout()
student_fig.savefig('saved_figs/student_visualizations.png')


# ----- SCIENCE PRIORITY VISUALIZATIONS -----
# Subplots (from science_grps):
# 1. bar chart, 'WRRI Science Priority' vs. 'Project Count'
# 2. pie chart, 'WRRI Science Priority' vs. 'Project Count'
# 3. bar chart, 'WRRI Science Priority' vs. 'Funding Amount'
# Additional info to display:
# The relative lengths of each bar in subplot 3, with 800000 being "1"
# The degrees that correspond to each section of the pie chart in subplot 2
# Figure arrangement:
# 2 rows, 2 columns (first subplot on top left, second subplot on top right, third subplot on bottom left, bottom right additional info)

science_fig = plt.figure(figsize=(16, 12))

# Subplot 1: WRRI Science Priority vs. Project Count
ax1 = science_fig.add_subplot(2, 2, 1)
ax1.bar(science_grps['WRRI Science Priority'], science_grps['Project Count'])
ax1.set_title('WRRI Science Priority vs. Project Count')
ax1.tick_params(axis='x', labelsize=8)
ax1.set_ylabel('# of Projects')
for i, v in enumerate(science_grps['Project Count']):
  ax1.text(i, v + 0.125, str(v), ha='center', va='bottom')

# Subplot 2: WRRI Science Priority vs. Project Count (Pie Chart)
ax2 = science_fig.add_subplot(2, 2, 2)
colors = cm.Pastel1(np.linspace(0, 1, len(science_grps)))
ax2.pie(science_grps['Project Count'], labels=science_grps['WRRI Science Priority'], autopct='%1.1f%%', colors=colors, textprops={'fontsize': 8})
ax2.set_title('WRRI Science Priority vs. Project Count (Pie Chart)')


# Subplot 3: WRRI Science Priority vs. Funding Amount
# y axis formatted as currency in units of XK (thousands)
# put number on top of each bar in full currency format without cents
# re-sort bars to be in descending order of funding amount
ax3 = science_fig.add_subplot(2, 2, 3)
science_grps = science_grps.sort_values(by='Funding Amount', ascending=False)
ax3.bar(science_grps['WRRI Science Priority'], science_grps['Funding Amount'])
ax3.set_title('WRRI Science Priority vs. Funding Amount')
ax3.tick_params(axis='x', labelsize=8)
ax3.set_ylabel('Funding Amount')
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
for i, v in enumerate(science_grps['Funding Amount']):
  ax3.text(i, v + 12500, f'${v:,.0f}', ha='center', va='bottom')

# Additional info to display:
# The relative lengths of each bar in subplot 3 to 4 decimal places, with 800000 being "1"
# The degrees that correspond to each section of the pie chart in subplot 2
# strip newlines from priority names for clarity
relative_lengths = science_grps['Funding Amount'] / 800000
info_text = "Relative Lengths of Funding Amount Bars (800,000 = 1):\n"
for priority, rel_length in zip(science_grps['WRRI Science Priority'], relative_lengths):
  priority_long = priority.replace('\n', ' ')
  info_text += f"{priority_long}: {rel_length:.4f}\n"

science_grps.sort_values(by=['Project Count'], inplace=True, ascending=False)

total_projects = science_grps['Project Count'].sum()
relative_degrees = (science_grps['Project Count'] / total_projects) * 360
info_text += "\nDegrees Per Pie Slice:\n"
for priority, degrees in zip(science_grps['WRRI Science Priority'], relative_degrees):
  priority_long = priority.replace('\n', ' ')
  info_text += f"{priority_long}: {degrees:.1f}\n"

ax4 = science_fig.add_subplot(2, 2, 4)
ax4.axis('off')
ax4.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')


plt.tight_layout()
science_fig.savefig('saved_figs/science_priority_visualizations.png')
