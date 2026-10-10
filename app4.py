import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import time
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="Mass Mail Sender",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'email_list' not in st.session_state:
    st.session_state.email_list = []
if 'send_history' not in st.session_state:
    st.session_state.send_history = []

# Title and description
st.title("📧 Mass Mail Sender")
st.markdown("---")

# Sidebar for SMTP Configuration
with st.sidebar:
    st.header("⚙️ SMTP Configuration")
    
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com", help="e.g., smtp.gmail.com for Gmail")
    smtp_port = st.number_input("SMTP Port", value=587, help="Usually 587 for TLS")
    sender_email = st.text_input("Your Email", help="The email you're sending from")
    sender_password = st.text_input("Password/App Password", type="password", 
                                   help="For Gmail, use App Password instead of regular password")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Total Emails in List", len(st.session_state.email_list))
    st.metric("Emails Sent Today", len([h for h in st.session_state.send_history 
                                        if h['date'] == datetime.now().strftime("%Y-%m-%d")]))

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Compose Email", "👥 Manage Recipients", "📎 Attachments", "📜 History"])

# Tab 1: Compose Email
with tab1:
    st.header("Compose Your Email")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.text_input("Subject Line", placeholder="Enter email subject")
        
        # --- NEW: CC Input Field ---
        cc_emails = st.text_input(
            "CC (Optional)", 
            placeholder="manager@example.com, hr@example.com",
            help="Separate multiple emails with commas. WARNING: These recipients will receive a copy of EVERY email sent in the batch."
        )
        # ---------------------------

        # Email body with formatting options
        st.markdown("**Email Body**")
        body_format = st.radio("Format", ["Plain Text", "HTML"], horizontal=True)
        
        if body_format == "Plain Text":
            email_body = st.text_area("Message", height=300, 
                                     placeholder="Type your message here...")
        else:
            email_body = st.text_area("HTML Content", height=300, 
                                     placeholder="<html><body><h1>Your HTML content here</h1></body></html>")
    
    with col2:
        st.markdown("**Personalization Tags**")
        st.info("""
        Use these tags in your email:
        - `{email}` - Recipient's email
        - `{name}` - Recipient's name (if provided)
        - `{date}` - Current date
        """)
        
        # Preview button
        if st.button("👁️ Preview Email"):
            st.markdown("### Preview")
            st.markdown(f"**Subject:** {subject}")
            
            # --- NEW: Preview CC ---
            if cc_emails:
                st.markdown(f"**CC:** {cc_emails}")
            # -----------------------

            st.markdown("**Body:**")
            if body_format == "HTML":
                st.markdown(email_body, unsafe_allow_html=True)
            else:
                st.text(email_body)

# Tab 2: Manage Recipients
with tab2:
    st.header("Manage Email Recipients")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Add Individual Email")
        
        with st.form("add_individual_email"):
            new_email = st.text_input("Email Address")
            recipient_name = st.text_input("Name (Optional)")
            submitted = st.form_submit_button("Add to List")
            
            if submitted:
                if new_email:
                    if '@' in new_email:
                        st.session_state.email_list.append({
                            'email': new_email,
                            'name': recipient_name if recipient_name else new_email.split('@')[0]
                        })
                        st.success(f"✅ Added {new_email}")
                    else:
                        st.error("Invalid email format")
                else:
                    st.warning("Please enter an email address")
    
    with col2:
        st.subheader("📋 Bulk Add Emails")
        
        with st.form("add_bulk_emails"):
            bulk_emails = st.text_area("Enter emails (one per line)", height=150,
                                       placeholder="email1@example.com\nemail2@example.com\nemail3@example.com")
            submitted_bulk = st.form_submit_button("Add Bulk Emails")
            
            if submitted_bulk:
                if bulk_emails:
                    lines = bulk_emails.strip().split('\n')
                    added = 0
                    for line in lines:
                        email = line.strip()
                        if email and '@' in email:
                            st.session_state.email_list.append({
                                'email': email,
                                'name': email.split('@')[0]
                            })
                            added += 1
                    st.success(f"✅ Added {added} emails to the list")
                else:
                    st.warning("Please enter at least one email")
    
    st.markdown("---")
    
    # Upload CSV
    st.subheader("📁 Import from CSV")
    uploaded_file = st.file_uploader("Upload CSV file (must have 'email' column)", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            if 'email' in df.columns:
                st.dataframe(df.head())
                
                with st.form("import_csv"):
                    submitted_csv = st.form_submit_button("Import from CSV")
                    
                    if submitted_csv:
                        for _, row in df.iterrows():
                            st.session_state.email_list.append({
                                'email': row['email'],
                                'name': row.get('name', row['email'].split('@')[0])
                            })
                        st.success(f"✅ Imported {len(df)} emails")
            else:
                st.error("CSV must contain an 'email' column")
        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")
    
    st.markdown("---")
    
    # Display current email list
    st.subheader("📬 Current Email List")
    
    if st.session_state.email_list:
        df_emails = pd.DataFrame(st.session_state.email_list)
        
        # Add delete functionality
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(df_emails, use_container_width=True, height=300)
        with col2:
            with st.form("clear_emails"):
                if st.form_submit_button("🗑️ Clear All", type="secondary"):
                    st.session_state.email_list = []
                    st.success("Email list cleared")
            
            # Download as CSV
            csv = df_emails.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"email_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No emails in the list yet. Add some above!")

# Tab 3: Attachments
with tab3:
    st.header("📎 Manage Attachments")
    
    uploaded_files = st.file_uploader(
        "Upload CV/Resume (PDF) or other attachments",
        type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'],
        accept_multiple_files=True,
        help="You can upload multiple files"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) ready to attach")
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"📄 {file.name}")
            with col2:
                st.text(f"{file.size / 1024:.2f} KB")
            with col3:
                st.text(file.type)
    
    st.info("💡 Tip: For Gmail, keep total attachment size under 25MB")

# Tab 4: Send Emails & History
with tab4:
    st.header("📤 Send Emails")
    
    # Send configuration
    col1, col2 = st.columns(2)
    with col1:
        delay_between = st.number_input("Delay between emails (seconds)", 
                                       min_value=0, max_value=60, value=2,
                                       help="Prevents being flagged as spam")
    with col2:
        test_mode = st.checkbox("Test Mode (send only to yourself)", value=False)
    
    st.markdown("---")
    
    # Send button
    if st.button("🚀 Send Emails", type="primary", use_container_width=True):
        # Validation
        if not sender_email or not sender_password:
            st.error("Please configure SMTP settings in the sidebar")
        elif not subject or not email_body:
            st.error("Please compose your email in the 'Compose Email' tab")
        elif not st.session_state.email_list and not test_mode:
            st.error("Please add recipients in the 'Manage Recipients' tab")
        else:
            # Sending process
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            recipients = [{'email': sender_email, 'name': 'Test'}] if test_mode else st.session_state.email_list
            total_emails = len(recipients)
            success_count = 0
            fail_count = 0
            
            try:
                # Connect to SMTP server
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                
                for idx, recipient in enumerate(recipients):
                    try:
                        # Create message
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = recipient['email']
                        msg['Subject'] = subject
                        
                        # --- NEW: Add CC Header ---
                        if cc_emails:
                            msg['Cc'] = cc_emails
                        # --------------------------
                        
                        # Personalize body
                        personalized_body = email_body.replace('{email}', recipient['email'])
                        personalized_body = personalized_body.replace('{name}', recipient['name'])
                        personalized_body = personalized_body.replace('{date}', datetime.now().strftime("%B %d, %Y"))
                        
                        # Attach body
                        if body_format == "HTML":
                            msg.attach(MIMEText(personalized_body, 'html'))
                        else:
                            msg.attach(MIMEText(personalized_body, 'plain'))
                        
                        # Attach files
                        if uploaded_files:
                            for file in uploaded_files:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(file.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename={file.name}')
                                msg.attach(part)
                                file.seek(0)  # Reset file pointer
                        
                        # Send email
                        # Note: send_message automatically looks at To, Cc, Bcc headers if recipients aren't specified explicitly
                        server.send_message(msg)
                        success_count += 1
                        
                        # Log to history
                        st.session_state.send_history.append({
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'recipient': recipient['email'],
                            'subject': subject,
                            'status': 'Success'
                        })
                        
                        # Update progress
                        progress = (idx + 1) / total_emails
                        progress_bar.progress(progress)
                        status_text.text(f"Sending... {idx + 1}/{total_emails}")
                        
                        # Delay
                        if idx < total_emails - 1:
                            time.sleep(delay_between)
                            
                    except Exception as e:
                        fail_count += 1
                        st.session_state.send_history.append({
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'time': datetime.now().strftime("%H:%M:%S"),
                            'recipient': recipient['email'],
                            'subject': subject,
                            'status': f'Failed: {str(e)}'
                        })
                
                server.quit()
                
                # Final status
                st.success(f"✅ Completed! {success_count} sent successfully, {fail_count} failed")
                
            except Exception as e:
                st.error(f"❌ SMTP Error: {str(e)}")
    
    st.markdown("---")
    
    # History section
    st.subheader("📜 Sending History")
    
    if st.session_state.send_history:
        df_history = pd.DataFrame(st.session_state.send_history)
        
        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(df_history, use_container_width=True, height=300)
        with col2:
            with st.form("clear_history"):
                if st.form_submit_button("🗑️ Clear History", type="secondary"):
                    st.session_state.send_history = []
                    st.success("History cleared")
            
            # Download history
            csv_history = df_history.to_csv(index=False)
            st.download_button(
                label="⬇️ Download History",
                data=csv_history,
                file_name=f"send_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No sending history yet")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <b>Tips:</b></p>
    <ul style='list-style-position: inside;'>
        <li>For Gmail, enable 2-Factor Authentication and use App Password</li>
        <li>Test with a few emails before sending to your entire list</li>
        <li>Add delays between emails to avoid spam filters</li>
        <li>Keep attachment sizes reasonable (under 25MB for Gmail)</li>
    </ul>
</div>
""", unsafe_allow_html=True)