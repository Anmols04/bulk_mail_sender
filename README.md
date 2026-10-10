<div align="center">

# 📧 Mass Mail Sender

**A simple Streamlit app for sending personalized bulk emails over SMTP.**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)


</div>

<img width="1856" height="1035" alt="Screenshot 2026-10-10 095219" src="https://github.com/user-attachments/assets/7a45ddfb-8d05-427b-a1c5-e810919e3223" />


## 📖 Overview

Mass Mail Sender lets you build a recipient list (manually, in bulk, or from a CSV), write a plain-text or HTML email with personalization tags, attach files, and send it to everyone with a single click. It runs locally in your browser, so your credentials stay on your machine.

## 📑 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Gmail Setup](#-gmail-setup)
- [Project Structure](#-project-structure)
- [Limitations](#-limitations)
- [Responsible Use](#-responsible-use)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## 🚀 Features

| Area | What you get |
|------|--------------|
| **SMTP** | Configurable server and port (defaults to Gmail, `smtp.gmail.com:587` with STARTTLS) |
| **Compose** | Plain Text or HTML body, live preview, optional CC |
| **Personalization** | `{name}`, `{email}` and `{date}` tags replaced per recipient |
| **Recipients** | Add one at a time, paste a list, or import a CSV; view, clear and export the list |
| **Attachments** | Multiple files (`pdf`, `doc`, `docx`, `txt`, `jpg`, `png`) attached to every email |
| **Sending** | Progress bar, adjustable delay (0 to 60 s) between emails, per-email error handling |
| **Test mode** | Sends only to your own address so you can check the result first |
| **History** | Success/failure log with a "sent today" counter, downloadable as CSV |

## ⚡ Quick Start

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/Anmols04/bulk_mail_sender.git
cd bulk_mail_sender

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app4.py
```

The app opens at `http://localhost:8501`.

## 🧭 Usage

1. **Sidebar:** enter your SMTP server, port, email address and password.
2. **Compose Email:** write the subject and body, optionally add CC, then click **Preview Email**.
3. **Manage Recipients:** add recipients manually, in bulk, or by CSV.
4. **Attachments:** upload any files to attach (optional).
5. **History:** set the delay, tick **Test Mode** for a trial run, then click **Send Emails**.

### CSV format

The `email` column is required. The `name` column is optional; if it is missing, the part before the `@` is used as the name.

```csv
email,name
john@example.com,John
jane@example.com,Jane
```

### Example email body

```text
Hi {name},

I'm writing to you on {date}. Please find my CV attached.

Regards,
Anmol
```

### Personalization tags

| Tag | Replaced with |
|-----|---------------|
| `{name}` | Recipient's name |
| `{email}` | Recipient's email address |
| `{date}` | Today's date (for example, `October 10, 2026`) |

## 🔐 Gmail Setup

Gmail does not accept your normal password for SMTP. Use an App Password instead:

1. Enable **2-Step Verification** on your Google account.
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and generate one.
3. Paste the 16-character password into the **Password/App Password** field in the app.

For other providers, use their SMTP host and a STARTTLS port (usually `587`), for example `smtp.office365.com`.

## 🗂️ Project Structure

```text
bulk_mail_sender/
├── app4.py            # Streamlit application
├── requirements.txt   # Python dependencies
└── README.md
```

## ⚠️ Limitations

- Recipients and history live only in the current browser session. Refreshing the page clears them, so download the CSVs if you want to keep them.
- Credentials are typed in each session and are not saved. Run the app locally and never share your App Password.
- CC recipients receive a copy of **every** email in the batch.
- Gmail limits attachments to about 25 MB and caps daily sending, so check your provider's limits before large batches.
- Always run a **Test Mode** send first, and keep a delay between emails to reduce the chance of being flagged as spam.

## 🤝 Responsible Use

Only email people who have agreed to hear from you. Unsolicited bulk email may violate anti-spam laws and your email provider's terms of service.

## 🛠️ Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 👤 Author

**Anmol Sharma**
GitHub: [@Anmols04](https://github.com/Anmols04)
