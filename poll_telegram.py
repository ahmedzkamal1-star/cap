import os
import time
from app import create_app
from models import SystemSettings, db
from telegram_utils import get_telegram_updates, send_telegram_notification

def poll_bot():
    app = create_app()
    with app.app_context():
        print("Bot polling started... (Press Ctrl+C to stop)")
        last_offset = None
        settings = SystemSettings.query.first()
        platform_url = settings.platform_url if settings and settings.platform_url else "لم يتم تحديد الرابط بعد."
        
        while True:
            try:
                updates = get_telegram_updates(offset=last_offset)
                for update in updates:
                    last_offset = update['update_id'] + 1
                    
                    if 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        text = update['message']['text'].lower()
                        user_name = update['message']['from'].get('first_name', 'طالبنا العزيز')
                        
                        # Keywords to trigger link distribution
                        keywords = ['link', 'الرابط', 'رابط', 'لينك', '/start']
                        if any(k in text for k in keywords):
                            reply = (
                                f"أهلاً بك يا {user_name} في منصة الدحيح! 👋✨\n\n"
                                f"إليك رابط المنصة الخاص بنا:\n"
                                f"🔗 {platform_url}\n\n"
                                f"سجل دخولك الآن وابدأ رحلة التعلم! 🚀"
                            )
                            # Custom send for specific chat_id
                            # We need to modify send_telegram_notification to support custom chat_id
                            # Or just use the token manually here.
                            
                            # Let's use the local helper for simplicity
                            from telegram_utils import current_app
                            import urllib.request, json
                            token = settings.telegram_bot_token if settings and settings.telegram_bot_token else app.config.get('TELEGRAM_BOT_TOKEN')
                            
                            url = f"https://api.telegram.org/bot{token}/sendMessage"
                            data = json.dumps({'chat_id': chat_id, 'text': reply, 'parse_mode': 'HTML'}).encode('utf-8')
                            req = urllib.request.Request(url, data=data)
                            req.add_header('Content-Type', 'application/json')
                            urllib.request.urlopen(req, timeout=10)
                            print(f"Replied to {user_name} with link.")

                time.sleep(3) # Polling interval
            except KeyboardInterrupt:
                print("Polling stopped.")
                break
            except Exception as e:
                print(f"Polling Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    poll_bot()
