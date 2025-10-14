#!/usr/bin/env python3
"""
Comprehensive script to fix Twilio WhatsApp issues.
This script will help you find the correct WhatsApp number and test the setup.
"""

import os
import time
from dotenv import load_dotenv
from twilio.rest import Client

def fix_twilio_whatsapp():
    """Fix Twilio WhatsApp configuration issues."""
    
    print("Twilio WhatsApp Fix Tool")
    print("=" * 50)
    
    load_dotenv()
    
    # Check environment variables
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    print(f"Current Configuration:")
    print(f"  - Account SID: {account_sid[:8] if account_sid else 'Not Set'}...")
    print(f"  - Auth Token: {'Set' if auth_token else 'Not Set'}")
    print(f"  - FROM WhatsApp: {from_whatsapp}")
    
    if not all([account_sid, auth_token]):
        print("\nERROR: Missing Twilio credentials!")
        print("Please set TWILIO_SID and TWILIO_AUTH_TOKEN in your .env file")
        return False
    
    try:
        client = Client(account_sid, auth_token)
        print("\n✅ Connected to Twilio successfully!")
        
        # Get account info
        account = client.api.accounts(account_sid).fetch()
        print(f"📋 Account: {account.friendly_name}")
        
        # Check if current FROM number works
        print(f"\n🧪 Testing current FROM number: {from_whatsapp}")
        if from_whatsapp:
            try:
                # Try to send a test message (this will show us the error)
                message = client.messages.create(
                    from_=from_whatsapp,
                    to="whatsapp:+919375981112",
                    body="Test message"
                )
                print(f"✅ Current FROM number works! Message SID: {message.sid}")
                return True
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Current FROM number failed: {error_msg}")
                
                if "Channel with the specified From address" in error_msg:
                    print("\n🔍 The FROM number is not valid. Let's find the correct one...")
                    return find_correct_whatsapp_number(client)
                elif "daily messages limit" in error_msg:
                    print("\n⚠️  Rate limit exceeded. You need to wait 24 hours or upgrade your plan.")
                    return False
        else:
            print("❌ No FROM number set. Let's find the correct one...")
            return find_correct_whatsapp_number(client)
            
    except Exception as e:
        print(f"❌ Error connecting to Twilio: {e}")
        return False

def find_correct_whatsapp_number(client):
    """Find the correct WhatsApp number for the account."""
    
    print("\n🔍 Searching for correct WhatsApp numbers...")
    
    # Common sandbox numbers to try
    sandbox_numbers = [
        "+14155238886",  # Most common US sandbox
        "+14155552671",  # Another common sandbox
        "+17744898996",  # Your current number
        "+14155551234",  # Another test number
    ]
    
    working_numbers = []
    
    for number in sandbox_numbers:
        print(f"\n🧪 Testing: whatsapp:{number}")
        try:
            # Try to send a test message
            message = client.messages.create(
                from_=f"whatsapp:{number}",
                to="whatsapp:+919375981112",
                body="Test message"
            )
            print(f"✅ {number} - WORKS! Message SID: {message.sid}")
            working_numbers.append(number)
        except Exception as e:
            error_msg = str(e)
            if "Channel with the specified From address" in error_msg:
                print(f"❌ {number} - Channel not found")
            elif "daily messages limit" in error_msg:
                print(f"⚠️  {number} - Rate limited (but channel exists)")
                working_numbers.append(number)  # This number works, just rate limited
            else:
                print(f"❌ {number} - Error: {error_msg}")
    
    if working_numbers:
        print(f"\n🎉 Found working numbers: {working_numbers}")
        
        # Update .env file
        best_number = working_numbers[0]
        update_env_file(best_number)
        
        print(f"\n✅ Updated .env file with: whatsapp:{best_number}")
        print("🔄 Please restart your backend server to use the new configuration.")
        
        return True
    else:
        print("\n❌ No working WhatsApp numbers found!")
        print("\n💡 Manual Setup Required:")
        print("1. Go to https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
        print("2. Find your sandbox number")
        print("3. Update your .env file with: TWILIO_WHATSAPP_NUMBER=whatsapp:+YOUR_SANDBOX_NUMBER")
        print("4. Make sure to join the sandbox by sending 'join <sandbox-code>' to the sandbox number")
        
        return False

def update_env_file(whatsapp_number):
    """Update the .env file with the correct WhatsApp number."""
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"⚠️  .env file not found. Creating one...")
        create_env_file(whatsapp_number)
        return
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add TWILIO_WHATSAPP_NUMBER
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("TWILIO_WHATSAPP_NUMBER="):
            lines[i] = f"TWILIO_WHATSAPP_NUMBER=whatsapp:{whatsapp_number}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"TWILIO_WHATSAPP_NUMBER=whatsapp:{whatsapp_number}\n")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def create_env_file(whatsapp_number):
    """Create a new .env file with the correct WhatsApp number."""
    
    env_content = f"""# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Twilio Configuration
TWILIO_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:{whatsapp_number}

# Application Configuration
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:8080
"""
    
    with open(".env", 'w') as f:
        f.write(env_content)

if __name__ == "__main__":
    fix_twilio_whatsapp()
