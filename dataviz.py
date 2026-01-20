import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import numpy as np

def clean_currency(x):
  if isinstance(x, str):
    return float(x.replace('$', '').replace(',', '').strip())
  
  return float(x)
    

proj_data = pd.read_csv('sample_projects.csv')
prod_data = pd.read_csv('sample_products.csv')
award_data = pd.read_csv('sample_awards.csv')

# clean funding amount column from proj_data
proj_data['Funding Amount'] = proj_data['Funding Amount'].apply(clean_currency)

# normalize values to all caps in 'Focus Category 1', 'Focus Category 2', 'Focus Category 3' columns from proj_data
proj_data['Focus Category 1'] = proj_data['Focus Category 1'].str.upper()
proj_data['Focus Category 2'] = proj_data['Focus Category 2'].str.upper()
proj_data['Focus Category 3'] = proj_data['Focus Category 3'].str.upper()

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
# use columns 'Focus Category 1', 'Focus Category 2', 'Focus Category 3'
# these columns may have overlapping categories, so we need to count unique occurrences of each category across all three columns
# create a single series with all categories, then count occurrences
all_categories = pd.concat([proj_data['Focus Category 1'], proj_data['Focus Category 2'], proj_data['Focus Category 3']])
category_counts = all_categories.value_counts()
cat_data = pd.DataFrame({
  'Category': category_counts.index,
  'Count': category_counts.values
})

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
ax2 = student_fig.add_subplot(1, 2, 2)
ax2.axis('off')
ax2.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center')

plt.tight_layout()
student_fig.savefig('saved_figs/student_visualizations.png')


# ----- CATEGORY VISUALIZATIONS PT. 1 -----
# Subplots (from cat_data):
# 1. bar chart, 'Category' vs. 'Count'
# Subplots (from proj_data):
# 1. bar chart, grouped by 'WRRI Science Priority', count of projects in each priority
# Figure arrangement:
# 1 row, 3 columns (first subplot on left, nothing in middle, second subplot on right)

cat_bar_fig = plt.figure(figsize=(24, 12))
gs = cat_bar_fig.add_gridspec(1, 2, width_ratios=[3, 2])

# Subplot 1: Category vs. Count
# title: Category Usage
# y label: # of Projects Using Category
# each category represented by a different color
# put percentage on top of each bar
ax1 = cat_bar_fig.add_subplot(gs[0, 0])
colors1 = plt.get_cmap('tab20', len(cat_data))(range(len(cat_data)))
bars1 = ax1.bar(cat_data['Category'], cat_data['Count'], color=colors1)
ax1.set_title('Category Usage')
ax1.set_ylabel('# of Projects Using Category')
ax1.set_xticks([])
ax1.margins(x=0.01)
ax1.legend(bars1, cat_data['Category'], title='Categories (for Category Usage)', loc='upper right')
for i, v in enumerate(cat_data['Count']):
  percentage = (v / cat_data['Count'].sum()) * 100
  ax1.text(i, v + 0.125, f'{percentage:.1f}%', ha='center', va='bottom')

# Subplot 2: WRRI Science Priority vs. Project Count
# title: WRRI Science Priority vs. Project Count
# y label: # of Projects
# put number on top of each bar
# put percentages just below top of bar
wrri_counts = proj_data['WRRI Science Priority'].value_counts()
ax2 = cat_bar_fig.add_subplot(gs[0, 1])
colors2 = plt.get_cmap('tab20', len(cat_data))(range(len(cat_data)))
bars2 = ax2.bar(wrri_counts.index, wrri_counts.values, color=colors2)
ax2.set_title('WRRI Science Priority vs. Project Count')
ax2.set_ylabel('# of Projects')
ax2.set_xticks([])
ax2.margins(x=0.01)
ax2.legend(bars2, wrri_counts.index, title='WRRI Science Priorities', loc='upper right')
for i, v in enumerate(wrri_counts.values):
  ax2.text(i, v + 0.125, str(v), ha='center', va='bottom')
  percentage = (v / wrri_counts.sum()) * 100
  ax2.text(i, v - 0.25, f'{percentage:.1f}%', ha='center', va='top')

plt.tight_layout()
cat_bar_fig.savefig('saved_figs/category_bar_visualizations.png')

# ----- CATEGORY VISUALIZATIONS PT. 2 -----
# Subplots (from proj_data):
# 1. pie chart, distribution of 'WRRI Science Priority' values
# 2. pie chart, distribution of 'Focus Category 1' values
# 3. pie chart, distribution of 'Focus Category 2' values
# 4. pie chart, distribution of 'Focus Category 3' values
# Figure arrangement:
# 2 rows, 2 columns (first subplot on top left, remaining subplots filling the rest of the grid)

cat_pie_fig = plt.figure(figsize=(12, 10))

# Subplot 3: Pie chart of WRRI Science Priority distribution
ax1 = cat_pie_fig.add_subplot(2, 2, 1)
ax1.pie(wrri_counts.values, labels=wrri_counts.index, autopct='%1.1f%%')
ax1.set_title('Distribution of WRRI Science Priorities')

# Subplot 4: Pie chart of Focus Category 1 distribution
focus_cat1_counts = proj_data['Focus Category 1'].value_counts()
ax2 = cat_pie_fig.add_subplot(2, 2, 2)
ax2.pie(focus_cat1_counts.values, labels=focus_cat1_counts.index, autopct='%1.1f%%')
ax2.set_title('Distribution of Focus Category 1')

# Subplot 5: Pie chart of Focus Category 2 distribution
focus_cat2_counts = proj_data['Focus Category 2'].value_counts()
ax3 = cat_pie_fig.add_subplot(2, 2, 3)
ax3.pie(focus_cat2_counts.values, labels=focus_cat2_counts.index, autopct='%1.1f%%')
ax3.set_title('Distribution of Focus Category 2')

# Subplot 6: Pie chart of Focus Category 3 distribution
focus_cat3_counts = proj_data['Focus Category 3'].value_counts()
ax4 = cat_pie_fig.add_subplot(2, 2, 4)
ax4.pie(focus_cat3_counts.values, labels=focus_cat3_counts.index, autopct='%1.1f%%')
ax4.set_title('Distribution of Focus Category 3')

plt.tight_layout()
cat_pie_fig.savefig('saved_figs/category_pie_visualizations.png')

# ----- PRODUCT VISUALIZATIONS -----
# Subplots (from prod_data):
# 1. bar chart, 'Product Type' vs. # of products
# Additional info to display:
# 1. total number of products (sum of counts from first subplot)

