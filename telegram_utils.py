import urllib.request
import urllib.parse
import json
import os
from flask import current_app

def send_telegram_notification(text, photo_filename=None):
    """
    Sends a notification to the configured Telegram Chat/Channel using built-in urllib.
    Supports PythonAnywhere proxies and dynamic DB settings.
    """
    from models import SystemSettings
    settings = SystemSettings.query.first()
    
    # Preferred: Use DB settings. Fallback: Use Config constants.
    token = settings.telegram_bot_token if settings and settings.telegram_bot_token else current_app.config.get('TELEGRAM_BOT_TOKEN')
    chat_id = settings.telegram_chat_id if settings and settings.telegram_chat_id else current_app.config.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Telegram Notification Skipped: Token or Chat ID missing.")
        return False
        
    try:
        # PythonAnywhere Proxy Support (Free Tier)
        # PA provides api.telegram.org access for free accounts but might require proxy setup for urllib
        if 'PYTHONANYWHERE_SITE' in os.environ:
            proxy_handler = urllib.request.ProxyHandler({
                'http': 'http://proxy.server:3128',
                'https': 'http://proxy.server:3128'
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        # Handle Photo (Text Fallback for urllib stability)
        if photo_filename:
            text = f"{text}\n(يوجد صورة مرفقة)"
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req, data=jsondata, timeout=15) as response:
            return response.getcode() == 200
        
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False

def get_telegram_updates(offset=None):
    """
    Polls the Telegram API for new messages/updates.
    """
    from models import SystemSettings
    settings = SystemSettings.query.first()
    token = settings.telegram_bot_token if settings and settings.telegram_bot_token else current_app.config.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        return []
        
    try:
        # PythonAnywhere Proxy Support
        if 'PYTHONANYWHERE_SITE' in os.environ:
            proxy_handler = urllib.request.ProxyHandler({
                'http': 'http://proxy.server:3128',
                'https': 'http://proxy.server:3128'
            })
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        if offset:
            url += f"?offset={offset}"
            
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('result', [])
    except Exception as e:
        print(f"Error getting Telegram updates: {e}")
        
    return []
