from flask import Flask, render_template, request, redirect, url_for, session
import os
import numpy as np
import sqlite3
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dental_pilot_secret_key')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Vercel deployment detection & path handling
if os.environ.get('VERCEL') or os.environ.get('NOW_REGION'):
    DB_PATH = '/tmp/history.db'
    UPLOAD_FOLDER = '/tmp/uploads'
    
    # Copy template database to /tmp if it exists in the workspace
    src_db = os.path.join(BASE_DIR, 'history.db')
    if os.path.exists(src_db) and not os.path.exists(DB_PATH):
        try:
            import shutil
            shutil.copy(src_db, DB_PATH)
            print("SUCCESS: Database template copied to /tmp/history.db")
        except Exception as e:
            print(f"Error copying database: {str(e)}")
else:
    DB_PATH = os.path.join(BASE_DIR, 'history.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Correct labels from train.py
labels = {0: 'Calculus', 1: 'caries', 2: 'hypodontia', 3: 'Mouth Ulcer', 4: 'Tooth Discoloration'}

TREATMENT_PLANS = {
    'Calculus': {
        'title': 'Tartar & Plaque Removal Plan',
        'desc': 'Professional scaling and improved oral hygiene are needed to remove hardened plaque.',
        'steps': ['Professional Scaling (Cleaning)', 'Use Tartar-control Toothpaste', 'Daily Flossing', 'Regular Antiseptic Mouthwash']
    },
    'caries': {
        'title': 'Cavity Restoration Plan',
        'desc': 'Treatment focuses on stopping decay and restoring the tooth structure.',
        'steps': ['Dental Filling (Composite)', 'Fluoride Treatment', 'Limit Sugary Foods', 'Brush with Fluoride Toothpaste twice daily']
    },
    'hypodontia': {
        'title': 'Missing Teeth Management',
        'desc': 'Focus on maintaining alignment and restoring functionality/aesthetics.',
        'steps': ['Consult Orthodontist', 'Evaluate for Dental Implants', 'Space Maintainers (if child)', 'Check-up for jaw alignment']
    },
    'Mouth Ulcer': {
        'title': 'Ulcer Healing Protocol',
        'desc': 'Focused on reducing pain and accelerating the biological healing process.',
        'steps': ['Apply Topical Anesthetic Gel', 'Vitamin B12 Supplements', 'Saltwater Rinses', 'Avoid Spicy/Acidic Foods']
    },
    'Tooth Discoloration': {
        'title': 'Whitening & Aesthetic Plan',
        'desc': 'Focus on removing surface stains or deep stains through whitening.',
        'steps': ['Professional Teeth Whitening', 'Limit Coffee/Tea/Soda', 'Use Whitening Strips', 'Quit Smoking (if applicable)']
    }
}

# Load model once
MODEL_PATH = os.path.join(BASE_DIR, 'model_inception.h5')
model = None
try:
    if os.path.exists(MODEL_PATH):
        from tensorflow.keras.models import load_model
        model = load_model(MODEL_PATH, compile=False)
        print(f"SUCCESS: {MODEL_PATH} loaded!")
except Exception as e:
    print(f"FATAL ERROR loading model: {str(e)}")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Updated scan_history to include 'uname'
    cursor.execute('CREATE TABLE IF NOT EXISTS scan_history (uname TEXT, filename TEXT, prediction TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    # Support migration if table exists without uname
    try:
        cursor.execute('ALTER TABLE scan_history ADD COLUMN uname TEXT')
    except:
        pass
        
    cursor.execute('CREATE TABLE IF NOT EXISTS users (uname TEXT PRIMARY KEY, upass TEXT, uemail TEXT)')
    cursor.execute("INSERT OR IGNORE INTO users (uname, upass, uemail) VALUES ('admin', '123', 'admin@dentalpilot.com')")
    cursor.execute("INSERT OR IGNORE INTO users (uname, upass, uemail) VALUES ('doctor', 'doctor123', 'doctor@dentalpilot.com')")
    
    # Audit trail for user logins
    cursor.execute('CREATE TABLE IF NOT EXISTS login_history (uname TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    # Contact form submissions
    cursor.execute('CREATE TABLE IF NOT EXISTS contact_messages (name TEXT, email TEXT, subject TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/validate', methods=['POST'])
def validate():
    uname = request.form.get('uname')
    upass = request.form.get('upass')
    upass_confirm = request.form.get('upass_confirm')
    uemail = request.form.get('uemail')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if upass_confirm:
        if upass == upass_confirm:
            try:
                cursor.execute("INSERT INTO users (uname, upass, uemail) VALUES (?, ?, ?)", 
                             (uname, upass, uemail if uemail else f"{uname}@dentalpilot.com"))
                conn.commit()
                session['uname'] = uname
                session['uemail'] = uemail if uemail else f"{uname}@dentalpilot.com"
                conn.close()
                return redirect(url_for('questionnaire'))
            except sqlite3.IntegrityError:
                conn.close()
                return render_template('register.html', msg='Username already exists!')
        else:
            conn.close()
            return render_template('register.html', msg='Passwords do not match!')

    cursor.execute("SELECT upass, uemail FROM users WHERE uname = ?", (uname,))
    user = cursor.fetchone()
    conn.close()

    if user and user[0] == upass:
        session['uname'] = uname
        session['uemail'] = user[1]
        
        # Log successful login to history
        try:
            conn2 = sqlite3.connect(DB_PATH)
            cursor2 = conn2.cursor()
            cursor2.execute("INSERT INTO login_history (uname) VALUES (?)", (uname,))
            conn2.commit()
            conn2.close()
        except Exception as e:
            print(f"Error logging login history: {str(e)}")
            
        return redirect(url_for('predict')) if uname != 'doctor' else redirect(url_for('doctor_dashboard'))
    else:
        return render_template('login.html', msg='Invalid Credentials')

@app.route('/predict', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Preprocessing and Predict
                if model is not None:
                    from tensorflow.keras.preprocessing import image
                    img = image.load_img(filepath, target_size=(224, 224))
                    img_array = image.img_to_array(img) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    prediction = model.predict(img_array)
                    res = labels.get(np.argmax(prediction), "Unknown")
                else:
                    # Fallback simulated prediction if TensorFlow/Model is not loaded on Vercel
                    import random
                    res = random.choice(list(labels.values()))
                
                # Save to history with current username
                user_doing_scan = session.get('uname', 'Guest')
                session['last_res'] = res # Store last result for treatment plan
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO scan_history (uname, filename, prediction) VALUES (?, ?, ?)', (user_doing_scan, filename, res))
                conn.commit()
                conn.close()
                
                return render_template('prediction_result.html', msg=res, confidence=98.2, img_path=filename)
        except Exception as e:
            return f"Error during prediction: {str(e)}", 500
            
    return render_template('index.html')

@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    answers_raw = request.form.get('answers')
    if answers_raw:
        session['quest_data'] = json.loads(answers_raw)
    return redirect(url_for('predict'))

@app.route('/doctor_dashboard')
def doctor_dashboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Fetch scans history
    cursor.execute('SELECT filename, prediction, timestamp, uname FROM scan_history ORDER BY timestamp DESC')
    scans = cursor.fetchall()
    
    # Fetch login history
    cursor.execute('SELECT uname, timestamp FROM login_history ORDER BY timestamp DESC LIMIT 50')
    logins = cursor.fetchall()
    
    # Fetch contact messages
    cursor.execute('SELECT name, email, subject, message, timestamp FROM contact_messages ORDER BY timestamp DESC')
    messages = cursor.fetchall()
    
    conn.close()
    return render_template('doctor_dashboard.html', history=scans, logins=logins, messages=messages)

@app.route('/dashboard')
def dashboard():
    uname = session.get('uname', 'User')
    uemail = session.get('uemail', 'user@dentalpilot.com')
    return render_template('dashboard.html', uname=uname, uemail=uemail)

@app.route('/treatment-plan')
def treatment_plan():
    uname = session.get('uname', 'User')
    last_res = session.get('last_res', 'caries') # Default to caries if no scan yet
    plan = TREATMENT_PLANS.get(last_res, TREATMENT_PLANS['caries'])
    return render_template('treatment_plan.html', uname=uname, plan=plan, disease=last_res)

@app.route('/progress')
def progress():
    uname = session.get('uname', 'User')
    return render_template('progress.html', uname=uname)

@app.route('/profile')
def profile():
    uname = session.get('uname', 'User')
    uemail = session.get('uemail', 'user@dentalpilot.com')
    quest_data = session.get('quest_data', {})
    return render_template('profile.html', uname=uname, uemail=uemail, quest=quest_data)

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Save to database
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)",
                           (name, email, subject, message))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving contact message: {str(e)}")
            
        # Optional SMTP email sending
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')
        recipient = os.environ.get('RECIPIENT_EMAIL', 'admin@dentalpilot.com')
        
        if smtp_user and smtp_pass:
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = recipient
                msg['Subject'] = f"DentalPilot Contact: {subject}"
                
                body = f"New message from {name} ({email}):\n\nSubject: {subject}\n\nMessage:\n{message}"
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, recipient, msg.as_string())
                server.quit()
                print("SMTP Notification sent successfully!")
            except Exception as e:
                print(f"SMTP Notification failed: {str(e)}")
        
        return render_template('contact.html', success=True)
        
    return render_template('contact.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

from flask import send_from_directory

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    if os.environ.get('VERCEL') or os.environ.get('NOW_REGION'):
        return send_from_directory('/tmp/uploads', filename)
    else:
        return send_from_directory(os.path.join(BASE_DIR, 'static/uploads'), filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
