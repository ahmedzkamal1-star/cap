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
                # Re-query settings inside loop to get latest token/url
                settings = SystemSettings.query.first()
                if not settings:
                    print("Error: No system settings found in DB.")
                    time.sleep(10)
                    continue

                platform_url = settings.platform_url if settings and settings.platform_url else "لم يتم تحديد الرابط بعد."
                
                updates = get_telegram_updates(offset=last_offset)
                if updates:
                    print(f"Received {len(updates)} updates.")
                
                for update in updates:
                    last_offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        chat_id = update['message']['chat']['id']
                        user_name = update['message']['from'].get('first_name', 'طالبنا العزيز')
                        
                        # 1. Handle Contact Sharing (Automatic Linking)
                        if 'contact' in update['message']:
                            # ... (rest of contact logic)
                            phone = update['message']['contact']['phone_number'].replace('+', '').strip()
                            # Clean local Egyptian numbers if needed (e.g., 20)
                            if phone.startswith('20') and len(phone) > 11:
                                search_phone = phone[2:] # Remove 20
                            else:
                                search_phone = phone
                                
                            from models import User
                            user = User.query.filter((User.phone.like(f"%{search_phone}%"))).first()
                            
                            if user:
                                user.telegram_id = str(chat_id)
                                db.session.commit()
                                reply = f"✅ تم التعرف عليك يا <b>{user.full_name}</b>!\nتم ربط حسابك في المنصة بهذا الحساب بنجاح. ستصلك تنبيهاتك الشخصية هنا."
                            else:
                                reply = f"❌ لم نجد حساباً مسجلاً برقم الهاتف: {phone}\nيرجى التأكد من كتابة الرقم بشكل صحيح في ملفك الشخصي بالمنصة."
                                
                            send_reply(chat_id, reply, settings, app)
                            continue

                        # 2. Handle Text Commands
                        if 'text' in update['message']:
                            text = update['message']['text'].lower()
                            print(f"Processing message: '{text}' from {user_name} ({chat_id})")
                            
                            # Keywords to trigger link distribution
                            keywords = ['link', 'الرابط', 'رابط', 'لينك', '/start']
                            if any(k in text for k in keywords):
                                reply = (
                                    f"أهلاً بك يا <b>{user_name}</b> في منصة الدحيح! 👋✨\n\n"
                                    f"إليك رابط المنصة الخاص بنا:\n"
                                    f"🔗 {platform_url}\n\n"
                                    f"لحصولك على تنبيهات شخصية (مثل مواعيدك الخاصة أو نتائجك)، اضغط على الزر أدناه لمشاركة رقمك والربط تلقائياً! 👇"
                                )
                                # Send with Reply Keyboard for Contact
                                keyboard = {
                                    'keyboard': [[{'text': '📱 مشاركة رقم الهاتف للربط التلقائي', 'request_contact': True}]],
                                    'resize_keyboard': True,
                                    'one_time_keyboard': True
                                }
                                send_reply(chat_id, reply, settings, app, keyboard)
                                print(f"Replied to {user_name} with link and contact request.")

                time.sleep(3) # Polling interval
            except KeyboardInterrupt:
                print("Polling stopped.")
                break
            except Exception as e:
                print(f"Polling Error: {e}")
                time.sleep(10)

def send_reply(chat_id, text, settings, app, reply_markup=None):
    from telegram_utils import current_app
    import urllib.request, json
    token = settings.telegram_bot_token if settings and settings.telegram_bot_token else app.config.get('TELEGRAM_BOT_TOKEN')
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    try:
        # Proxy for PythonAnywhere
        if 'PYTHONANYWHERE_SITE' in os.environ:
            proxy_handler = urllib.request.ProxyHandler({'http': 'http://proxy.server:3128', 'https': 'http://proxy.server:3128'})
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Send Reply Error: {e}")

if __name__ == "__main__":
    poll_bot()
