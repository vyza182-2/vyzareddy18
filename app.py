from flask import Flask, render_template, redirect, request
from datetime import datetime
import csv
import logging
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_url_path='/static')
logging.basicConfig(level=logging.INFO)

# Telegram configuration - using environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_notification(name, email, message):
    """Send notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram credentials not configured")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📬 New Form Submission:\nName: {name}\nEmail: {email}\nMessage: {message[:500]}"  # Truncate long messages
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logging.info(f"Telegram notification sent: {response.json()}")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram notification: {str(e)}")
        return False

def write_data(user_data):
    """Safely write user data to CSV file"""
    try:
        name = user_data.get('name', '').replace('|', '')
        email = user_data.get('email', '').replace('|', '')
        message = user_data.get('message', '').replace('|', '')
        time1 = datetime.now()
        
        with open('user_records.csv', 'a', newline='') as csvfile:
            db_writer = csv.writer(csvfile, delimiter='|', 
                                 quotechar=' ', quoting=csv.QUOTE_MINIMAL)
            db_writer.writerow([name, email, message, time1])
        
        # Send Telegram notification
        send_telegram_notification(name, email, message)
        
        return True
    except Exception as e:
        logging.error(f"Error writing to CSV: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_form', methods=['GET', 'POST'])
def submit_form():
    if request.method == "POST":
        try:
            user_data = request.form.to_dict()
            if write_data(user_data):
                message = "Your form is submitted. I'll get back to you ASAP"
            else:
                message = "Form submitted but notification failed"
            return render_template('submit_form.html', message=message)
        except Exception as e:
            logging.error(f"Form submission error: {str(e)}")
            message = "Error submitting form. Please try again."
            return render_template('submit_form.html', message=message)
    else:
        return render_template('submit_form.html', message="FORM NOT SUBMITTED")

if __name__ == "__main__":
    app.run(debug=True)