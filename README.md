📧 Mass Email Sender

A Streamlit-based web application to send personalized bulk emails using data from a CSV file.
You can easily configure SMTP settings (e.g., Gmail), preview emails before sending, attach multiple files, and insert custom placeholders using your CSV columns.

🚀 Features

Upload and preview CSV data

Automatically detect email column

Personalize emails using placeholders like {Name}, {Company}, etc.

Attach PDFs, DOCs, or images

Optional test mode (send to first 3 recipients only)

Progress tracking and error reporting

Safe Gmail integration using App Passwords

🧩 Requirements

Create a file named requirements.txt with the following content:

streamlit
pandas


✅ (Optional but recommended)
If you're deploying on Streamlit Cloud, the above is enough — Python’s built-in smtplib and email modules are already included.

🔑 How to Generate Your Gmail App Password

If you’re using Gmail, you must use an App Password (not your normal password).
Here’s how to create one:

Go to your Google Account Security settings
👉 https://myaccount.google.com/apppasswords

Log in and enable 2-Step Verification if not already enabled.

Under “App passwords”, select:

App: Mail

Device: Other → type Mass Email Sender

Click Generate — copy the 16-character key shown (e.g., abcd efgh ijkl mnop)

Use this key as your Email Password in the app sidebar.

⚙️ How to Run

Clone or download this repository.

Install dependencies:

pip install -r requirements.txt


Run the Streamlit app:

streamlit run app.py


Open the link displayed in your terminal (usually http://localhost:8501).

📂 CSV Format Example
Name	Email Address	Company
John	john@example.com
	Acme Corp
Alice	alice@example.com
	Beta Inc.

In your email body, you can use:

Dear {Name},

We are excited to collaborate with {Company}.

⚠️ Notes

Avoid sending large batches to prevent spam flags.

Always test with “Test Mode” checked before full send.

Use responsibly and comply with email regulations (CAN-SPAM, GDPR, etc.).


