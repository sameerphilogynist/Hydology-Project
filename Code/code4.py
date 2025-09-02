import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Step 1: Define the model function
def model(Q, a, b):
    return a * Q**b

# Step 2: Load the filtered CSV
df = pd.read_csv('3002_filtered_results.csv')

# Convert 'Streamflow' to numeric
df['Streamflow'] = pd.to_numeric(df['Streamflow'], errors='coerce')

# Step 3: Split into event groups (blank rows separate groups)
event_groups = [
    group["Streamflow"].dropna().reset_index(drop=True)
    for _, group in df[df["Streamflow"].notna()].groupby((df["Streamflow"].isna()).cumsum())
]

# Step 4: Fit model for each group and store results
results = []

for i, q_series in enumerate(event_groups, 1):
    if len(q_series) < 2:
        results.append({"event": i, "a": np.nan, "b": np.nan})
        continue

    Q = q_series[:-1].values
    dQ = q_series.diff().dropna().values
    delta_Q = -dQ

    try:
        popt, _ = curve_fit(model, Q, delta_Q, p0=[1, 1], maxfev=10000)
        a, b = popt
        results.append({"event": i, "a": a, "b": b})
    except:
        results.append({"event": i, "a": np.nan, "b": np.nan})

# Step 5: Create result DataFrame and save as CSV
results_df = pd.DataFrame(results)
results_df.to_csv("3002_ab_parameters.csv", index=False)

# Step 6: Calculate median
valid_results = results_df.dropna(subset=['a', 'b'])
median_a = valid_results['a'].median()
median_b = valid_results['b'].median()

# Step 7: Append median row for display
results_df_display = results_df.copy()
results_df_display[['a', 'b']] = results_df_display[['a', 'b']].round(4)

median_row = pd.DataFrame([{
    "event": "Median",
    "a": round(median_a, 4),
    "b": round(median_b, 4)
}])

results_df_display = pd.concat([results_df_display, median_row], ignore_index=True)

# Step 8: Save as PDF table
fig, ax = plt.subplots(figsize=(8, 0.5 + 0.4 * len(results_df_display)))
ax.axis('off')
table = ax.table(
    cellText=results_df_display.values,
    colLabels=results_df_display.columns,
    loc='center',
    cellLoc='center'
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)

plt.savefig("3002_ab_parameters.pdf", bbox_inches="tight")
plt.show()

# Print medians
print(f"Median of a: {median_a:.4f}")
print(f"Median of b: {median_b:.4f}")
