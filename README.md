# smart-attendance-face-recognition
A Python desktop app that marks attendance automatically using OpenCV face recognition and Tkinter. No manual roll-call, no sign-in sheets — just look at the camera.
# Face Recognition Attendance System

A desktop application built with **Python 3.10**, **OpenCV**, and **Tkinter** that marks attendance automatically by recognising faces from a webcam. No manual roll-call, no paper sign-in sheets — register each student once, train the model, and the app logs their attendance to a dated CSV file every time they appear in front of the camera.

---

## ✨ Features

- 📸 **Student registration** — capture 60 face samples per student in a few seconds
- 🧠 **On-device training** — LBPH (Local Binary Pattern Histogram) face recogniser, no cloud, no internet
- 🎥 **Live attendance scanning** — recognises registered faces in real time and logs ID, name, date, time
- 🔒 **Password protection** — training is gated behind a password you set on first use
- 📊 **CSV export** — one file per day, Excel-ready, in `Attendance/Attendance_DD-MM-YYYY.csv`
- 🎨 **Soft UI** — muted palette, clean layout, live clock
- 🖥️ **Fully offline** — all data stays on your machine

---

## 🖼️ Screenshot

*(Add a screenshot of the GUI here once you have one — drag an image into the README editor on GitHub and it will auto-generate the markdown link.)*

---

## 🛠️ Tech Stack

| Layer | Library / Tool |
|---|---|
| GUI | `tkinter` + `ttk` |
| Computer vision | `opencv-contrib-python` |
| Face detector | Haar cascade (`haarcascade_frontalface_default.xml`) |
| Face recogniser | LBPH (`cv2.face.LBPHFaceRecognizer_create`) |
| Image handling | `Pillow`, `numpy` |
| Data storage | `csv` (stdlib) |
| Python version | 3.10+ |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/face-recognition-attendance-system.git
cd face-recognition-attendance-system
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the Haar cascade

The cascade file ships with OpenCV. Copy it to the project root:

```python
import cv2, os, shutil
src = os.path.join(os.path.dirname(cv2.__file__), "data",
                   "haarcascade_frontalface_default.xml")
shutil.copy(src, "haarcascade_frontalface_default.xml")
print("Copied to:", os.path.abspath("haarcascade_frontalface_default.xml"))
```

> ⚠️ The file must be **~930 KB**. A truncated file (~180 KB) will load but detect nothing. Re-download from [OpenCV's GitHub](https://github.com/opencv/opencv/blob/4.x/data/haarcascades/haarcascade_frontalface_default.xml) if in doubt.

---

## 🚀 Usage

```bash
python main.py
```

### Workflow

1. **Register** — enter a numeric Student ID and full name, click **Take Images**, look at the camera (60 samples captured automatically, ~5 seconds)
2. **Set password** — first time you click **Save Profile**, you'll be asked to create a password
3. **Train** — click **Save Profile**, enter the password, and the model trains on all captured faces (~1 second)
4. **Mark attendance** — click **Take Attendance**. The app scans for 30 seconds (or until you press `Q`) and logs every recognised face
5. **View results** — open `Attendance/Attendance_DD-MM-YYYY.csv` in Excel, Google Sheets, or any text editor

### Tips

- **Good lighting matters.** The Haar detector needs a reasonably bright, front-facing face.
- **Confidence threshold** is `55` in `track_images()`. Lower it (e.g. `45`) if real students are marked "Unknown", or raise it (e.g. `65`) if random objects are being matched.
- **When the OpenCV camera window opens**, click it once to give it focus before pressing `Q`.

---

## 📁 Project Structure

```
face-recognition-attendance-system/
├── main.py                                 # The application
├── requirements.txt                        # Python dependencies
├── haarcascade_frontalface_default.xml     # Face detector (download separately)
├── README.md
├── LICENSE
├── .gitignore
│
├── StudentDetails/                         # Created on first run
│   └── StudentDetails.csv                  # ID, Name registry
│
├── TrainingImage/                          # Captured face samples
│   └── <name>.<serial>.<id>.<n>.jpg
│
├── TrainingImageLabel/                     # Model + password
│   ├── Trainner.yml                        # Trained LBPH model
│   └── psd.txt                             # Hashed password
│
└── Attendance/                             # Daily attendance logs
    └── Attendance_DD-MM-YYYY.csv
```

---

## 📊 Attendance File Format

Each row is one detection event:

| ID | Name | Date | Time |
|---|---|---|---|
| 812622243014 | Hail Gracy A | 09-11-2026 | 16:53:20 |
| 812622243014 | Hail Gracy A | 09-11-2026 | 16:53:56 |

**Note:** if the same person is scanned twice, two rows are logged. To get a single "present" row per student per day, deduplicate by `ID + Date` in Excel:

```
=UNIQUE(A2:C100)   # Google Sheets
=INDEX/MATCH...    # Excel alternative
```

---

## 🔒 Privacy & Data

- **Everything runs locally.** No images, no attendance records, and no passwords ever leave your computer.
- The `TrainingImage/` folder contains **photos of students' faces**. Do **not** commit this folder to a public repository.
- The `Attendance/` folder contains **real names and IDs**. Do **not** commit it to a public repository.
- The `.gitignore` file provided excludes both folders by default. Only commit them if you have obtained consent and are using a **private** repository.

---

## 🐛 Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: cv2` | `pip install opencv-contrib-python` into the *same* Python you're running the app with |
| Camera window appears behind IDLE | Click it once in the taskbar, then press `Q` |
| Cascade file "not found" | Download it to the project root (see Step 4 above) |
| Cascade file loads but detects nothing | File is truncated — must be ~930 KB |
| "No Registrations" when saving profile | Take images first |
| Everyone shows as "Unknown" | Re-capture samples with better lighting; retrain; or lower `conf < 55` to `conf < 65` |
| Attendance CSV not created | Folder `Attendance/` only appears after a successful scan |
| App launched from IDLE puts files in the wrong place | Add `os.chdir(os.path.dirname(os.path.abspath(__file__)))` at the top of `main.py` |

---

## 🗺️ Roadmap

- [ ] Export to `.xlsx` with one sheet per month
- [ ] Deduplicate daily attendance (one row per student per day)
- [ ] Register multiple faces per student (different angles)
- [ ] Add a "View today's attendance" table inside the GUI
- [ ] Auto-download the cascade file on first run
- [ ] Windows `.exe` build with PyInstaller

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome. Open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

Released under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 🙏 Acknowledgements

- [OpenCV](https://opencv.org/) — face detection and recognition
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI framework
- Haar cascade originally trained by **Rainer Lienhart** and **Jochen Maydt** (2002)

---

## 📬 Contact

Hail Gracy A - hailgracy89@gmail.com

