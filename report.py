import pandas as pd

CSV_FILE = "data/history.csv"

# Load data
df = pd.read_csv(CSV_FILE)

# ==============================
# Basic validation
# ==============================
if df.empty:
    print("No data available in history file.")
    exit()

# ==============================
# Convert units
# ==============================
df["hash_rate_5m_th"] = df["hash_rate_5m"] / 1000

farm_ph = df["hash_rate_5m"].sum() / 1_000_000

# ==============================
# Summary stats
# ==============================
workers_count = df["worker"].nunique()

avg_ph = df["hash_rate_5m"].mean() / 1_000_000
max_ph = df["hash_rate_5m"].max() / 1_000_000
min_ph = df["hash_rate_5m"].min() / 1_000_000

offline_workers = df[df["state"] == "off"]["worker"].unique()

# ==============================
# Per-worker average hashrate
# ==============================
avg_per_worker = (
    df.groupby("worker")["hash_rate_5m"]
    .mean()
    .sort_values(ascending=False)
)

best_worker = avg_per_worker.idxmax()
worst_worker = avg_per_worker.idxmin()

# ==============================
# REPORT OUTPUT
# ==============================
print("\n" + "=" * 50)
print("           BRAIINS MINING REPORT")
print("=" * 50)

print(f"\nWorkers: {workers_count}")

print(f"\n🌐 Farm Hashrate: {farm_ph:.3f} PH/s")

print(f"\n📊 Average Hashrate: {avg_ph:.3f} PH/s")
print(f"🔺 Max Hashrate: {max_ph:.3f} PH/s")
print(f"🔻 Min Hashrate: {min_ph:.3f} PH/s")

print("\n🚨 Offline Workers:")
if len(offline_workers) > 0:
    for w in offline_workers:
        print(f" - {w}")
else:
    print("None")

print("\n⚠️ Per Worker Hashrate (TH/s):")
for worker, value in avg_per_worker.items():
    print(f"{worker}: {value/1000:.2f} TH/s")

print("\n🏆 Best Worker:", best_worker)
print("🐌 Worst Worker:", worst_worker)

print("\n" + "=" * 50)