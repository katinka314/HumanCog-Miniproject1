import random
import csv
import os
import time
import tkinter as tk
from datetime import datetime

# -----------------------------------
# Experiment settings
# -----------------------------------
CONDITION = "2D"
TASK = "serial_recall"
LIST_LENGTH = 7
PRESENTATION_MS = 1500
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
    window.title("Serial Recall – Word Presentation")
    window.geometry("800x400")
    window.configure(bg="white")
    window.lift()
    window.attributes("-topmost", True)

    label = tk.Label(window, text="", font=("Arial", 40), fg="black", bg="white")
    label.pack(expand=True, padx=40, pady=40)

    window.after(300, show_next_word)
    window.mainloop()

# -----------------------------------
# Serial recall scoring (position-by-position)
# -----------------------------------
def serial_recall_score(presented, recalled):
    score = []
    for i in range(len(presented)):
        if i < len(recalled) and recalled[i].strip().lower() == presented[i].strip().lower():
            score.append(1)
        else:
            score.append(0)
    return score

# -----------------------------------
# Run one serial-recall trial
# -----------------------------------
def run_single_trial(all_words):
    presented = random.sample(all_words, LIST_LENGTH)

    # Timestamp: presentation start
    presentation_start = time.time()
    show_words_timed(presented, duration_ms=PRESENTATION_MS)
    # Timestamp: presentation end
    presentation_end = time.time()

    # Timestamp: recall start (immediately)
    recall_start = time.time()

    # SERIAL recall: one answer per position, blanks allowed
    print(f"\nEnter the {len(presented)} words in the correct order:")
    recalled = []
    for i in range(len(presented)):
        ans = input(f"Word {i+1}: ").strip()
        recalled.append(ans)

    sp_score = serial_recall_score(presented, recalled)

    return presented, recalled, sp_score, presentation_start, presentation_end, recall_start

# -----------------------------------
# Full experiment: one participant × 10 trials
# -----------------------------------
def run_experiment():
    all_words = load_four_letter_words("words_3_4.txt")

    name = input("Enter participant name: ")
    print("Say 'dubidubi' out loud continuously during this experiment.")

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
            "score",
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
                "|".join(presented),
                "|".join(recalled),
                "|".join(map(str, sp_score)),
                t_start,
                t_end,
                t_recall
            ])

    print(f"\nSerial recall experiment complete. Data saved to {filename}")

# Run experiment
if __name__ == "__main__":
    run_experiment()
