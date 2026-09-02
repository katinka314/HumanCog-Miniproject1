import re

input_file = "eng_sentences_org.tsv"
output_file = "clean_sentences.txt"

# Load your simplified English dictionary.
# One English word per line, lowercase.
dictionary_file = "english_dictionary_simple.txt"

with open(dictionary_file, "r", encoding="utf-8") as f:
    dictionary = {
        line.strip().lower()
        for line in f
        if line.strip() and not line.startswith("#")
    }


def contains_number(sentence):
    return bool(re.search(r"\d", sentence))


def contains_all_caps_word(sentence):
    words = re.findall(r"\b[A-Za-z]+\b", sentence)

    for word in words:
        # Ignore single-letter capitals such as "I"
        if len(word) > 1 and word.isupper():
            return True

    return False


def contains_long_word(sentence):
    words = re.findall(r"[A-Za-z]+", sentence)

    return any(len(word) > 6 for word in words)


def contains_unknown_word(sentence):
    words = re.findall(r"[A-Za-z]+", sentence.lower())

    for word in words:
        if word not in dictionary:
            return True

    return False


with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_file, "w", encoding="utf-8") as outfile:

    for line in infile:

        # Expected format:
        # 1276    eng    Let's try something.
        parts = line.strip().split("\t", 2)

        if len(parts) < 3:
            continue
        
        sentence = parts[2].strip()


        # Remove sentences containing numbers
        if contains_number(sentence):
            continue

        # Remove sentences containing ALL-CAPS words such as API, PIN, NASA
        if contains_all_caps_word(sentence):
            continue

        # Remove sentences containing words longer than 8 characters
        if contains_long_word(sentence):
            continue

        # Remove special characters.
        # Apostrophes are retained for contractions.
        cleaned = re.sub(
            r"[^A-Za-zÀ-ÿ\s']",
            "",
            sentence
        )

        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Exactly 15 words
        words = cleaned.split()

        if len(words) != 15:
            continue
        print("here")
        # Remove sentences containing words not in dictionary
        if contains_unknown_word(cleaned):
            continue
        print("also here")
        outfile.write(cleaned + "\n")