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
# aggregate to get count of projects and sum of 'Funding Amount' in each priority
# sort by funding amount descending
inst_grps = proj_data.groupby('PI Affiliated Organization', as_index=False, dropna=True).agg(
  **{'Project Count': ('Project ID', 'size'), 'Funding Amount': ('Funding Amount', 'sum')}
).sort_values('Project Count', ascending=False)

# rename 'PI Afilliated Organization' to 'Institution'
inst_grps.rename(columns={'PI Affiliated Organization': 'Institution'}, inplace=True)

# add line breaks to institution for better visualization
inst_grps['Institution'] = inst_grps['Institution'].apply(wrap_label)


# ----- INSTITUTION VISUALIZATIONS -----
# Subplots (from inst_grps):
# 1. bar chart, 'Institution' vs 'Funding Amount', only include biggest number
# 2. bar chart, 'Institution' vs 'Funding Amount', only include second biggest number
# 2. bar chart, 'Institution' vs 'Funding Amount', include all but two biggest numbers
# Additional info to display:
# 1. The relative length of the bar in figure 1, if 1500000 is "1"
# 2. The relative length of the bar in figure 2, if 300000 is "1"
# 3. The relative lengths of the bars in figure 3, if 30000 is "1"
# Figure arrangement:
# 2 rows, 2 columns (first two subplots on top row, third subplot on bottom left, additional info on bottom right)

inst_fig = plt.figure(figsize=(12, 8))

# Subplot 1: largest funding amount
# y label: funding provided
# y tick marks go from 0 to 1.5 million
# y axis formatted as currency in units of 1.XXM
# put amount on top of bar
ax1 = inst_fig.add_subplot(2, 2, 1)
inst_sorted = inst_grps.sort_values('Funding Amount', ascending=False)
largest_inst = inst_sorted.iloc[0]
ax1.bar([largest_inst['Institution']], [largest_inst['Funding Amount']])
ax1.set_title('Institution vs. Funding Amount (Largest)')
ax1.tick_params(axis='x', labelsize=8)
ax1.set_ylabel('Funding Provided')
ax1.set_ylim(0, 1500000)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.2f}M'))
ax1.text(0, largest_inst['Funding Amount'] + 25000, f"${largest_inst['Funding Amount']:,.0f}", ha='center', va='bottom')

# Subplot 2: second largest funding amount
# y label: funding provided
# y tick marks go from 0 to 300 thousand
# y axis formatted as currency in units of 1XXK
# put amount on top of bar
ax2 = inst_fig.add_subplot(2, 2, 2)
second_inst = inst_sorted.iloc[1]
ax2.bar([second_inst['Institution']], [second_inst['Funding Amount']])
ax2.set_title('Institution vs. Funding Amount (Second Largest)')
ax2.tick_params(axis='x', labelsize=8)
ax2.set_ylabel('Funding Provided')
ax2.set_ylim(0, 300000)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
ax2.text(0, second_inst['Funding Amount'] + 5000, f"${second_inst['Funding Amount']:,.0f}", ha='center', va='bottom')

# Subplot 3: remaining institutions
# y label: funding provided
# y tick marks go from 0 to 35 thousand
# y axis formatted as currency in units of 1X.XK
# put amount on top of each bar
ax3 = inst_fig.add_subplot(2, 2, 3)
remaining_insts = inst_sorted.iloc[2:]
ax3.bar(remaining_insts['Institution'], remaining_insts['Funding Amount'])
ax3.set_title('Institution vs. Funding Amount (Remaining)')
ax3.tick_params(axis='x', labelsize=8)
ax3.set_ylabel('Funding Provided')
ax3.set_ylim(0, 35000)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.1f}K'))
for i, v in enumerate(remaining_insts['Funding Amount']):
  ax3.text(i, v + 500, f'${v:,.0f}', ha='center', va='bottom')


# Additional info to display:
# 1. The relative length of the bar in figure 1, with 1500000 being "1"
# 2. The relative length of the bar in figure 2, with 300000 being "1"
# 3. The relative lengths of the bars in figure 3, with 30000 is "1"
# for all: strip newline characters from institution names for clarity, list number to 4 decimal places
info_text = "Relative Lengths of Funding Amount Bars:\n"
largest_name = largest_inst['Institution'].replace('\n', ' ')
second_name = second_inst['Institution'].replace('\n', ' ')
info_text += f"{largest_name} (1,500,000 = 1): {largest_inst['Funding Amount'] / 1500000:.4f}\n"
info_text += f"{second_name} (300,000 = 1): {second_inst['Funding Amount'] / 300000:.4f}\n"
for inst, amount in zip(remaining_insts['Institution'], remaining_insts['Funding Amount']):
  inst_name = inst.replace('\n', ' ')
  info_text += f"{inst_name} (30,000 = 1): {amount / 30000:.4f}\n"
ax4 = inst_fig.add_subplot(2, 2, 4)
ax4.axis('off')
ax4.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')


plt.tight_layout()
inst_fig.savefig('saved_figs/institution_visualizations.png')

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
# strip newlines from priority names for clarity
relative_lengths = science_grps['Funding Amount'] / 800000
info_text = "Relative Lengths of Funding Amount Bars (800,000 = 1):\n"
for priority, rel_length in zip(science_grps['WRRI Science Priority'], relative_lengths):
  priority_long = priority.replace('\n', ' ')
  info_text += f"{priority_long}: {rel_length:.4f}\n"
ax4 = science_fig.add_subplot(2, 2, 4)
ax4.axis('off')
ax4.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')


plt.tight_layout()
science_fig.savefig('saved_figs/science_priority_visualizations.png')