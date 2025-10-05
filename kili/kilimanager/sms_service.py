import requests
import json
from django.conf import settings

def send_sms_notification(recipient, message):
    """
    Send SMS notification using Webline SMS API
    
    Args:
        recipient (str): Phone number in format 255XXXXXXXXX
        message (str): SMS message content
    
    Returns:
        dict: API response with status and message
    """
    
    # SMS API configuration
    SMS_API_URL = "https://sms.webline.co.tz/api/v3/sms/send"
    BEARER_TOKEN = "297|qbloKMOZI53C8E7Wt8qOPbsu2DO62QP32oRJSIjM394dbe92"
    SENDER_ID = "TAARIFA"
    
    # Admin phone number (you can move this to settings.py)
    ADMIN_PHONE = "255741228394"
    
    try:
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {BEARER_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare data
        data = {
            'recipient': recipient,
            'sender_id': SENDER_ID,
            'message': message
        }
        
        # Send SMS
        response = requests.post(
            SMS_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        # Check response
        if response.status_code == 200:
            response_data = response.json()
            return {
                'success': True,
                'message': 'SMS sent successfully',
                'response': response_data
            }
        else:
            return {
                'success': False,
                'message': f'SMS API error: {response.status_code}',
                'response': response.text
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'SMS API timeout - request took too long'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'SMS API connection error - unable to connect'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'SMS sending error: {str(e)}'
        }

def send_reservation_notification(booking_id, customer_name, customer_phone, room_type, check_in_date, check_out_date):
    """
    Send reservation notification SMS to admin in Kiswahili
    
    Args:
        booking_id (str): Booking ID
        customer_name (str): Customer full name
        customer_phone (str): Customer phone number
        room_type (str): Room type name
        check_in_date (str): Check-in date
        check_out_date (str): Check-out date
    
    Returns:
        dict: SMS sending result
    """
    
    # Admin phone number
    ADMIN_PHONE = "255713999610"
    
    # Create message in Kiswahili
    message = (
        f"KILI HAVEN LODGE\n"
        f"TAARIFA: Mgeni mpya amefanya uhifadhi wa chumba.\n"
        f"Jina: {customer_name}\n"
        f"Namba ya simu: {customer_phone}\n"
        f"Chumba: {room_type}\n"
        f"Tarehe ya kuingia: {check_in_date}\n"
        f"Tarehe ya kutoka: {check_out_date}\n"
        f"Nambari ya uhifadhi: {booking_id}\n"
        f"Asante kwa kuchagua Kili Haven Lodge!"
    )

    # Send SMS
    result = send_sms_notification(ADMIN_PHONE, message)
    
    return result
