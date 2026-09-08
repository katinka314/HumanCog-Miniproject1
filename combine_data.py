import csv
import glob
import os

import pandas as pd

DATA_DIR = "Result"
OUT_FILE = "all_data.csv"

# Condition names, longest first so "free_recall_baseline" is matched
# before "baseline". Older versions of the scripts used different file
# names for the same condition.
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

TASKS = {
    "baseline": "free_recall",
    "1A": "free_recall",
    "1B": "free_recall",
    "1C": "free_recall",
    "2C": "free_recall",
    "serial_baseline": "serial_recall",
    "2D": "serial_recall",
    "2E": "serial_recall",
}

COLUMNS = [
    "condition",
    "task",
    "participant",
    "trial",
    "sentence",
    "list_length",
    "presentation_ms",
    "presented_words",
    "recalled_words",
    "score",
    "presentation_start_time",
    "presentation_end_time",
    "recall_start_time",
]

# Column layouts written by the older versions of the scripts
LEGACY_SHORT = ["participant", "trial", "presented_words", "recalled_words", "score"]
LEGACY_LONG = LEGACY_SHORT + [
    "presentation_start_time",
    "presentation_end_time",
    "recall_start_time",
]
# Old 2C wrote a "sentence" value that was missing from its header
LEGACY_2C = ["participant", "trial", "sentence", "presented_words", "recalled_words",
             "score", "presentation_start_time", "presentation_end_time",
             "recall_start_time"]

def condition_from_filename(path):
    stem = os.path.basename(path)[:-4]
    for prefix, condition in CONDITION_PREFIXES:
        if stem.startswith(prefix):
            return condition
    return "unknown"

def normalise_words(value):
    """Old files separated words with spaces, new ones with '|'."""
    if not isinstance(value, str) or "|" in value:
        return value
    return "|".join(value.split())

def read_legacy(path, rows, condition):
    """Map a pre-fix CSV onto the current column layout."""
    width = max(len(r) for r in rows)
    if condition == "2C" and width == len(LEGACY_2C):
        names = LEGACY_2C
    elif width == len(LEGACY_LONG):
        names = LEGACY_LONG
    elif width == len(LEGACY_SHORT):
        names = LEGACY_SHORT
    else:
        print(f"  ! {os.path.basename(path)}: unrecognised layout ({width} columns), skipped")
        return None

    df = pd.DataFrame([r for r in rows if len(r) == width], columns=names)
    df["condition"] = condition
    df["task"] = TASKS.get(condition)
    # presentation_ms was not recorded before, and list_length is recoverable
    # from the presented words themselves
    df["presentation_ms"] = pd.NA
    df["list_length"] = df["presented_words"].apply(lambda s: len(str(s).split()))
    return df

def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None

    header, data = rows[0], rows[1:]
    if "condition" in header:
        df = pd.DataFrame([r for r in data if len(r) == len(header)], columns=header)
        df["format"] = "current"
        # Free recall and serial recall name their score column differently
        df = df.rename(columns={"serial_position_score": "score",
                                "serial_recall_score": "score"})
    else:
        df = read_legacy(path, data, condition_from_filename(path))
        if df is None:
            return None
        df["format"] = "legacy"

    for column in COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    for column in ("presented_words", "recalled_words", "score"):
        df[column] = df[column].apply(normalise_words)

    df["source_file"] = os.path.basename(path)
    return df[COLUMNS + ["format", "source_file"]]

def main():
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))

    frames = []
    for path in paths:
        df = load(path)
        if df is not None and not df.empty:
            frames.append(df)

    if not frames:
        print(f"No data found in {DATA_DIR}/")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUT_FILE, index=False)

    legacy = (combined["format"] == "legacy").sum()
    print(f"Combined {len(frames)} files -> {OUT_FILE} ({len(combined)} rows)")
    if legacy:
        print(f"{legacy} rows came from older versions of the scripts; "
              f"their presentation_ms is empty.")
    print()
    print(combined.groupby(["condition", "participant"]).size())

if __name__ == "__main__":
    main()
