import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import io

# Page configuration
st.set_page_config(
    page_title="Mass Email Sender",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'email_column' not in st.session_state:
    st.session_state.email_column = None
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False

# Title
st.title("📧 Mass Email Sender")
st.markdown("---")

# Sidebar for SMTP Configuration
with st.sidebar:
    st.header("⚙️ Email Configuration")
    
    smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com", help="e.g., smtp.gmail.com for Gmail")
    smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
    
    sender_email = st.text_input("Your Email Address")
    sender_password = st.text_input("Email Password/App Password", type="password", 
                                   help="For Gmail, use App Password instead of your regular password")
    
    st.markdown("---")
    st.markdown("### 📝 Tips:")
    st.info("""
    - For Gmail, enable 2FA and create an App Password
    - Test with a small batch first
    - Check your email column selection carefully
    - PDF attachments are supported (CVs, documents, etc.)
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1️⃣ Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # First, try standard reading
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                # If that fails, try with error handling
                uploaded_file.seek(0)  # Reset file pointer
                try:
                    df = pd.read_csv(
                        uploaded_file,
                        on_bad_lines='skip',
                        encoding='utf-8'
                    )
                    st.warning("⚠️ Some rows were skipped due to formatting issues. Please check your CSV.")
                except:
                    # Last resort: try with different delimiter detection
                    uploaded_file.seek(0)
                    df = pd.read_csv(
                        uploaded_file,
                        encoding='utf-8',
                        quotechar='"',
                        escapechar='\\',
                        on_bad_lines='skip'
                    )
                    st.warning("⚠️ CSV had formatting issues. Some rows may have been skipped.")
            
            # Strip whitespace from headers
            df.columns = df.columns.str.strip()
            st.session_state.df = df
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows")
            
            # Show preview
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show column info
            st.subheader("📋 Available Columns")
            st.write(df.columns.tolist())
            
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("💡 **Fix suggestions:**\n- Ensure commas within fields are enclosed in quotes\n- Check for extra commas in your data\n- Verify all rows have the same number of columns")

with col2:
    if st.session_state.df is not None:
        st.header("2️⃣ Select Email Column")
        
        email_column = st.selectbox(
            "Choose the column containing email addresses:",
            options=st.session_state.df.columns.tolist(),
            index=st.session_state.df.columns.tolist().index("Email Address") 
                  if "Email Address" in st.session_state.df.columns.tolist() else 0
        )
        
        st.session_state.email_column = email_column
        
        # Show sample emails
        st.subheader("📧 Sample Email Addresses")
        sample_emails = st.session_state.df[email_column].dropna().head(5).tolist()
        for i, email in enumerate(sample_emails, 1):
            st.text(f"{i}. {email}")
        
        # Email count
        total_emails = st.session_state.df[email_column].notna().sum()
        st.metric("Total Valid Emails", total_emails)
        
        # Show any rows with missing emails
        missing_emails = len(st.session_state.df) - total_emails
        if missing_emails > 0:
            st.warning(f"⚠️ {missing_emails} rows have missing email addresses and will be skipped")

# Email composition section
if st.session_state.df is not None and st.session_state.email_column is not None:
    st.markdown("---")
    st.header("3️⃣ Compose Email")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subject = st.text_input("Email Subject", placeholder="Enter email subject")
        
        # Option to personalize with columns
        st.subheader("📝 Email Body")
        st.info("💡 Tip: Use {ColumnName} to insert data from CSV. Example: Hello {Name}!")
        
        email_body = st.text_area(
            "Email Content",
            height=300,
            placeholder="Dear {Name},\n\nThis is a sample email...\n\nBest regards"
        )
        
        # Show available placeholders
        with st.expander("📌 Available Placeholders"):
            st.write("You can use these placeholders in your email:")
            for col in st.session_state.df.columns:
                st.code(f"{{{col}}}")
    
    with col2:
        st.subheader("📎 Attachments")
        
        # Multiple file uploader for attachments
        attachments = st.file_uploader(
            "Upload files (PDF, DOCX, TXT, Images)",
            type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="You can upload multiple files. Common use: CV/Resume PDFs"
        )
        
        if attachments:
            st.success(f"✅ {len(attachments)} file(s) selected:")
            for att in attachments:
                file_size = len(att.getvalue()) / 1024  # Size in KB
                st.text(f"📄 {att.name} ({file_size:.1f} KB)")
        
        st.markdown("---")
        
        st.subheader("⏱️ Sending Options")
        delay_between_emails = st.slider(
            "Delay between emails (seconds)",
            min_value=0,
            max_value=10,
            value=1,
            help="Add delay to avoid being flagged as spam"
        )
        
        test_mode = st.checkbox("Test Mode (Send to first 3 emails only)", value=True)

# Preview section
if st.session_state.df is not None and subject and email_body:
    st.markdown("---")
    st.header("4️⃣ Preview Email")
    
    # Generate preview with first row
    preview_row = st.session_state.df.iloc[0]
    preview_body = email_body
    
    for col in st.session_state.df.columns:
        placeholder = f"{{{col}}}"
        if placeholder in preview_body:
            preview_body = preview_body.replace(placeholder, str(preview_row[col]))
    
    with st.expander("👁️ View Email Preview (Based on first row)", expanded=True):
        st.markdown(f"**To:** {preview_row[st.session_state.email_column]}")
        st.markdown(f"**Subject:** {subject}")
        st.markdown("**Body:**")
        st.text(preview_body)
        if attachments:
            st.markdown("**Attachments:**")
            for att in attachments:
                st.text(f"📎 {att.name}")

# Confirmation and sending section
if st.session_state.df is not None and subject and email_body and sender_email and sender_password:
    st.markdown("---")
    st.header("5️⃣ Confirm and Send")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        total_to_send = 3 if test_mode else st.session_state.df[st.session_state.email_column].notna().sum()
        st.metric("Emails to Send", total_to_send)
    
    with col2:
        st.metric("Email Column", st.session_state.email_column)
    
    with col3:
        st.metric("Sender", sender_email)
    
    with col4:
        att_count = len(attachments) if attachments else 0
        st.metric("Attachments", att_count)
    
    # Confirmation checkbox
    confirm = st.checkbox(
        "✅ I have reviewed the email preview and confirmed the email column is correct",
        value=False
    )
    
    if confirm:
        if st.button("🚀 Send Emails", type="primary", use_container_width=True):
            # Sending logic
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            failed_count = 0
            failed_emails = []
            
            # Filter recipients
            recipients_df = st.session_state.df[st.session_state.df[st.session_state.email_column].notna()].copy()
            if test_mode:
                recipients_df = recipients_df.head(3)
            
            total = len(recipients_df)
            
            try:
                # Connect to SMTP server
                status_text.text("Connecting to email server...")
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                status_text.text("✅ Connected to email server")
                time.sleep(0.5)
                
                for idx, (_, row) in enumerate(recipients_df.iterrows()):
                    try:
                        recipient_email = row[st.session_state.email_column]
                        
                        # Create message
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = recipient_email
                        msg['Subject'] = subject
                        
                        # Personalize body
                        personalized_body = email_body
                        for col in st.session_state.df.columns:
                            placeholder = f"{{{col}}}"
                            if placeholder in personalized_body:
                                personalized_body = personalized_body.replace(
                                    placeholder, 
                                    str(row[col]) if pd.notna(row[col]) else ""
                                )
                        
                        # Attach body
                        msg.attach(MIMEText(personalized_body, 'plain'))
                        
                        # Attach files
                        if attachments:
                            for attachment_file in attachments:
                                # Reset file pointer to beginning
                                attachment_file.seek(0)
                                
                                # Create MIMEBase object
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment_file.read())
                                encoders.encode_base64(part)
                                part.add_header(
                                    'Content-Disposition',
                                    f'attachment; filename={attachment_file.name}'
                                )
                                msg.attach(part)
                        
                        # Send email
                        server.send_message(msg)
                        success_count += 1
                        status_text.text(f"✅ Sent to {recipient_email} ({success_count}/{total})")
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / total)
                        
                        # Delay between emails
                        if idx < total - 1:
                            time.sleep(delay_between_emails)
                        
                    except Exception as e:
                        failed_count += 1
                        failed_emails.append((recipient_email, str(e)))
                        status_text.text(f"❌ Failed to send to {recipient_email}")
                        time.sleep(0.5)
                
                # Close connection
                server.quit()
                
                # Show final results
                st.success(f"✅ Email sending complete!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ Successfully Sent", success_count)
                with col2:
                    st.metric("❌ Failed", failed_count)
                
                if failed_emails:
                    with st.expander("View Failed Emails"):
                        for email, error in failed_emails:
                            st.text(f"❌ {email}: {error}")
                
                # Balloons for celebration!
                if success_count > 0:
                    st.balloons()
                
            except smtplib.SMTPAuthenticationError:
                st.error("❌ Authentication failed. Please check your email and password/app password.")
            except smtplib.SMTPException as e:
                st.error(f"❌ SMTP error occurred: {str(e)}")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    else:
        st.warning("⚠️ Please check the confirmation box to enable sending emails.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📧 Mass Email Sender | Use responsibly and follow email best practices</p>
    <p style='font-size: 0.8em;'>Tip: Always test with a small batch before sending to all recipients</p>
</div>
""", unsafe_allow_html=True)