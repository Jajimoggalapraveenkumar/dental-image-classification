# Dental Image Classification Web Application

This is a web-based project developed to classify dental images and identify common dental issues using deep learning. The application is built with Python and Flask for the backend, and it uses a trained InceptionV3 model (model_inception.h5) for image classification.

## Dental Conditions Detected by the App
The model is trained to classify images into one of these 5 classes:
1. Calculus (Plaque build-up)
2. Caries (Tooth cavities)
3. Hypodontia (Missing teeth)
4. Mouth Ulcer (Sores)
5. Tooth Discoloration (Stains on teeth)

## Features Included
* User Registration & Login: Users can sign up and log in. User details are stored in a local SQLite database.
* User Questionnaire: A questionnaire where users answer questions about their daily oral hygiene habits (like brushing frequency, current symptoms, etc.).
* Image Upload and Prediction: Users can upload a photo of their teeth. The deep learning model analyzes it and displays the classified condition.
* Treatment Plans: Shows a basic step-by-step treatment recommendation based on the detected condition.
* Doctor Dashboard: A dedicated page for doctors to log in and view the user scan history, login history, and user contact messages.

## Technologies Used
* Frontend: HTML5, CSS
* Backend: Python, Flask
* Database: SQLite3
* Deep Learning: TensorFlow, Keras (InceptionV3 model)
* Deployment: Vercel

## How to Set Up and Run Locally

### Prerequisites
You need Python installed on your computer.

### Steps:
1. Clone or download this project folder.
2. Open your terminal in the project directory.
3. Install the required python libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the server:
   ```bash
   python app.py
   ```
   *Note: You can also start the application by running the `run_app.bat` or `Run_Dental_App.bat` batch files.*
6. Open your web browser and go to: `http://127.0.0.1:5000`

## Default Access Credentials
To test the Doctor dashboard or Admin view:
* Admin:
  * Username: admin
  * Password: 123
* Doctor:
  * Username: doctor
  * Password: doctor123
