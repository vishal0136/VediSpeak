# VediSpeak
An Indian Sign Language TTS-STT model for the deaf and mute persons

**VediSpeak** is a research-driven platform designed to bridge communication gaps for the Deaf and Hard-of-Hearing community in India. It leverages **Indian Sign Language (ISL)** gestures and provides real-time conversion to **text** and **speech** using **machine learning**, **computer vision**, and **speech technologies**.

---

## 🌟 Features

- **Real-time ISL Gesture Recognition**
- **Convert ISL gestures to Text & Speech**
- **User-friendly interface**
- **STT & TTS tools integrated**
- **Profile management & authentication**
- **Dashboard with resources & learning materials**

---

## 📂 Project Structure

VediSpeak/
│
├── app.py # Main Flask application
├── templates/ # HTML templates
│ ├── dashboard.html
│ ├── profile.html
│ ├── about.html
│ ├── resources.html
│ ├── learning.html
│ └── login.html, register.html
├── static/ # CSS, JS, images
├── requirements.txt # Python dependencies
└── README.md

---

## ⚡ Quick Setup & Deployment

### 1️⃣ Clone the repository
git clone https://github.com/vishal0136/VediSpeak.git
cd VediSpeak
### 2️⃣ Create & activate a virtual environment
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / MacOS
python3 -m venv venv
source venv/bin/activate

### 3️⃣ Install dependencies

pip install -r requirements.txt

### 4️⃣ Setup MySQL Database

Open MySQL and create a database:

CREATE DATABASE isl_app;
Create a users table:

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    email VARCHAR(50),
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Update app.py MySQL config if needed:

python code
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "your_password"
app.config["MYSQL_DB"] = "isl_app"

### 5️⃣ Run the Flask app
python app.py
Visit http://127.0.0.1:5000 in your browser.

---

## 🛠️ Tools Used
Flask → Backend web framework

Flask-MySQLdb → MySQL integration

Flask-Bcrypt → Password hashing

gTTS → Text-to-Speech conversion

SpeechRecognition → Speech-to-Text

pydub → Audio processing (mp3 ↔ wav)

HTML, CSS, TailwindCSS → Frontend design

---

### 👥 Team
Name	Role
Vishal 	Project Lead & ISL Expert
Tushar Gupta	Frontend Developer
Vishal Singh	Backend Developer
Yash Singhal	UI/UX Designer

### 📚 References
Pujar, P.B. & Goudar , S. D. (2016). Indian Sign Language Recognition Using Hidden Markov Models. International Journal of Computer Applications, 140(9), 29–33.
GitHub: HMM-based Sign Language Recognition

Agarwal A. & Agarwal R. (2016). Real-time Sign Language Recognition and Translation System for Indian Sign Language (ISL). International Journal of Advanced Research in Computer Science and Software Engineering, 6(5), 58-64.
GitHub: Indian Sign Language Recognition System

Bhargava S. & Ghosh D. (2019). Sign Language Recognition Using Deep Learning for Indian Sign Language. IEEE Access, 7, 54801–54809.
GitHub: ISL Deep Learning Model

(See resources.html for full list of references and GitHub repos.)

### 💡 Notes
Ensure Python 3.10+ is installed.

Make sure MySQL server is running locally.

All teammates can clone, install, and run using the steps above.

VediSpeak - Making ISL accessible to everyone! 🖐️💬
 
