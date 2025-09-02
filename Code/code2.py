import pandas as pd
import glob
import os

# Grab all uploaded CSV files in the current working directory
csv_files = glob.glob("*.csv")

# List to store result for each file
summary_data = []

for file_path in csv_files:
    try:
        df = pd.read_csv(file_path)

        # Ensure 'prcp(mm/day)' is numeric
        df['prcp(mm/day)'] = pd.to_numeric(df['prcp(mm/day)'], errors='coerce')

        # Convert 'Date' column to datetime format
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        # Drop the 'pet_gleam(mm/day)' column if it exists
        if 'pet_gleam(mm/day)' in df.columns:
            df = df.drop(columns=['pet_gleam(mm/day)'])

        # Filter for zero precipitation
        df = df[df['prcp(mm/day)'] == 0]

        # Ensure strictly decreasing streamflow
        df = df.loc[df['Streamflow'].diff().lt(0) | df['Streamflow'].diff().isna()]

        # Identify date gaps and group
        df['date_diff'] = df['Date'].diff().fillna(pd.Timedelta(days=1)).dt.days.astype(int)
        df['group'] = (df['date_diff'] > 1).cumsum()

        # Remove first 3 rows of each group (if size > 3)
        filtered = df.groupby('group').apply(lambda x: x.iloc[3:] if len(x) > 3 else x).reset_index(drop=True)

        # Keep only groups with at least 6 rows
        valid_groups = filtered['group'].value_counts()
        valid_groups = valid_groups[valid_groups >= 6].index
        filtered = filtered[filtered['group'].isin(valid_groups)]

        # Drop helper columns
        filtered = filtered.drop(columns=['date_diff', 'group'])

        # Add blank rows between event groups
        output = []
        for _, group in filtered.groupby((filtered['Date'].diff() > pd.Timedelta(days=1)).cumsum()):
            output.append(group)
            output.append(pd.DataFrame({col: [''] for col in group.columns}))

        # Check and concatenate only if there's data
        if output:
            final_result = pd.concat(output, ignore_index=True)

            # Convert Streamflow to numeric
            final_result['Streamflow'] = pd.to_numeric(final_result['Streamflow'], errors='coerce')

            # Split Streamflow column into sublists, separated by NaNs
            sublists = [group["Streamflow"].tolist() for _, group in final_result[final_result["Streamflow"].notna()].groupby((final_result["Streamflow"].isna()).cumsum())]

            # Record the number of valid events
            summary_data.append({
                'filename': os.path.basename(file_path),
                'num_events': len(sublists)
            })
        else:
            summary_data.append({
                'filename': os.path.basename(file_path),
                'num_events': 0
            })
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        summary_data.append({
            'filename': os.path.basename(file_path),
            'num_events': 'error'
        })

# Save summary as a CSV
summary_df = pd.DataFrame(summary_data)
summary_df.to_csv("event_counts_summary.csv", index=False)

# Display summary
summary_df
