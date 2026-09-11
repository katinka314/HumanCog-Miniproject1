import random
import csv
import time
import tkinter as tk

SENTENCES = "clean_sentences10.txt"
# -----------------------------------
# Load sentences (chunking condition)
# -----------------------------------
def load_sentences(filename):
    with open(filename, "r", encoding="utf-8") as f:
        sentences = [line.strip() for line in f.readlines() if line.strip()]
    return sentences

def sentence_to_words(sentence):
    return sentence.split()

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
    window.title("Chunking Recall – Word Presentation")
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
    # A sentence can contain the same word several times, so each recalled
    # word is used up once instead of always matching the first occurrence.
    remaining = [w.lower() for w in recalled]
    score = []
    for word in presented:
        if word.lower() in remaining:
            remaining.remove(word.lower())
            score.append(1)
        else:
            score.append(0)
    return score

# -----------------------------------
# Run one trial
# -----------------------------------
def run_single_trial(all_sentences):
    sentence = random.choice(all_sentences)
    presented = sentence_to_words(sentence)

    # Timestamp: presentation start
    presentation_start = time.time()
    show_words_timed(presented, duration_ms=1500)
    # Timestamp: presentation end
    presentation_end = time.time()

    # Timestamp: recall start (immediately, no delay/interference — matches baseline)
    recall_start = time.time()

    recalled_raw = input("Write all the words you remember: ")
    recalled = recalled_raw.split()

    sp_score = serial_position_score(presented, recalled)

    return sentence, presented, recalled, sp_score, presentation_start, presentation_end, recall_start

# -----------------------------------
# Full experiment: 4 participants × 10 trials
# -----------------------------------
def run_experiment():
    all_sentences = load_sentences(SENTENCES)

    for p in range(1):
        print(f"\n--- Participant {p} ---")
        name = input("Enter participant name: ")
        
        with open(f"Result/2C_{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "participant",
                "trial",
                "sentence",
                "presented_words",
                "recalled_words",
                "serial_recall_score",
                "presentation_start_time",
                "presentation_end_time",
                "recall_start_time"
            ])

            for trial in range(1, 11):
                print(f"\nTrial {trial} for {name}")
                (sentence, presented, recalled, sp_score,
                t_start, t_end, t_recall) = run_single_trial(all_sentences)

                writer.writerow([
                    name,
                    trial,
                    sentence,
                    " ".join(presented),
                    " ".join(recalled),
                    " ".join(map(str, sp_score)),
                    t_start,
                    t_end,
                    t_recall
                ])

    print(f"\nChunking experiment complete. Data saved to Result/2C_{name}.csv")

# Run experiment
if __name__ == "__main__":
    run_experiment()
