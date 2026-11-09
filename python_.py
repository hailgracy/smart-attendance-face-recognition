
import os
import csv
import time
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import cv2
import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# Soft / muted palette (differs from the original bright theme)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg":        "#f4f1ea",   # warm off-white
    "panel":     "#e6e2d3",   # soft sand
    "accent":    "#7fa99b",   # muted sage
    "accent2":   "#c9a9a6",   # dusty rose
    "text":      "#2f2f2f",
    "text_light":"#ffffff",
    "warn":      "#d9b48f",   # soft amber
    "danger":    "#c98b8b",   # muted coral
    "button":    "#b8c9c1",
}

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 10)

DATASET_DIR   = "TrainingImage"
LABEL_DIR     = "TrainingImageLabel"
DETAILS_DIR   = "StudentDetails"
ATTEND_DIR    = "Attendance"
CASCADE_FILE  = "haarcascade_frontalface_default.xml"
TRAINER_FILE  = os.path.join(LABEL_DIR, "Trainner.yml")
DETAILS_FILE  = os.path.join(DETAILS_DIR, "StudentDetails.csv")
PASSWORD_FILE = os.path.join(LABEL_DIR, "psd.txt")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def cascade_ok() -> bool:
    if not os.path.isfile(CASCADE_FILE):
        messagebox.showerror("Missing file",
                             f"{CASCADE_FILE} not found in project folder.")
        return False
    return True


# ---------------------------------------------------------------------------
# Application class
# ---------------------------------------------------------------------------
class AttendanceApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Attendance — Face Recognition")
        self.root.geometry("1180x700")
        self.root.resizable(True, False)
        self.root.configure(bg=PALETTE["bg"])

        self._build_styles()
        self._build_header()
        self._build_registration_panel()
        self._build_attendance_panel()
        self._refresh_registration_count()
        self._tick_clock()

    # ---------------- styling ----------------
    def _build_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Soft.Treeview",
                        background=PALETTE["panel"],
                        fieldbackground=PALETTE["panel"],
                        foreground=PALETTE["text"],
                        rowheight=26,
                        font=FONT_BODY)
        style.configure("Soft.Treeview.Heading",
                        background=PALETTE["accent"],
                        foreground=PALETTE["text_light"],
                        font=FONT_HEAD)

    # ---------------- header ----------------
    def _build_header(self):
        header = tk.Frame(self.root, bg=PALETTE["bg"])
        header.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(header, text="Face Recognition Attendance System",
                 bg=PALETTE["bg"], fg=PALETTE["text"],
                 font=FONT_TITLE).pack(side="left")

        self.clock_lbl = tk.Label(header, text="", bg=PALETTE["bg"],
                                  fg=PALETTE["accent"], font=FONT_HEAD)
        self.clock_lbl.pack(side="right", padx=(10, 0))

        now = datetime.datetime.now()
        date_txt = now.strftime("%d %B %Y")
        tk.Label(header, text=date_txt, bg=PALETTE["bg"],
                 fg=PALETTE["accent2"], font=FONT_HEAD).pack(side="right")

    def _tick_clock(self):
        self.clock_lbl.config(text=time.strftime("%H:%M:%S"))
        self.root.after(500, self._tick_clock)

    # ---------------- registration panel ----------------
    def _build_registration_panel(self):
        wrap = tk.Frame(self.root, bg=PALETTE["bg"])
        wrap.pack(fill="both", expand=True, padx=15, pady=10)

        # left panel = new registrations
        self.reg_frame = tk.Frame(wrap, bg=PALETTE["panel"],
                                  highlightbackground=PALETTE["accent"],
                                  highlightthickness=1)
        self.reg_frame.place(relx=0.02, rely=0.0, relwidth=0.46, relheight=0.95)

        tk.Label(self.reg_frame, text="New Registration",
                 bg=PALETTE["accent"], fg=PALETTE["text_light"],
                 font=FONT_HEAD).pack(fill="x", pady=(0, 12))

        tk.Label(self.reg_frame, text="Student ID", bg=PALETTE["panel"],
                 fg=PALETTE["text"], font=FONT_BODY).pack(anchor="w", padx=25, pady=(10, 2))
        self.entry_id = tk.Entry(self.reg_frame, font=FONT_BODY, relief="solid", bd=1)
        self.entry_id.pack(fill="x", padx=25)

        tk.Label(self.reg_frame, text="Full Name", bg=PALETTE["panel"],
                 fg=PALETTE["text"], font=FONT_BODY).pack(anchor="w", padx=25, pady=(12, 2))
        self.entry_name = tk.Entry(self.reg_frame, font=FONT_BODY, relief="solid", bd=1)
        self.entry_name.pack(fill="x", padx=25)

        self.reg_status = tk.Label(self.reg_frame,
                                   text="Step 1: capture images  →  Step 2: save profile",
                                   bg=PALETTE["panel"], fg=PALETTE["accent"],
                                   font=FONT_SMALL)
        self.reg_status.pack(pady=15)

        self.count_lbl = tk.Label(self.reg_frame, text="",
                                  bg=PALETTE["panel"], fg=PALETTE["text"],
                                  font=FONT_BODY)
        self.count_lbl.pack(pady=(0, 15))

        btn_row = tk.Frame(self.reg_frame, bg=PALETTE["panel"])
        btn_row.pack(fill="x", padx=25, pady=5)

        self._soft_button(btn_row, "Take Images", self.take_images,
                          PALETTE["button"]).pack(fill="x", pady=4)
        self._soft_button(btn_row, "Save Profile", self.save_profile,
                          PALETTE["accent"]).pack(fill="x", pady=4)

    # ---------------- attendance panel ----------------
    def _build_attendance_panel(self):
        self.att_frame = tk.Frame(self.root, bg=PALETTE["panel"],
                                  highlightbackground=PALETTE["accent2"],
                                  highlightthickness=1)
        self.att_frame.place(relx=0.52, rely=0.0, relwidth=0.46, relheight=0.95)

        tk.Label(self.att_frame, text="Today's Attendance",
                 bg=PALETTE["accent2"], fg=PALETTE["text_light"],
                 font=FONT_HEAD).pack(fill="x", pady=(0, 10))

        table_wrap = tk.Frame(self.att_frame, bg=PALETTE["panel"])
        table_wrap.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.tree = ttk.Treeview(table_wrap, height=14,
                                 columns=("name", "date", "time"),
                                 style="Soft.Treeview")
        self.tree.column("#0", width=90, anchor="center")
        self.tree.column("name", width=160)
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("time", width=120, anchor="center")
        self.tree.heading("#0", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        actions = tk.Frame(self.att_frame, bg=PALETTE["panel"])
        actions.pack(fill="x", padx=15, pady=10)

        self._soft_button(actions, "Take Attendance", self.track_images,
                          PALETTE["accent"]).pack(fill="x", pady=4)
        self._soft_button(actions, "Quit", self.root.destroy,
                          PALETTE["danger"]).pack(fill="x", pady=4)

    # ---------------- button factory ----------------
    def _soft_button(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=PALETTE["text"],
                         activebackground=PALETTE["bg"],
                         activeforeground=PALETTE["text"],
                         relief="flat", bd=0,
                         font=FONT_HEAD, pady=8, cursor="hand2")

    # ---------------- counts ----------------
    def _refresh_registration_count(self):
        if os.path.isfile(DETAILS_FILE):
            with open(DETAILS_FILE, newline="") as f:
                rows = list(csv.reader(f))
            count = max(len(rows) - 1, 0)
        else:
            count = 0
        self.count_lbl.config(text=f"Registered students: {count}")

    # ---------------- take images ----------------
    def take_images(self):
        if not cascade_ok():
            return

        ensure_dir(DATASET_DIR)
        ensure_dir(DETAILS_DIR)

        student_id = self.entry_id.get().strip()
        name = self.entry_name.get().strip()

        if not student_id.isdigit():
            messagebox.showwarning("Invalid ID", "Student ID must be numeric.")
            return
        if not name.replace(" ", "").isalpha():
            messagebox.showwarning("Invalid Name", "Name must contain letters only.")
            return

        # determine serial number
        serial = 1
        if os.path.isfile(DETAILS_FILE):
            with open(DETAILS_FILE, newline="") as f:
                serial = sum(1 for _ in csv.reader(f))

        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier(CASCADE_FILE)
        samples = 0

        while samples <= 60:
            ok, frame = cam.read()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                samples += 1
                fname = f"{name}.{serial}.{student_id}.{samples}.jpg"
                cv2.imwrite(os.path.join(DATASET_DIR, fname),
                            gray[y:y + h, x:x + w])
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (127, 169, 155), 2)
            cv2.imshow("Capturing — press Q to stop", frame)
            if cv2.waitKey(80) & 0xFF == ord("q"):
                break

        cam.release()
        cv2.destroyAllWindows()

        if samples == 0:
            messagebox.showwarning("No face detected",
                                   "Try again with better lighting.")
            return

        # append student record
        write_header = not os.path.isfile(DETAILS_FILE)
        with open(DETAILS_FILE, "a", newline="") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["SERIAL NO.", "", "ID", "", "NAME"])
            w.writerow([serial, "", student_id, "", name])

        self.reg_status.config(
            text=f"Captured {samples} images for {name} (ID {student_id})")
        self._refresh_registration_count()

    # ---------------- save profile ----------------
    def save_profile(self):
        if not cascade_ok():
            return
        ensure_dir(LABEL_DIR)

        if not self._check_password():
            return

        faces, labels = self._load_faces()
        if not faces:
            messagebox.showwarning("No data",
                                   "Register at least one student first.")
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        recognizer.save(TRAINER_FILE)
        self.reg_status.config(text="Profile trained and saved successfully.")

    # ---------------- password ----------------
    def _check_password(self):
        if not os.path.isfile(PASSWORD_FILE):
            new = simpledialog.askstring("Set password",
                                         "No password set. Create one:",
                                         show="*")
            if not new:
                messagebox.showwarning("Cancelled", "Password not set.")
                return False
            with open(PASSWORD_FILE, "w") as f:
                f.write(new)
            messagebox.showinfo("Password saved", "New password registered.")
            return True

        with open(PASSWORD_FILE) as f:
            saved = f.read().strip()
        entered = simpledialog.askstring("Password", "Enter password:", show="*")
        if entered is None:
            return False
        if entered != saved:
            messagebox.showerror("Wrong password", "Access denied.")
            return False
        return True

    # ---------------- training data loader ----------------
    def _load_faces(self):
        faces, labels = [], []
        if not os.path.isdir(DATASET_DIR):
            return faces, labels
        for fname in os.listdir(DATASET_DIR):
            if not fname.lower().endswith(".jpg"):
                continue
            path = os.path.join(DATASET_DIR, fname)
            pil = Image.open(path).convert("L")
            arr = np.array(pil, "uint8")
            try:
                label = int(fname.split(".")[1])
            except (IndexError, ValueError):
                continue
            faces.append(arr)
            labels.append(label)
        return faces, labels

    # ---------------- attendance ----------------
    def track_images(self):
        if not cascade_ok():
            return
        if not os.path.isfile(TRAINER_FILE):
            messagebox.showerror("No model",
                                 "Please save a profile first.")
            return
        if not os.path.isfile(DETAILS_FILE):
            messagebox.showerror("No details",
                                 "Student details file is missing.")
            return

        # clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(TRAINER_FILE)
        detector = cv2.CascadeClassifier(CASCADE_FILE)

        # build id/name lookup from details
        lookup = {}
        with open(DETAILS_FILE, newline="") as f:
            r = csv.reader(f)
            next(r, None)
            for row in r:
                if len(row) >= 5 and row[0].strip():
                    try:
                        lookup[int(row[0])] = (row[2], row[4])
                    except ValueError:
                        continue

        cam = cv2.VideoCapture(0)
        marked = set()
        deadline = time.time() + 30  # 30-second scan window

        while time.time() < deadline:
            ok, frame = cam.read()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
                if conf < 55 and serial in lookup:
                    sid, sname = lookup[serial]
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (127, 169, 155), 2)
                    cv2.putText(frame, sname, (x, y + h + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (127, 169, 155), 2)
                    if serial not in marked:
                        marked.add(serial)
                        self._log_attendance(sid, sname)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (201, 139, 139), 2)
                    cv2.putText(frame, "Unknown", (x, y + h + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (201, 139, 139), 2)
            cv2.imshow("Scanning — press Q to stop", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cam.release()
        cv2.destroyAllWindows()
        self._load_attendance_table()

    def _log_attendance(self, sid, sname):
        ensure_dir(ATTEND_DIR)
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        path = os.path.join(ATTEND_DIR, f"Attendance_{today}.csv")
        header = ["ID", "Name", "Date", "Time"]
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        new_file = not os.path.isfile(path)
        with open(path, "a", newline="") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(header)
            w.writerow([sid, sname, today, stamp])

    def _load_attendance_table(self):
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        path = os.path.join(ATTEND_DIR, f"Attendance_{today}.csv")
        if not os.path.isfile(path):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        with open(path, newline="") as f:
            r = csv.reader(f)
            next(r, None)
            for row in r:
                if len(row) >= 4:
                    self.tree.insert("", "end",
                                     text=row[0],
                                     values=(row[1], row[2], row[3]))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
