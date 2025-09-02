import pandas as pd

# Load the CSV file
file_path = '3002.csv'
df = pd.read_csv(file_path)

# Ensure the 'prcp(mm/day)' column is numeric
df['prcp(mm/day)'] = pd.to_numeric(df['prcp(mm/day)'], errors='coerce')

# Convert 'Date' column to datetime format and keep only the date
df['Date'] = pd.to_datetime(df['Date']).dt.date

# Drop the 'pet_gleam(mm/day)' column (no longer needed)
df = df.drop(columns=['pet_gleam(mm/day)'])

# Filter rows where precipitation is zero
df = df[df['prcp(mm/day)'] == 0]

# Ensure strictly decreasing streamflow
df = df.loc[df['Streamflow'].diff().lt(0) | df['Streamflow'].diff().isna()]

# Identify gaps between consecutive dates
df['date_diff'] = df['Date'].diff().fillna(pd.Timedelta(days=1)).dt.days.astype(int)

# Define groups based on consecutive dates
df['group'] = (df['date_diff'] > 1).cumsum()

# Remove the first 3 rows from each group (if size > 3)
filtered = df.groupby('group').apply(lambda x: x.iloc[3:] if len(x) > 3 else x).reset_index(drop=True)

# Keep only groups with at least 6 rows
valid_groups = filtered['group'].value_counts()
valid_groups = valid_groups[valid_groups >= 6].index
filtered = filtered[filtered['group'].isin(valid_groups)]

# Drop helper columns
filtered = filtered.drop(columns=['date_diff', 'group'])

# Add blank rows between groups
output = []
for _, group in filtered.groupby((filtered['Date'].diff() > pd.Timedelta(days=1)).cumsum()):
    output.append(group)  # Add the group
    output.append(pd.DataFrame({col: [''] for col in group.columns}))  # Add a blank row

# Concatenate the final results
final_result = pd.concat(output, ignore_index=True)

# Save the final result to a CSV file
final_result.to_csv('3002_filtered_results_final.csv', index=False)

# Show the final result (optional)
pd.set_option('display.max_rows', None)
print(final_result)
pd.reset_option('display.max_rows')
