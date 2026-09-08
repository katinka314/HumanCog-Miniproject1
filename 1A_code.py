import random
import csv
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
def show_words_timed(words, duration_ms=750):
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
# -----------------------------------
def serial_position_score(presented, recalled):
    presented_lower = [w.lower() for w in presented]
    score = [0] * len(presented)
    for word in recalled:
        if word.lower() in presented_lower:
            idx = presented_lower.index(word.lower())
            score[idx] = 1
    return score

# -----------------------------------
# Run one trial
# -----------------------------------
def run_single_trial(all_words):
    presented = random.sample(all_words, 15)
    show_words_timed(presented, duration_ms=750)

    recalled_raw = input("Write all the words you remember: ")
    recalled = recalled_raw.split()

    sp_score = serial_position_score(presented, recalled)

    return presented, recalled, sp_score

# -----------------------------------
# Full experiment: 4 participants × 10 trials
# -----------------------------------
def run_experiment():
    all_words = load_four_letter_words("words_3_4.txt")

    # Loop over participants
    for p in range(1):
        print(f"\n--- Participant {p} ---")
        name = input("Enter participant name: ")

        # Prepare CSV file
        with open(f"Result/1A_{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant",
                "trial",
                "presented_words",
                "recalled_words",
                "serial_position_score"
                ])
            
            # 10 trials per participant
            for trial in range(1, 11):
                print(f"\nTrial {trial} for {name}")
                presented, recalled, sp_score = run_single_trial(all_words)

                # Write to CSV
                writer.writerow([
                    name,
                    trial,
                    " ".join(presented),
                    " ".join(recalled),
                    " ".join(map(str, sp_score))
                ])

    print(f"\nExperiment complete. Data saved to Result/1A_{name}.csv")

# Run experiment
if __name__ == "__main__":
    run_experiment()
