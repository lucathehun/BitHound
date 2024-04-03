
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import ping3
import matplotlib.pyplot as plt

# Configuration
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your email provider's SMTP server
SMTP_PORT = 587                 # May be 465 for SSL
SENDER_EMAIL = 'your sender email'
PASSWORD = 'your sender mail password' 
RECIPIENT_EMAIL = 'your receiver email'
TARGET_HOST = 'www.google.com'  # Website or IP for ping test
TODAY = time.strftime('%Y-%m-%d')

# Data tracking
ping_results = []
timestamps = []

def check_internet_and_record():
    """Checks internet connectivity and stores results."""
    result = ping3.ping(TARGET_HOST)

    # Handle missing results gracefully
    if result is not False:
        ping_results.append(result)
    else:
        ping_results.append(None)  # Indicates connection issue

    timestamps.append(time.strftime('%H:%M'))

def send_report():
    """Generates a plot and sends the email report."""
    plt.figure(figsize=(8, 4))  # Adjust figure size as needed
    plt.plot(timestamps, ping_results)
    plt.xlabel('time')
    plt.ylabel('Ping (ms)')
    plt.title(f'Internet Connectivity Report - {TODAY}')
    plt.grid(True)

    plt.savefig('connectivity_report.png')  # Save plot as an image

    #  Construct email
    msg = MIMEMultipart()
    msg['Subject'] = 'Daily Internet Connectivity Report'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    text = MIMEText("Please find attached the daily internet connectivity report.")
    msg.attach(text)

    with open(f'connectivity_report.png', 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='png')
        attachment.add_header('Content-Disposition', 'attachment', filename=f'connectivity_report.png')
    msg.attach(attachment)

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, PASSWORD)
        smtp.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

# Main loop
while True:
    check_internet_and_record()

    # Adjust the time for the end of the day reporting
    current_hour = int(time.strftime('%H'))
    if current_hour == 23 or ping_results[-1] > 100:  # Send report around 11 PM or when ping is too high
        send_report() 
        # if uptime.log exists, append data to it
        with open(f'uptime_{TODAY}.log', 'a') as f:
            for i in range(len(timestamps)):
                f.write(timestamps[i] + ',' + str(ping_results[i]) + '\n')
        ping_results = []  # Reset data for the next day
        timestamps = [] 

    time.sleep(300)  # Wait for 5 minutes

