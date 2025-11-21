import json
import os
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs

import requests
import telebot
from aliexpress_api import AliexpressApi, models
from dotenv import load_dotenv
from flask import Flask, request
from telebot import types

# =========================
# إعداد المتغيرات والـ APIs
# =========================

load_dotenv()

TELEGRAM_TOKEN_BOT = os.getenv("TELEGRAM_BOT_TOKEN")
ALIEXPRESS_API_PUBLIC = os.getenv("ALIEXPRESS_API_PUBLIC")
ALIEXPRESS_API_SECRET = os.getenv("ALIEXPRESS_API_SECRET")

if not TELEGRAM_TOKEN_BOT:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

if not ALIEXPRESS_API_PUBLIC or not ALIEXPRESS_API_SECRET:
    raise RuntimeError("ALiExpress API credentials are not set")

bot = telebot.TeleBot(TELEGRAM_TOKEN_BOT, parse_mode="HTML")

try:
    aliexpress = AliexpressApi(
        ALIEXPRESS_API_PUBLIC,
        ALIEXPRESS_API_SECRET,
        models.Language.AR,
        models.Currency.EUR,
        "telegramBot",
    )
    print("AliExpress API initialized successfully.")
except Exception as e:
    print(f"Error initializing AliExpress API: {e}")
    raise

# ==========
# Keyboards
# ==========

keyboardStart = types.InlineKeyboardMarkup(row_width=1)
keyboardStart.add(
    types.InlineKeyboardButton(
        "⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️",
        url="https://s.click.aliexpress.com/e/_DdwUZVd",
    ),
    types.InlineKeyboardButton(
        "⭐️تخفيض العملات على منتجات السلة 🛒⭐️",
        callback_data="click",
    ),
    types.InlineKeyboardButton(
        "❤️ اشترك في القناة للمزيد من العروض ❤️",
        url="https://t.me/ShopAliExpressMaroc",
    ),
    types.InlineKeyboardButton(
        "🎬 شاهد كيفية عمل البوت 🎬",
        url="https://t.me/ShopAliExpressMaroc/9",
    ),
)

keyboard = types.InlineKeyboardMarkup(row_width=1)
keyboard.add(
    types.InlineKeyboardButton(
        "⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️",
        url="https://s.click.aliexpress.com/e/_DdwUZVd",
    ),
    types.InlineKeyboardButton(
        "⭐️تخفيض العملات على منتجات السلة 🛒⭐️",
        callback_data="click",
    ),
    types.InlineKeyboardButton(
        "❤️ اشترك في القناة للمزيد من العروض ❤️",
        url="https://t.me/ShopAliExpressMaroc",
    ),
)

keyboard_games = types.InlineKeyboardMarkup(row_width=1)
keyboard_games.add(
    types.InlineKeyboardButton(
        "⭐️ صفحة مراجعة وجمع النقاط يوميا ⭐️",
        url="https://s.click.aliexpress.com/e/_DdwUZVd",
    ),
    types.InlineKeyboardButton(
        "⭐️ لعبة Merge boss ⭐️",
        url="https://s.click.aliexpress.com/e/_DlCyg5Z",
    ),
    types.InlineKeyboardButton(
        "⭐️ لعبة Fantastic Farm ⭐️",
        url="https://s.click.aliexpress.com/e/_DBBkt9V",
    ),
    types.InlineKeyboardButton(
        "⭐️ لعبة قلب الاوراق Flip ⭐️",
        url="https://s.click.aliexpress.com/e/_DdcXZ2r",
    ),
    types.InlineKeyboardButton(
        "⭐️ لعبة GoGo Match ⭐️",
        url="https://s.click.aliexpress.com/e/_DDs7W5D",
    ),
)

# ======================
# دوال مساعدة Utilities
# ======================


def get_usd_to_mad_rate() -> float | None:
    """جلب سعر تحويل USD إلى MAD."""
    try:
        resp = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD", timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return float(data["rates"]["MAD"])
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None


def resolve_full_redirect_chain(link: str) -> str:
    """حل كل التحويلات للحصول على رابط AliExpress النهائي."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.36"
        )
    }
    try:
        session_req = requests.Session()
        resp = session_req.get(
            link, allow_redirects=True, timeout=10, headers=headers
        )
        final_url = resp.url
        print(f"🔗 Resolved URL: {link} -> {final_url}")

        if "star.aliexpress.com" in final_url:
            parsed_url = urlparse(final_url)
            params = parse_qs(parsed_url.query)
            if "redirectUrl" in params:
                redirect_url = params["redirectUrl"][0]
                print(f"🔗 Found redirectUrl: {redirect_url}")
                return redirect_url

        return final_url
    except requests.RequestException as e:
        print(f"❌ Error resolving redirect chain for link {link}: {e}")
        return link


def extract_product_id(link: str) -> str | None:
    """استخراج product_id من رابط AliExpress (يتعامل مع روابط مختصرة وطويلة)."""
    print(f"🔍 Extracting product ID from: {link}")
    resolved_link = resolve_full_redirect_chain(link)
    print(f"🔗 Using resolved link: {resolved_link}")

    match = re.search(r"/item/(d+).html", resolved_link)
    if match:
        pid = match.group(1)
        print(f"✅ Extracted product ID (standard): {pid}")
        return pid

    coin_match = re.search(r"productIds=(d+)", resolved_link)
    if coin_match:
        pid = coin_match.group(1)
        print(f"✅ Extracted product ID (coin-index): {pid}")
        return pid

    match_alt = re.search(r"(d{13,})", resolved_link)
    if match_alt:
        pid = match_alt.group(1)
        print(f"✅ Extracted product ID (long format): {pid}")
        return pid

    print(f"❌ Could not extract product ID from: {resolved_link}")
    return None


def generate_coin_affiliate_link(product_id: str) -> str | None:
    """لينك coin-index (قناة 620)."""
    try:
        coin_index_url = (
            "https://m.aliexpress.com/p/coin-index/index.html"
            f"?_immersiveMode=true&from=syicon&productIds={product_id}"
        )
        affiliate_link = aliexpress.get_affiliate_links(coin_index_url)
        return affiliate_link[0].promotion_link
    except Exception as e:
        print(f"❌ Error generating coin affiliate link for product {product_id}: {e}")
        return None


def generate_bundle_affiliate_link(product_id: str, original_link: str) -> str | None:
    """لينك bundle (قناة 560)."""
    try:
        bundle_url = (
            "https://star.aliexpress.com/share/share.htm"
            "?platform=AE&businessType=ProductDetail"
            f"&redirectUrl={original_link}?sourceType=560&aff_fcid="
        )
        affiliate_link = aliexpress.get_affiliate_links(bundle_url)
        return affiliate_link[0].promotion_link
    except Exception as e:
        print(f"❌ Error generating bundle affiliate link for product {product_id}: {e}")
        return None


def extract_link(text: str) -> str | None:
    """استخراج أول رابط من نص الرسالة."""
    links = re.findall(r"https?://S+|www.S+", text)
    if links:
        print(f"Extracted link: {links[0]}")
        return links[0]
    return None


def get_url_params(link: str) -> dict:
    parsed_url = urlparse(link)
    return parse_qs(parsed_url.query)


def create_query_string_url(link: str, params: dict) -> str:
    return link + urllib.parse.urlencode(params)


def build_shopcart_link(link: str) -> str:
    params = get_url_params(link)
    shop_cart_link = "https://www.aliexpress.com/p/trade/confirm.html?"
    shop_cart_params = {
        "availableProductShopcartIds": ",".join(
            params.get("availableProductShopcartIds", [])
        ),
        "extraParams": json.dumps(
            {"channelInfo": {"sourceType": "620"}}, separators=(",", ":")
        ),
    }
    return create_query_string_url(shop_cart_link, shop_cart_params)


def get_affiliate_shopcart_link(link: str, message):
    try:
        shopcart_link = build_shopcart_link(link)
        affiliate_link = aliexpress.get_affiliate_links(shopcart_link)[0].promotion_link
        text2 = f"هذا رابط تخفيض السلة {affiliate_link}"
        img_link3 = ("https://i.postimg.cc/1Xrk1RJP/Copy-of-Basket-aliexpress-telegram.png")
        bot.send_photo(message.chat.id, img_link3, caption=text2)
    except Exception as e:
        print(f"Error in get_affiliate_shopcart_link: {e}")
        bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")


# ==========
# Handlers
# ==========


@bot.message_handler(commands=["start"])
def welcome_user(message):
    print("Handling /start command")
    bot.send_message(
        message.chat.id,
        ("مرحبا بكم 👋\n"
         "أنا علي إكسبريس بوت أقوم بتخفيض المنتجات والبحث عن أفضل العروض.\n"
         "انسخ رابط المنتج وضعه هنا 👇 ستجد جميع عروض المنتج بثمن أقل 🔥"),
        reply_markup=keyboardStart,
    )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        print(f"Message received: {message.text}")
        link = extract_link(message.text or "")
        sent = bot.send_message(
            message.chat.id, "المرجو الانتظار قليلا، يتم تجهيز العروض ⏳"
        )
        loading_msg_id = sent.message_id

        if (
            link
            and "aliexpress.com" in link.lower()
            and "p/shoppingcart" not in message.text.lower()
        ):
            if "availableProductShopcartIds".lower() in message.text.lower():
                get_affiliate_shopcart_link(link, message)
            else:
                get_affiliate_links(message, loading_msg_id, link)
        else:
            bot.delete_message(message.chat.id, loading_msg_id)
            bot.send_message(
                message.chat.id,
                (
                    "الرابط غير صحيح! تأكد من رابط المنتج أو أعد المحاولة."
                    "قم بإرسال <b>الرابط فقط</b> بدون عنوان المنتج."
                ),
            )
    except Exception as e:
        print(f"Error in echo_all handler: {e}")


def get_affiliate_links(message, loading_msg_id: int, link: str):
    try:
        resolved_link = resolve_full_redirect_chain(link)
        if not resolved_link:
            bot.delete_message(message.chat.id, loading_msg_id)
            bot.send_message(
                message.chat.id,
                "❌ لم أتمكن من حل الرابط! تأكد من رابط المنتج أو أعد المحاولة.",
            )
            return

        product_id = extract_product_id(resolved_link)
        if not product_id:
            bot.delete_message(message.chat.id, loading_msg_id)
            bot.send_message(
                message.chat.id,
                "❌ لم أتمكن من استخراج معرف المنتج من الرابط.",
            )
            return

        coin_affiliate_link = generate_coin_affiliate_link(product_id)
        bundle_affiliate_link = generate_bundle_affiliate_link(
            product_id, resolved_link
        )

        super_links = aliexpress.get_affiliate_links(
            "https://star.aliexpress.com/share/share.htm"
            f"?platform=AE&businessType=ProductDetail&redirectUrl={resolved_link}"
            "&sourceType=562&aff_fcid="
        )[0].promotion_link

        limit_links = aliexpress.get_affiliate_links(
            "https://star.aliexpress.com/share/share.htm"
            f"?platform=AE&businessType=ProductDetail&redirectUrl={resolved_link}"
            "&sourceType=561&aff_fcid="
        )[0].promotion_link

        try:
            products = aliexpress.get_products_details(
                [product_id],
                fields=[
                    "target_sale_price",
                    "product_title",
                    "product_main_image_url",
                ],
            )
            bot.delete_message(message.chat.id, loading_msg_id)

            if products:
                p = products[0]
                print(
                    "Product details object: "
                    f"{json.dumps(p.__dict__, indent=2, ensure_ascii=False)}"
                )

                price_usd = float(p.target_sale_price)
                title = p.product_title
                img_link = p.product_main_image_url

                rate = get_usd_to_mad_rate()
                price_mad = price_usd * rate if rate else price_usd

                msg = (
                    "🛒 منتجك هو : 🔥"
                    f"{title} 🛍"
                    "سعر المنتج : "
                    f"{price_usd:.2f} دولار 💵 / {price_mad:.2f} درهم مغربي 💵"
                    "قارن بين الأسعار واشتري 🔥"
                )
            else:
                msg = "قارن بين الأسعار واشتري 🔥"

            if coin_affiliate_link:
                msg += (
                    "💰 عرض العملات (السعر النهائي عند الدفع):"
                    f"{coin_affiliate_link}"
                )

            if bundle_affiliate_link:
                msg += (
                    "📦 عرض الحزمة (عروض متنوعة):"
                    f"{bundle_affiliate_link}"
                )

            msg += (
                "💎 عرض السوبر:"
                f"{super_links}"
                "🔥 عرض محدود:"
                f"{limit_links}"
                "#AliExpressSaverBot ✅"
            )

            if products:
                bot.send_photo(message.chat.id, img_link, caption=msg, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, msg, reply_markup=keyboard)

        except Exception as e:
            print(f"Error in get_affiliate_links inner try: {e}")
            bot.delete_message(message.chat.id, loading_msg_id)

            msg = "قارن بين الأسعار واشتري 🔥"
            if coin_affiliate_link:
                msg += (
                    "💰 عرض العملات (السعر النهائي عند الدفع):"
                    f"{coin_affiliate_link}"
                )
            if bundle_affiliate_link:
                msg += (
                    "📦 عرض الحزمة (عروض متنوعة):"
                    f"{bundle_affiliate_link}"
                )
            msg += (
                "💎 عرض السوبر:"
                f"{super_links}"
                "🔥 عرض محدود:"
                f"{limit_links}"
                "#AliExpressSaverBot ✅"
            )
            bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    except Exception as e:
        print(f"Error in get_affiliate_links: {e}")
        bot.send_message(message.chat.id, "حدث خطأ 🤷🏻‍♂️")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        print(f"Callback query received: {call.data}")
        if call.data == "click":
            link = "https://www.aliexpress.com/p/shoppingcart/index.html?"
            get_affiliate_shopcart_link(link, call.message)
        else:
            bot.send_message(call.message.chat.id, "..")
            img_link2 = (
                "https://i.postimg.cc/VvmhgQ1h/Basket-aliexpress-telegram.png"
            )
            bot.send_photo(
                call.message.chat.id,
                img_link2,
                caption=(
                    "روابط ألعاب جمع العملات المعدنية لإستعمالها في خفض السعر لبعض "
                    "المنتجات، قم بالدخول يوميا لها للحصول على أكبر عدد ممكن في اليوم 👇"
                ),
                reply_markup=keyboard_games,
            )
    except Exception as e:
        print(f"Error in handle_callback_query: {e}")


# ========================
# Flask + Webhook (Render)
# ========================

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        return "WEBHOOK_URL not set", 500
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        return f"webhook set to {webhook_url}", 200
    except Exception as e:
        return f"error setting webhook: {e}", 500


@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200
