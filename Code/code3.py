import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Load the CSV files
events_df = pd.read_csv("events_count.csv")
info_df = pd.read_csv("Data_Information.csv")

# Normalize column names (optional but good for safety)
info_df.columns = info_df.columns.str.upper()
events_df["GAGE_ID"] = events_df["filename"].str.replace(".csv", "", regex=False).astype(str)
info_df["GAGE_ID"] = info_df["GAGE_ID"].astype(str)

# Merge the two DataFrames
merged = pd.merge(info_df, events_df, on="GAGE_ID")

# Plotting the map
fig = plt.figure(figsize=(10, 12))
ax = plt.axes(projection=ccrs.PlateCarree())

# South India extent
ax.set_extent([73, 86, 8, 24], crs=ccrs.PlateCarree())

# Add features
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.STATES, edgecolor='gray')

# Scatter plot
sc = ax.scatter(
    merged["LONGITUDE"],
    merged["LATITUDE"],
    c=merged["num_events"],
    cmap='Oranges',
    s=60,
    edgecolor='black',
    vmin=0,
    vmax=merged["num_events"].max(),
    transform=ccrs.PlateCarree()
)

# Colorbar
cbar = plt.colorbar(sc, ax=ax, shrink=0.6, pad=0.03)
cbar.set_label("No. of Events", fontsize=12)


# Add gridlines with labels
gl = ax.gridlines(draw_labels=True, linestyle="--", color="gray", alpha=0.5)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {"size": 10}
gl.ylabel_style = {"size": 10}
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()



# Title
plt.title("Event Distribution Across South India", fontsize=16)
plt.savefig("south_india_event_map.pdf", format="pdf", bbox_inches="tight")
plt.show()
