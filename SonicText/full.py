import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import librosa
import noisereduce as nr
import soundfile as sf
from vosk import Model, KaldiRecognizer
import numpy as np
import threading
import json
import sys
import os


class LoadingScreen:
    def __init__(self, parent):
        self.parent = parent
        self.loading_frame = None
        self.loading_label = None

    def show(self):
        self.loading_frame = tk.Frame(self.parent)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.loading_label = tk.Label(self.loading_frame, text="Processing audio, please wait...", font=font_style)
        self.loading_label.pack(pady=20)

    def hide(self):
        if self.loading_frame:
            self.loading_frame.destroy()
            self.loading_frame = None
            self.loading_label = None

def denoise_audio():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    if file_path:
        loading_screen.show()
        threading.Thread(target=process_audio, args=(file_path,)).start()

def process_audio(file_path):
    try:
        data, rate = librosa.load(file_path)
        reduced = nr.reduce_noise(y=data, sr=rate)
        denoised_file_path = file_path.replace(".mp3", "_denoised.wav")
        sf.write(denoised_file_path, reduced, rate)
        text = convert_to_text(denoised_file_path)
        loading_screen.hide()
        show_text(text)
        show_output_file(denoised_file_path)
        show_audio_length(file_path)
        show_word_count(text)
    except Exception as e:
        loading_screen.hide()
        error_message = f"An error occurred: {str(e)}"
        show_error_message(error_message)



def convert_to_text(audio_file_path):
    model = Model(r"C:\Users\KIIT\Desktop\SonicText\vosk-model-en-in-0.5\vosk-model-en-in-0.5")
    recognizer = KaldiRecognizer(model, 16000)

    audio_data, sample_rate = sf.read(audio_file_path)
    audio_data = (audio_data * 32767).astype(np.int16).tobytes()

    text = ''
    chunk_size = 4096
    offset = 0

    while offset < len(audio_data):
        end = offset + chunk_size
        chunk = audio_data[offset:end]
        if recognizer.AcceptWaveform(chunk):
            result = recognizer.Result()
            result_json = json.loads(result)
            text += result_json["text"]
        offset = end

    text = text.replace('\n', ' ')
    return text

def show_text(text):
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, text)

def show_output_file(file_path):
    output_file_label.config(text=f"Output File: {file_path}")

def show_audio_length(file_path):
    duration = librosa.get_duration(filename=file_path)
    audio_length_label.config(text=f"Audio Length: {duration:.2f} seconds")

def show_word_count(text):
    word_count = len(text.split())
    word_count_label.config(text=f"Word Count: {word_count} words")

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def search_text(event=None):
    keyword = search_entry.get("1.0", tk.END).strip()
    text = result_text.get("1.0", tk.END)
    if keyword:
        if keyword.lower() in text.lower():
            result_text.tag_remove("highlight", "1.0", tk.END)
            start_pos = "1.0"
            while True:
                start_pos = result_text.search(keyword, start_pos, tk.END, nocase=True)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                result_text.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos
            result_text.tag_config("highlight", background="yellow")
        else:
            result_text.tag_remove("highlight", "1.0", tk.END)

def save_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
    if file_path:
        denoised_file_path = output_file_label.cget("text")[13:]
        if os.path.isfile(denoised_file_path):
            try:
                os.rename(denoised_file_path, file_path)
                output_file_label.config(text=f"Output File: {file_path}")
            except Exception as e:
                error_message = f"An error occurred while saving the file: {str(e)}"
                show_error_message(error_message)

def minimize_application():
    window.iconify()

def close_application():
    window.destroy()

def show_error_message(message):
    error_window = tk.Toplevel(window)
    error_window.title("Error")
    error_window.geometry("300x100")
    error_label = tk.Label(error_window, text=message, font=font_style)
    error_label.pack(pady=20)

window = tk.Tk()
window.title("Audio Denoizer and Converter")
window.attributes('-fullscreen', True)  # Open the window in full-screen mode

font_style = ("Arial", 12)

style = ttk.Style()
style.configure("Modern.TButton", font=font_style)
denoise_button = ttk.Button(window, text="Denoize Audio", command=denoise_audio, style="Modern.TButton")
denoise_button.pack(pady=10)

search_frame = tk.Frame(window)
search_frame.pack(pady=10)
search_entry = tk.Text(search_frame, height=1, width=30, font=font_style)
search_entry.pack(side=tk.LEFT, padx=5, pady=5)
search_entry.bind("<KeyRelease>", search_text)  # Bind KeyRelease event to search_text function
search_button = ttk.Button(search_frame, text="Search", command=search_text, style="Modern.TButton")
search_button.pack(side=tk.LEFT, padx=5)

result_text = tk.Text(window, height=25, width=160, font=font_style)
result_text.pack()

output_file_label = tk.Label(window, text="Output File: ", font=font_style)
output_file_label.pack(pady=10)

audio_length_label = tk.Label(window, text="Audio Length: ", font=font_style)
audio_length_label.pack(pady=5)

word_count_label = tk.Label(window, text="Word Count: ", font=font_style)
word_count_label.pack(pady=5)

save_button = ttk.Button(window, text="Save Output File", command=save_output_file, style="Modern.TButton")
save_button.pack(pady=10)

restart_button = ttk.Button(window, text="Restart Application", command=restart_program, style="Modern.TButton")
restart_button.pack(pady=10)

minimize_button = ttk.Button(window, text="Minimize Application", command=minimize_application, style="Modern.TButton")
minimize_button.pack(pady=10)

close_button = ttk.Button(window, text="Close Application", command=close_application, style="Modern.TButton")
close_button.pack(pady=10)

loading_screen = LoadingScreen(window)

window.mainloop()