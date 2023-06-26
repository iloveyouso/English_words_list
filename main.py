import csv
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import os.path
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

ans_check_time = 2000  # ms
num_reviewed_words = 0
wraplen = 1000


def on_key_press(event):
    # Mapping of number keys to index of option_buttons
    key_to_index = {'1': 0, '2': 1, '3': 2, '4': 3}
    # If the key pressed is one of the number keys, emulate button click
    if event.char in key_to_index:
        index = key_to_index[event.char]
        check_answer(option_buttons[index].cget("text"))


# Function to load words from CSV
def load_words_from_csv(file_name):
    if os.path.isfile(file_name):
        with open(file_name, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    else:
        print(f"CSV file '{file_name}' not found.")
        return []


# Function to play the pronunciation of the word
def play_pronunciation(word):
    tts = gTTS(word, lang='en-gb')
    audio_file = 'pronunciation.mp3'
    tts.save(audio_file)
    audio = AudioSegment.from_mp3(audio_file)
    play(audio)
    os.remove(audio_file)


# Function to load new word
def load_new_word():
    global current_word, num_words_practiced, max_words, wrong_words, wraplen

    if num_words_practiced < max_words:
        current_word = random.choice(words)
        options = [current_word["Meaning"]] + random.sample(
            [w["Meaning"] for w in words if w != current_word], 3
        )
        random.shuffle(options)

        # Update GUI
        word_label.config(text=current_word["Word"])
        result_label.config(text="")
        for i, button in enumerate(option_buttons):
            button.config(text=options[i], state=tk.NORMAL, wraplength=wraplen)

        # Play pronunciation
        play_pronunciation(current_word["Word"])
    else:
        # End of practice session
        review_button.pack(side=tk.LEFT)
        start_button.pack(side=tk.LEFT)


# Function to load a word for review
def load_review_word():
    global current_review_word, num_reviewed_words, wraplen

    if num_reviewed_words < len(wrong_words):
        current_review_word = wrong_words[num_reviewed_words]
        options = [current_review_word["Meaning"]] + random.sample(
            [w["Meaning"] for w in words if w != current_review_word], 3
        )
        random.shuffle(options)

        # Update GUI
        word_label.config(text=current_review_word["Word"])
        result_label.config(text="")
        for i, button in enumerate(option_buttons):
            button.config(text=options[i], state=tk.NORMAL, wraplength=wraplen)

        num_reviewed_words += 1
    else:
        # End of review session
        review_button.pack(side=tk.LEFT)
        start_button.pack(side=tk.LEFT)


# Function to check the answer
def check_answer(option):
    global num_words_practiced

    # Disable buttons while showing the result
    for button in option_buttons:
        button.config(state=tk.DISABLED)

    if option == current_word["Meaning"]:
        result_label.config(text="O")
    else:
        result_label.config(text=f"X {current_word['Meaning']}")
        wrong_words.append(current_word)

    # Load new word after 2 seconds
    num_words_practiced += 1
    root.after(ans_check_time, load_new_word)


def check_review_answer(option):
    global num_reviewed_words

    # Disable buttons while showing the result
    for button in option_buttons:
        button.config(state=tk.DISABLED)

    if option == current_review_word["Meaning"]:
        result_label.config(text="O")
    else:
        result_label.config(text=f"X {current_review_word['Meaning']}")

    # Load new review word after 2 seconds
    root.after(ans_check_time, load_review_word)


# Function to start practice session
def start_practice():
    global max_words, word_label, result_label, option_buttons, review_button, start_button

    max_words = simpledialog.askinteger(
        "Number of Words", "Enter the number of words you want to practice:"
    )

    if max_words:
        # Unpack the review and start buttons
        review_button.pack_forget()
        start_button.pack_forget()

        # Reset practice session
        global current_word, num_words_practiced, wrong_words
        current_word = None
        num_words_practiced = 0
        wrong_words = []

        # Load the first word
        load_new_word()


# Function to start review session
def start_review():
    global num_reviewed_words, current_review_word

    # Unpack the review and start buttons
    review_button.pack_forget()
    start_button.pack_forget()

    # Hide option buttons
    for button in option_buttons:
        button.pack_forget()

    # Reset review session
    current_review_word = None
    num_reviewed_words = 0

    # Load the first review word
    load_review_word()


# Load words from the CSV file
words = load_words_from_csv("dist/word_data.csv")

# Create main window
root = tk.Tk()
root.title("Flashcard App")
root.configure(bg="white")
root.geometry("1000x700")
root.resizable(False, False)

# Bind key press events to the on_key_press function
root.bind("<KeyPress>", on_key_press)

# Create GUI widgets
word_label = tk.Label(root, text="", font=("Times New Roman", 30), bg="white")
word_label.pack(pady=40)

result_label = tk.Label(root, text="", font=("Times New Roman", 24), bg="white")
result_label.pack(pady=10)

option_buttons = []
for i in range(4):
    button = tk.Button(
        root,
        text="",
        font=("Times New Roman", 18),
        bg="white",
        command=lambda i=i: check_answer(option_buttons[i].cget("text")),
    )
    button.pack(pady=10)
    option_buttons.append(button)

review_button = tk.Button(
    root,
    text="Review",
    font=("Times New Roman", 18),
    bg="white",
    command=start_review,
)
start_button = tk.Button(
    root,
    text="Start New Session",
    font=("Times New Roman", 18),
    bg="white",
    command=start_practice,
)

# Start practice
start_practice()

# Start the GUI event loop
root.mainloop()
