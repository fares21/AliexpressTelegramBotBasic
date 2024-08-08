import json
import telebot
from flask import Flask, request
import threading
from telebot import types
from aliexpress_api import AliexpressApi, models
import re
import os
from urllib.parse import urlparse, parse_qs
import urllib.parse
import requests

# Initialize the bot with the token
TELEGRAM_TOKEN_BOT = os.getenv('TELEGRAM_BOT_TOKEN')
ALIEXPRESS_API_PUBLIC = os.getenv('ALIEXPRESS_API_PUBLIC')
ALIEXPRESS_API_SECRET = os.getenv('ALIEXPRESS_API_SECRET')
bot = telebot.TeleBot(TELEGRAM_TOKEN_BOT)

# Initialize Aliexpress API
try:
    aliexpress = AliexpressApi(ALIEXPRESS_API_PUBLIC, ALIEXPRESS_API_SECRET,
                               models.Language.AR, models.Currency.EUR, 'telegramBot')
    print("AliExpress API initialized successfully.")
except Exception as e:
    print(f"Error initializing AliExpress API: {e}")

# Define keyboards
keyboardStart = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton("⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️", url="https://s.click.aliexpress.com/e/_DdwUZVd")
btn2 = types.InlineKeyboardButton("⭐️تخفيض العملات على منتجات السلة 🛒⭐️", callback_data='click')
btn3 = types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️", url="https://t.me/ShopAliExpressMaroc")
btn4 = types.InlineKeyboardButton("🎬 شاهد كيفية عمل البوت 🎬", url="https://t.me/ShopAliExpressMaroc/9")
btn5 = types.InlineKeyboardButton("💰 حمل تطبيق Aliexpress عبر الضغط هنا للحصول على مكافأة 5 دولار 💰", url="https://a.aliexpress.com/_mtV0j3q")
keyboardStart.add(btn1, btn2, btn3, btn4)

keyboard = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton("⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️", url="https://s.click.aliexpress.com/e/_DdwUZVd")
btn2 = types.InlineKeyboardButton("⭐️تخفيض العملات على منتجات السلة 🛒⭐️", callback_data='click')
btn3 = types.InlineKeyboardButton("❤️ اشترك في القناة للمزيد من العروض ❤️", url="https://t.me/ShopAliExpressMaroc")
keyboard.add(btn1, btn2, btn3)

keyboard_games = types.InlineKeyboardMarkup(row_width=1)
btn1 = types.InlineKeyboardButton("⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️", url="https://s.click.aliexpress.com/e/_DdwUZVd")
btn2 = types.InlineKeyboardButton("⭐️ لعبة Merge boss ⭐️", url="https://s.click.aliexpress.com/e/_DlCyg5Z")
btn3 = types.InlineKeyboardButton("⭐️ لعبة Fantastic Farm ⭐️", url="https://s.click.aliexpress.com/e/_DBBkt9V")
btn4 = types.InlineKeyboardButton("⭐️ لعبة قلب الاوراق Flip ⭐️", url="https://s.click.aliexpress.com/e/_DdcXZ2r")
btn5 = types.InlineKeyboardButton("⭐️ لعبة GoGo Match ⭐️", url="https://s.click.aliexpress.com/e/_DDs7W5D")
keyboard_games.add(btn1, btn2, btn3, btn4, btn5)

# Define function to get exchange rate from USD to MAD
def get_usd_to_mad_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        return data['rates']['MAD']
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

# Define bot handlers
@bot.message_handler(commands=['start'])
def welcome_user(message):
    print("Handling /start command")
    bot.send_message(
        message.chat.id,
        "مرحبا بكم👋 \n" 
        "أنا علي إكسبريس بوت أقوم بتخفيض المنتجات و البحث  عن أفضل العروض إنسخ رابط المنتج وضعه هنا 👇 ستجد جميع عروض المنتج بثمن أقل 🔥",
        reply_markup=keyboardStart)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        print(f"Message received: {message.text}")
        link = extract_link(message.text)
        sent_message = bot.send_message(message.chat.id, 'المرجو الانتظار قليلا، يتم تجهيز العروض ⏳')
        message_id = sent_message.message_id
        if link and "aliexpress.com" in link and not ("p/shoppingcart" in message.text.lower()):
            if "availableProductShopcartIds".lower() in message.text.lower():
                get_affiliate_shopcart_link(link, message)
                return
            get_affiliate_links(message, message_id, link)
        else:
            bot.delete_message(message.chat.id, message_id)
            bot.send_message(message.chat.id, "الرابط غير صحيح ! تأكد من رابط المنتج أو اعد المحاولة.\n"
                                              " قم بإرسال <b> الرابط فقط</b> بدون عنوان المنتج",
                             parse_mode='HTML')
    except Exception as e:
        print(f"Error in echo_all handler: {e}")

def extract_link(text):
    link_pattern = r'https?://\S+|www\.\S+'
    links = re.findall(link_pattern, text)
    if links:
        print(f"Extracted link: {links[0]}")
        return links[0]
    return None

def get_affiliate_links(message, message_id, link):
    try:
        affiliate_link = aliexpress.get_affiliate_links(
            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=620&aff_fcid='
        )
        affiliate_link = affiliate_link[0].promotion_link

        super_links = aliexpress.get_affiliate_links(
            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=562&aff_fcid='
        )
        super_links = super_links[0].promotion_link

        limit_links = aliexpress.get_affiliate_links(
            f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}?sourceType=561&aff_fcid='
        )
        limit_links = limit_links[0].promotion_link

        try:
            img_link = aliexpress.get_products_details([
                '1005006678051682',
                f'https://star.aliexpress.com/share/share.htm?platform=AE&businessType=ProductDetail&redirectUrl={link}'
            ])
            # Print all details of img_link in JSON format
            print(f"Product details object: {json.dumps(img_link[0].__dict__, indent=2, ensure_ascii=False)}")
            price_pro = float(img_link[0].target_sale_price)
            title_link = img_link[0].product_title
            img_link = img_link[0].product_main_image_url
            # Convert price to MAD
            exchange_rate = get_usd_to_mad_rate()
            if exchange_rate:
                price_pro_mad = price_pro * exchange_rate
            else:
                price_pro_mad = price_pro  # fallback to USD if exchange rate not available
            print(f"Product details: {title_link}, {price_pro}, {img_link}")
            bot.delete_message(message.chat.id, message_id)
            bot.send_photo(message.chat.id,
                           img_link,
                           caption=" \n🛒 منتجك هو : 🔥 \n"
                                   f" {title_link} 🛍 \n"
                                   f" سعر المنتج : "
                                   f" {price_pro:.2f} دولار 💵 / {price_pro_mad:.2f} درهم مغربي 💵\n"
                                   " \n قارن بين الاسعار واشتري 🔥 \n"
                                   "💰 عرض العملات (السعر النهائي عند الدفع) : \n"
                                   f"الرابط {affiliate_link} \n"
                                   f"💎 عرض السوبر : \n"
                                   f"الرابط {super_links} \n"
                                   f"🔥 عرض محدود : \n"
                                   f"الرابط {limit_links} \n\n"
                                   "#AliExpressSaverBot ✅",
                           reply_markup=keyboard)
        except Exception as e:
            print(f"Error in get_affiliate_links inner try: {e}")
            bot.delete_message(message.chat.id, message_id)
            bot.send_message(message.chat.id, "قارن بين الاسعار واشتري 🔥 \n"
                                              "💰 عرض العملات (السعر النهائي عند الدفع) : \n"
                                              f"الرابط {affiliate_link} \n"
                                              f"💎 عرض السوبر : \n"
                                              f"الرابط {super_links} \n"
                                              f"♨️ عرض محدود : \n"
                                              f"الرابط {limit_links} \n\n"
                                              "#AliExpressSaverBot ✅",
                             reply_markup=keyboard)
    except Exception as e:
        print(f"Error in get_affiliate_links: {e}")
        bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")

def build_shopcart_link(link):
    params = get_url_params(link)
    shop_cart_link = "https://www.aliexpress.com/p/trade/confirm.html?"
    shop_cart_params = {
        "availableProductShopcartIds": ",".join(params["availableProductShopcartIds"]),
        "extraParams": json.dumps({"channelInfo": {"sourceType": "620"}}, separators=(',', ':'))
    }
    return create_query_string_url(link=shop_cart_link, params=shop_cart_params)

def get_url_params(link):
    parsed_url = urlparse(link)
    params = parse_qs(parsed_url.query)
    return params

def create_query_string_url(link, params):
    return link + urllib.parse.urlencode(params)

def get_affiliate_shopcart_link(link, message):
    try:
        shopcart_link = build_shopcart_link(link)
        affiliate_link = aliexpress.get_affiliate_links(shopcart_link)[0].promotion_link
        text2 = f"هذا رابط تخفيض السلة \n{str(affiliate_link)}"
        img_link3 = "https://i.postimg.cc/1Xrk1RJP/Copy-of-Basket-aliexpress-telegram.png"
        bot.send_photo(message.chat.id, img_link3, caption=text2)
    except Exception as e:
        print(f"Error in get_affiliate_shopcart_link: {e}")
        bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        print(f"Callback query received: {call.data}")
        if call.data == 'click':
            # Replace with your link and message if needed
            link = 'https://www.aliexpress.com/p/shoppingcart/index.html?'
            get_affiliate_shopcart_link(link, call.message)
        else:
            bot.send_message(call.message.chat.id, "..")
            img_link2 = "https://i.postimg.cc/VvmhgQ1h/Basket-aliexpress-telegram.png"
            bot.send_photo(call.message.chat.id,
                           img_link2,
                           caption="روابط ألعاب جمع العملات المعدنية لإستعمالها في خفض السعر لبعض المنتجات، قم بالدخول يوميا لها للحصول على أكبر عدد ممكن في اليوم 👇",
                           reply_markup=keyboard_games)
    except Exception as e:
        print(f"Error in handle_callback_query: {e}")

# Flask app for handling webhook

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return 'OK', 200

# Start Flask app in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.remove_webhook()
    bot.set_webhook(url='https://bottelegramaliexpress.onrender.com/webhook')
