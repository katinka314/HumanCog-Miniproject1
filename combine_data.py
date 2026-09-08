import glob
import os

import pandas as pd

DATA_DIR = "Result"
OUT_FILE = "all_data.csv"

# -----------------------------------
# Merge every run's CSV into one table
# -----------------------------------
def main():
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))

    frames = []
    for path in paths:
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["source_file"] = os.path.basename(path)
        frames.append(df)

    if not frames:
        print(f"No data found in {DATA_DIR}/")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUT_FILE, index=False)

    print(f"Combined {len(frames)} files -> {OUT_FILE} ({len(combined)} rows)")
    print()
    print(combined.groupby(["condition", "participant"]).size())

if __name__ == "__main__":
    main()
