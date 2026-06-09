# Dental Image Classification & Diagnosis Web Application

A Deep Learning-based web application designed to classify dental images and detect various dental issues. The application is built using **Flask** for the backend and utilizes a trained **InceptionV3** model (`model_inception.h5`) to perform image classification.

## 🦷 Supported Dental Conditions
The model classifies dental images into five distinct categories:
1. **Calculus (Tartar & Plaque)** - Detects hardened plaque build-up.
2. **Caries (Cavities)** - Identifies tooth decay and cavities.
3. **Hypodontia (Missing Teeth)** - Identifies missing teeth or developmental anomalies.
4. **Mouth Ulcer** - Detects ulcers or sores in the oral cavity.
5. **Tooth Discoloration** - Identifies stains and color changes on teeth.

---

## 🚀 Key Features
* **User Authentication**: Secure user registration and login system with SQLite database storage.
* **Onboarding Questionnaire**: Collects user dental habits (brushing frequency, issues, etc.) for personalized tracking.
* **Deep Learning Analysis**: Upload a dental image and get instantaneous predictions with confidence scores.
* **Interactive Treatment Plans**: Generates customized steps, descriptions, and advice based on the detected condition.
* **Doctor Dashboard**: Dedicated interface for dental professionals to review patient scan histories, user logins, and contact queries.
* **Deployment Ready**: Optimized configuration (`vercel.json` and temporary folder handling) for cloud deployment on platforms like Vercel.

---

## 🛠️ Technology Stack
* **Backend**: Python, Flask
* **Machine Learning**: TensorFlow, Keras (InceptionV3 Model)
* **Database**: SQLite3
* **Frontend**: HTML5, CSS3, Vanilla JS
* **Deployment**: Vercel/Gunicorn

---

## ⚙️ How to Setup and Run Locally

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Jajimoggalapraveenkumar/dental-image-classification.git
cd dental-image-classification
```

### 3. Install Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Database Initialization
Before running the app, initialize the database by running:
```bash
python init_db.py
```

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```
Or use the provided batch scripts:
* Double-click on `run_app.bat` or `Run_Dental_App.bat` to launch the application.

Once running, open your web browser and navigate to:
👉 `http://127.0.0.1:5000`

---

## 📁 Project Directory Structure
```text
├── Tooth dataset/          # Dataset folders for training images
│   ├── Calculus/
│   ├── caries/
│   ├── hypodontia/
│   ├── Mouth Ulcer/
│   └── Tooth Discoloration/
├── static/                 # CSS, JavaScript, and uploaded images
│   ├── css/
│   └── uploads/
├── templates/              # HTML frontend pages
├── app.py                  # Main Flask application
├── init_db.py              # Script to initialize SQLite database
├── train.py                # Deep learning training script
├── requirements.txt        # Project dependencies
├── vercel.json             # Vercel deployment configuration
└── README.md               # Project documentation
```

---

## 🔒 Default Admin & Doctor Credentials
For evaluation and dashboard access:
* **Admin Dashboard**: `Username: admin` | `Password: 123`
* **Doctor Dashboard**: `Username: doctor` | `Password: doctor123`
