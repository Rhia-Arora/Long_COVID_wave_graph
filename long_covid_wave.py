import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np

#Load my excel data in (need only sheet 5)
df_raw = pd.read_excel(r"C:\Users\rhiaa\OneDrive\Documents\New folder\ONS dataset.xlsx", sheet_name="5", header=None)

#Build weekly dataframe and clean it (remove blanks)
weekly = df_raw.iloc[6:, [20,21, 22, 23, 24, 25]].copy() #ignore first 6 rows, use columns 21 to 26
weekly.columns = ["week_date", "avg_hosp", "wave1", "wave2", "wave3", "wave4"]
weekly = weekly.dropna(subset=["week_date"])
weekly["week_date"] = pd.to_datetime(weekly["week_date"])

for col in ["avg_hosp", "wave1", "wave2", "wave3", "wave4"]:
    weekly[col] = pd.to_numeric(weekly[col], errors="coerce")

weekly = weekly.dropna(subset=["avg_hosp"]).sort_values("week_date").reset_index(drop=True)

# Calculate bar width to exactly fill the 7-day gap between bars
dates = weekly["week_date"].values
bar_width = int((dates[1] - dates[0]) / np.timedelta64(1, 'D'))  # will be 7

# Characteristics of wave graphs
WAVE_COLOURS = {
    "wave1": "#E63946",
    "wave2": "#2196F3",
    "wave3": "#4CAF50",
    "wave4": "#FF9800",
}
WAVE_LABELS = {
    "wave1": "Wave 1  (14 Nov – 14 Dec 2023)",
    "wave2": "Wave 2  (12 Dec 2023 – 11 Jan 2024)",
    "wave3": "Wave 3  (9 Jan – 8 Feb 2024)",
    "wave4": "Wave 4  (6 Feb - 7 Mar 2024)",
}
BAR_ALPHA = 0.45 #transparency

# Figure layout
fig, ax1 = plt.subplots(figsize=(18, 8))
ax2 = ax1.twinx() #lets line and bars overlay on same chart with different axis
ax1.set_zorder(ax2.get_zorder() + 1)  # bring ax1 in front of ax2
ax1.patch.set_visible(False)           # keep the background transparent

# Plot wave bars on ax2 — width=7 days so bars touch with no gaps
for wave_col, colour in WAVE_COLOURS.items():
    wave_data = weekly.dropna(subset=[wave_col])
    ax2.bar(
        wave_data["week_date"],
        wave_data[wave_col],
        width=bar_width,
        align="center",
        color=colour,
        alpha=BAR_ALPHA,
        edgecolor="none",
        zorder=2,
    )

# Plot hospitalisation line on ax1
ax1.plot(
    weekly["week_date"],
    weekly["avg_hosp"],
    color="#1a1a2e",
    linewidth=2,
    zorder=5,
    label="Weekly avg COVID-19 hospitalisations",
)

ax1.set_xlim(pd.Timestamp("2020-03-01"), weekly["week_date"].max()) #Making the x axis start from the 01/03/2020 and end when my hospitalisation data ends 

# Vertical dashed lines at wave midpoints
wave_midpoints = {
    "Wave 1\nmidpoint": (pd.Timestamp("2023-11-29"), 1.02),#numbers are the heights I set them at so they don't overlap
    "Wave 2\nmidpoint": (pd.Timestamp("2023-12-31"), 0.96),
    "Wave 3\nmidpoint": (pd.Timestamp("2024-01-28"), 0.90),
    "Wave 4\nmidpoint": (pd.Timestamp("2024-02-26"), 0.84),
}

ax1.set_ylim(bottom=0)
y_max = weekly["avg_hosp"].max()

for label, (date, y_frac) in wave_midpoints.items():
    ax1.axvline(x=date, color="grey", linestyle="--", linewidth=1, alpha=0.7, zorder=4)

    ax1.text(
        date, y_max * y_frac, label,
        fontsize=10, color="black", ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6),
    )

# Axis labels and title 
ax1.set_xlabel("Date", fontsize=14, labelpad=10)
ax1.set_ylabel("Weekly avg COVID-19 Hospitalisations", fontsize=14, color="#000000")
ax2.set_ylabel(
    "Population Estimate — Self-Reported Long COVID Cases (weekly avg)",
    fontsize=14, color="#000000",
)
ax1.tick_params(axis="y", labelcolor="#1a1a2e")
ax2.tick_params(axis="y", labelcolor="#000000")


# Legend
hosp_line = plt.Line2D([0], [0], color="#1a1a2e", linewidth=2,
                        label="Weekly avg hospitalisations")
wave_patches = [
    mpatches.Patch(color=WAVE_COLOURS[w], alpha=BAR_ALPHA, label=WAVE_LABELS[w])
    for w in WAVE_COLOURS
]
ax1.legend(
    handles=[hosp_line] + wave_patches,
    loc="upper center", fontsize=14, framealpha=0.9,
)

# Grid and x-axis formatting
ax1.grid(axis="y", linestyle="--", alpha=0.3, zorder=1)
ax1.set_axisbelow(True)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=60, ha="right")

# Save and display it
plt.tight_layout()
plt.savefig(r"C:\Users\rhiaa\OneDrive\Documents\New folder\long_covid_chart.png", dpi=300, bbox_inches="tight")
print("Chart saved!")
plt.show() 