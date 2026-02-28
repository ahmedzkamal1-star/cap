import urllib.request
import urllib.parse
import json
import os
from flask import current_app

def send_telegram_notification(text, photo_filename=None, chat_id=None, reply_markup=None):
    """
    Sends a notification to the configured Telegram Chat/Channel using built-in urllib.
    Supports PythonAnywhere proxies and dynamic DB settings.
    """
    from models import SystemSettings
    settings = SystemSettings.query.first()
    
    # Preferred: Use DB settings. Fallback: Use Config constants.
    token = settings.telegram_bot_token if settings and settings.telegram_bot_token else current_app.config.get('TELEGRAM_BOT_TOKEN')
    target_chat_id = chat_id or (settings.telegram_chat_id if settings and settings.telegram_chat_id else current_app.config.get('TELEGRAM_CHAT_ID'))
    
    if not token or not target_chat_id:
        print("Telegram Notification Skipped: Token or Chat ID missing.")
        return False
        
    try:
        # PythonAnywhere Proxy Support (Free Tier)
        if 'PYTHONANYWHERE_SITE' in os.environ:
            proxy_handler = urllib.request.ProxyHandler({'http': 'http://proxy.server:3128', 'https': 'http://proxy.server:3128'})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        # Handle Photo (Text Fallback for urllib stability)
        if photo_filename:
            text = f"{text}\n(يوجد صورة مرفقة)"
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': target_chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req, data=jsondata, timeout=15) as response:
            return response.getcode() == 200
        
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False

def set_telegram_webhook(webhook_url):
    """
    Sets the Telegram webhook to the specified URL.
    """
    from models import SystemSettings
    settings = SystemSettings.query.first()
    token = settings.telegram_bot_token if settings and settings.telegram_bot_token else current_app.config.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        return False, "Token missing"
        
    try:
        if 'PYTHONANYWHERE_SITE' in os.environ:
            proxy_handler = urllib.request.ProxyHandler({'http': 'http://proxy.server:3128', 'https': 'http://proxy.server:3128'})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('ok', False), data.get('description', '')
    except Exception as e:
        return False, str(e)
    return False, "Unknown error"
