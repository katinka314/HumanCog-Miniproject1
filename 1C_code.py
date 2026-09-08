import random
import csv
import os
import time
import tkinter as tk
from datetime import datetime

# -----------------------------------
# Experiment settings
# -----------------------------------
CONDITION = "1C"
TASK = "free_recall"
LIST_LENGTH = 15
PRESENTATION_MS = 1500
PAUSE_SECONDS = 30
TRIALS = 10
DATA_DIR = "Result"

# -----------------------------------
# Load and filter words
# -----------------------------------
def load_four_letter_words(filename):
    with open(filename, "r", encoding="utf-8") as f:
        words = [w.strip() for w in f.readlines()]
    return [w for w in words if len(w) == 4]

# -----------------------------------
# Show one word at a time with timer
# -----------------------------------
def show_words_timed(words, duration_ms=PRESENTATION_MS):
    index = 0

    def show_next_word():
        nonlocal index
        if index < len(words):
            label.config(text=words[index])
            index += 1
            window.after(duration_ms, show_next_word)
        else:
            window.destroy()

    window = tk.Tk()
    window.title("Free Recall – Word Presentation")
    window.configure(bg="white")
    window.lift()
    window.focus_force()

    label = tk.Label(window, text="", font=("Arial", 40), fg="black", bg="white")
    label.pack(padx=40, pady=40)

    show_next_word()
    window.mainloop()

# -----------------------------------
# Serial-position scoring
# Order-independent: each recalled word is consumed once, so repeated
# words must be recalled as often as they were presented.
# -----------------------------------
def serial_position_score(presented, recalled):
    remaining = [w.strip().lower() for w in recalled]
    score = []
    for word in presented:
        key = word.strip().lower()
        if key in remaining:
            remaining.remove(key)
            score.append(1)
        else:
            score.append(0)
    return score

# -----------------------------------
# 30-second pause (no math task)
# -----------------------------------
def pause_30_seconds():
    print(f"\nPause for {PAUSE_SECONDS} seconds. Please wait...")
    time.sleep(PAUSE_SECONDS)
    print("You may now recall the words.")

# -----------------------------------
# Run one trial
# -----------------------------------
def run_single_trial(all_words):
    presented = random.sample(all_words, LIST_LENGTH)

    # Timestamp: presentation start
    presentation_start = time.time()
    show_words_timed(presented, duration_ms=PRESENTATION_MS)
    # Timestamp: presentation end
    presentation_end = time.time()

    # Pause for 30 seconds
    pause_30_seconds()

    # Timestamp: recall start
    recall_start = time.time()

    # Now recall
    recalled_raw = input("Write all the words you remember: ")
    recalled = recalled_raw.split()

    sp_score = serial_position_score(presented, recalled)

    return presented, recalled, sp_score, presentation_start, presentation_end, recall_start

# -----------------------------------
# Full experiment: one participant × 10 trials
# -----------------------------------
def run_experiment():
    all_words = load_four_letter_words("words_3_4.txt")

    name = input("Enter participant name: ")

    # Prepare CSV file
    os.makedirs(DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(DATA_DIR, f"{CONDITION}_{name}_{timestamp}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "condition",
            "task",
            "participant",
            "trial",
            "list_length",
            "presentation_ms",
            "presented_words",
            "recalled_words",
            "serial_position_score",
            "presentation_start_time",
            "presentation_end_time",
            "recall_start_time"
        ])

        for trial in range(1, TRIALS + 1):
            print(f"\nTrial {trial} for {name}")
            (presented, recalled, sp_score,
             t_start, t_end, t_recall) = run_single_trial(all_words)

            writer.writerow([
                CONDITION,
                TASK,
                name,
                trial,
                LIST_LENGTH,
                PRESENTATION_MS,
                " ".join(presented),
                " ".join(recalled),
                " ".join(map(str, sp_score)),
                t_start,
                t_end,
                t_recall
            ])

    print(f"\nExperiment complete. Data saved to {filename}")

# Run experiment
if __name__ == "__main__":
    run_experiment()
