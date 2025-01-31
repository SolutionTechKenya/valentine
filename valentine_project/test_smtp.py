import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import sys
import socket

def test_gmail_smtp_verbose(host_user, host_password, recipient_email, timeout=30):
    """
    Test Gmail SMTP configuration with step-by-step feedback
    """
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Connection settings
    smtp_server = "smtp.gmail.com"
    port = 587
    
    try:
        print("1. Creating SMTP connection...")
        # Set default timeout
        socket.setdefaulttimeout(timeout)
        server = smtplib.SMTP(smtp_server, port)
        print("✓ SMTP connection established")
        
        print("\n2. Setting debug level...")
        server.set_debuglevel(1)
        print("✓ Debug level set")
        
        print("\n3. Starting TLS...")
        server.starttls()
        print("✓ TLS started")
        
        print("\n4. Attempting login...")
        server.login(host_user, host_password)
        print("✓ Login successful")
        
        print("\n5. Creating email message...")
        msg = MIMEMultipart()
        msg['From'] = host_user
        msg['To'] = recipient_email
        msg['Subject'] = "Test Email - SMTP Configuration"
        
        body = "This is a test email to verify SMTP configuration."
        msg.attach(MIMEText(body, 'plain'))
        print("✓ Email message created")
        
        print("\n6. Attempting to send email...")
        server.sendmail(host_user, recipient_email, msg.as_string())
        print("✓ Email sent successfully!")
        
        print("\n7. Closing connection...")
        server.quit()
        print("✓ Connection closed")
        
        return True, "Email test completed successfully"
        
    except socket.timeout as e:
        error_msg = f"Connection timed out: {str(e)}"
        print(f"\n❌ Error: {error_msg}")
        return False, error_msg
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Authentication failed: {str(e)}"
        print(f"\n❌ Error: {error_msg}")
        return False, error_msg
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        print(f"\n❌ Error: {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"\n❌ Error: {error_msg}")
        return False, error_msg
    
    finally:
        try:
            server.quit()
        except:
            pass

# Run the test
if __name__ == "__main__":
    print("Starting Gmail SMTP Test\n")
    success, message = test_gmail_smtp_verbose(
        'solutech888@gmail.com',
        'tnaf rvve lsgi ofpf',
        'kinyuanjoro9@gmail.com',
        timeout=30
    )
    
    print("\nFinal Result:")
    print(f"Success: {success}")
    print(f"Message: {message}")