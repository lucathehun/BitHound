
import os
import webbrowser
import smtplib
import time
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import ping3
import matplotlib.pyplot as plt

# Configuration
MONITORING = True
EMAIL_SERVER = 'smtp.gmail.com'  # Replace with your email provider's SMTP server
SMTP_PORT = 587                 # May be 465 for SSL
SENDER_EMAIL = 'sender_email'
PASSWORD = 'password' 
RECIPIENT_EMAIL = 'uptime.loging@gmail.com'
TARGET_HOST = 'www.google.com'  # Website or IP for ping test
TODAY = time.strftime('%Y-%m-%d')

# Data tracking
PING_RESULTS = [] 
TIMESTAMPS = []

def check_internet_and_record():
    """Checks internet connectivity and stores results."""
    result = ping3.ping(TARGET_HOST)

    # Handle missing results gracefully
    if result is not False:
        PING_RESULTS.append(result)
    else:
        PING_RESULTS.append(0)  # Indicates connection issue

    TIMESTAMPS.append(time.strftime('%H:%M'))

def send_report():
    """Generates a plot and sends the email report."""
    hours = []
    for i in range(len(TIMESTAMPS)):
        if TIMESTAMPS[i].split(':')[0] not in hours:
            hours.append(TIMESTAMPS[i].split(':')[0])
        else:
            hours.append(' ')
    plt.figure(figsize=(8, 4))  # Adjust figure size as needed
    plt.plot(hours, PING_RESULTS)
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
    with smtplib.SMTP(EMAIL_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, PASSWORD)
        smtp.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

# Main loop
def main(PING_RESULTS, TIMESTAMPS):
    while MONITORING == True:
        check_internet_and_record()
        
        # Adjust the time for the end of the day reporting
        current_hour = int(time.strftime('%H'))
        if current_hour == 23:   # Send report around 11 PM or when ping is too high
            send_report() 
            # if uptime.log exists, append data to it
            with open(f'uptime_{TODAY}.log', 'a') as f:
                for i in range(len(TIMESTAMPS)):
                    f.write(TIMESTAMPS[i] + ',' + str(PING_RESULTS[i]) + '\n')
            PING_RESULTS = []  # Reset data for the next day
            TIMESTAMPS = [] 

        time.sleep(300)  # Wait for 5 minutes
        emailscanner(PING_RESULTS, TIMESTAMPS)

# Start main loop
def emailscanner(PING_RESULTS, TIMESTAMPS):
    while True:
        mail = imaplib.IMAP4_SSL(EMAIL_SERVER, 993)
        mail.login(SENDER_EMAIL, PASSWORD)
        mail.select("inbox")
        result, data = mail.uid("search", None, "ALL")
        mails = len(data[0].split())
        # Find all emails in the inbox
        status, messages = mail.search(None, 'ALL')
        latest_email_uid = data[0].split()[-1]
        result, email_data = mail.uid("fetch", latest_email_uid, "(RFC822)") 


        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode("utf-8")
        email_message = email.message_from_string(raw_email_string)
        subject = email_message["subject"]
        print (subject)
        if subject == "start":
            main(PING_RESULTS, TIMESTAMPS)
        elif subject == "stop":
            MONITORING = False
        elif subject == "reset":
            os.system(f"mv uptime_{TODAY} logs/uptime_{TODAY}.log")
            PING_RESULTS = []
            TIMESTAMPS = []
        elif subject == "scan":
            check_internet_and_record()
            send_report()
        elif subject == "clear":
            os.system("rm -rf logs/ && mkdir logs")
        else:
            continue

emailscanner(PING_RESULTS, TIMESTAMPS)
     
