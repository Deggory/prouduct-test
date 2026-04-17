import tkinter as tk
from detector import detect_signals
from dbc_generator import generate_dbc

class App:
    def __init__(self, panda):
        self.panda = panda

        self.root = tk.Tk()
        self.root.title("CAN AI Tool")

        tk.Button(self.root, text="Start Capture", command=self.start).pack()
        tk.Button(self.root, text="Stop & Analyze", command=self.analyze).pack()

        self.text = tk.Text(self.root, height=30, width=100)
        self.text.pack()

    def start(self):
        self.panda.clear_log()
        self.panda.start()
        self.text.insert(tk.END, "🚗 Capturing...\n")

    def analyze(self):
        self.panda.stop()
        log = self.panda.get_log()

        detected = detect_signals(log)

        for d in detected:
            self.text.insert(tk.END, f"{d['label']} ({d['confidence']}%)\n")

        dbc = generate_dbc(detected)

        self.text.insert(tk.END, "\n=== GENERATED DBC ===\n")
        self.text.insert(tk.END, dbc)

    def run(self):
        self.root.mainloop()
