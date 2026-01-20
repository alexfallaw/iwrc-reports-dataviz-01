import pandas as pd
import matplotlib.pyplot as plt
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

# remove rows with 'inProgress' or 'inReview' in 'Product Stage' column from prod_data
prod_data = prod_data[~prod_data['Product Stage'].isin(['inProgress', 'inReview'])]

# new DF (from proj_data):
# use columns 'Undergraduates Supported by WRRA$', 'Masters Students Supported by WRRA$', 'PhD Students Supported by WRRA$', 'Postdocs Supported by WRRA$', 'Students Supported by Non-Federal (Matching) Funds'
# sum these columns to create dataframe with columns: 'Student Type', 'Student Count'
# student type values: 'Undergraduate', 'Masters', 'PhD', 'Postdoc', 'Non-Federal'
# student count values: sum of respective columns
student_cols = [
  'Undergraduates Supported by WRRA$',
  'Masters Students Supported by WRRA$',
  'PhD Students Supported by WRRA$',
  'Postdocs Supported by WRRA$',
  'Students Supported by Non-Federal (Matching) Funds'
]
student_types = ['Undergraduate', 'Masters', 'PhD', 'Postdoc', 'Non-Federal']
student_counts = []
for col in student_cols:
  total = proj_data[col].sum()
  student_counts.append(total)
student_data = pd.DataFrame({
  'Student Type': student_types,
  'Student Count': student_counts
})
print(student_data.to_string())

# ----- FUNDING VISUALIZATIONS -----
# subplots (from proj_data):
# 1. bar chart, 'Funding Type' vs. # of projects
# 2. bar chart, 'Funding Type' vs. funding amount


# ----- STUDENT VISUALIZATIONS -----
# subplots (from proj_data):
# 1. bar chart, student type vs. # of students

# ----- PRODUCT VISUALIZATIONS -----
# subplots (from prod_data):
# 1. bar chart, 'Product Type' vs. # of products
