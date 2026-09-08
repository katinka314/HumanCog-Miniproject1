import csv
import glob
import os

import pandas as pd

DATA_DIR = "Result"
OUT_FILE = "all_data.csv"

# Which condition a result file belongs to, taken from the start of its name.
# Longest first, so "free_recall_baseline" wins over "baseline". Older versions
# of the scripts used a different name for the baseline files.
CONDITION_PREFIXES = [
    ("free_recall_baseline", "baseline"),
    ("serial_baseline", "serial_baseline"),
    ("baseline", "baseline"),
    ("1A", "1A"),
    ("1B", "1B"),
    ("1C", "1C"),
    ("2C", "2C"),
    ("2D", "2D"),
    ("2E", "2E"),
]

# The 2C script used to write a sentence value that was missing from its
# header, so those files have one more value per row than they have columns.
OLD_2C_COLUMNS = [
    "participant",
    "trial",
    "sentence",
    "presented_words",
    "recalled_words",
    "serial_recall_score",
    "presentation_start_time",
    "presentation_end_time",
    "recall_start_time",
]

def condition_from_filename(path):
    stem = os.path.basename(path)[:-4]
    for prefix, condition in CONDITION_PREFIXES:
        if stem.startswith(prefix):
            return condition
    return "unknown"

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None

    header, data = rows[0], rows[1:]
    condition = condition_from_filename(path)
    if condition == "unknown":
        print(f"  ! {os.path.basename(path)}: cannot tell which condition this is "
              f"from the file name, skipped")
        return None
    width = max(len(r) for r in data)

    if width == len(header):
        columns = header
    elif condition == "2C" and width == len(OLD_2C_COLUMNS):
        # Written before the missing sentence column was added to the header
        columns = OLD_2C_COLUMNS
    else:
        print(f"  ! {os.path.basename(path)}: {width} values per row but "
              f"{len(header)} columns, skipped")
        return None

    df = pd.DataFrame([r for r in data if len(r) == width], columns=columns)

    # Free recall and serial recall name their score column differently
    df = df.rename(columns={"serial_position_score": "score",
                            "serial_recall_score": "score"})

    df.insert(0, "condition", condition)
    df["source_file"] = os.path.basename(path)
    return df

def main():
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))

    frames = [df for df in (load(p) for p in paths) if df is not None and not df.empty]
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
