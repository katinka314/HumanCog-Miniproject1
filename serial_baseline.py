import random
import csv
import time
import tkinter as tk

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
def show_words_timed(words, duration_ms=1500):
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

    label = tk.Label(window, text="", font=("Arial", 40))
    label.pack(padx=40, pady=40)

    show_next_word()
    window.mainloop()

# -----------------------------------
# Serial recall scoring (position-by-position)
# -----------------------------------
def serial_recall_score(presented, recalled):
    score = []
    for i in range(len(presented)):
        if i < len(recalled) and recalled[i] == presented[i]:
            score.append(1)
        else:
            score.append(0)
    return score

# -----------------------------------
# Run one serial-recall trial
# -----------------------------------
def run_single_trial(all_words):
    presented = random.sample(all_words, 15)

    # Timestamp: presentation start
    presentation_start = time.time()
    show_words_timed(presented, duration_ms=1500)
    # Timestamp: presentation end
    presentation_end = time.time()

    # Timestamp: recall start (immediately)
    recall_start = time.time()

    # SERIAL recall: one answer per position
    print("\nEnter the 7 words in the correct order:")
    recalled = []
    for i in range(7):
        ans = input(f"Word {i+1}: ").strip()
        recalled.append(ans)

    sp_score = serial_recall_score(presented, recalled)

    return presented, recalled, sp_score, presentation_start, presentation_end, recall_start

# -----------------------------------
# Full experiment: 4 participants × 10 trials
# -----------------------------------
def run_experiment():
    all_words = load_four_letter_words("words_3_4.txt")

    # Loop over participants
    for p in range(1):
        print(f"\n--- Participant {p} ---")
        name = input("Enter participant name: ")

        with open(f"Result/serial_baseline_{name}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "participant",
                    "trial",
                    "presented_words",
                    "recalled_words",
                    "serial_recall_score",
                    "presentation_start_time",
                    "presentation_end_time",
                    "recall_start_time"
        ])

        for trial in range(1, 11):
            print(f"\nTrial {trial} for {name}")
            (presented, recalled, sp_score,
                t_start, t_end, t_recall) = run_single_trial(all_words)

            writer.writerow([
                name,
                trial,
                " ".join(presented),
                " ".join(recalled),
                " ".join(map(str, sp_score)),
                t_start,
                t_end,
                t_recall
            ])

    print("\nSerial recall experiment complete. Data saved to serial_recall_experiment.csv")

# Run experiment
if __name__ == "__main__":
    run_experiment()
