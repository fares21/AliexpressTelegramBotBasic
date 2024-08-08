import telebot
from aliexpress_api import AliexpressApi, models
import random
import logging
import requests
import schedule
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the bot with your token
bot = telebot.TeleBot('7203070953:AAHTg1OwfXo3koUeO_IsHRjnvXsAcjYaY9w')

# Initialize Aliexpress API with USD currency
aliexpress = AliexpressApi('508800', 'TK2sfsvmmxQ89nS4oV9i7AX8OJM8XEH6',
                           models.Language.AR, models.Currency.USD, 'telegramBot')

# Your Telegram channel username or ID
CHANNEL_ID = '@ShopAliExpressMaroc'

# Define function to get exchange rate from USD to MAD
def get_usd_to_mad_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        return data['rates']['MAD']
    except Exception as e:
        logger.error(f"Error fetching exchange rate: {e}")
        return None

def get_random_products(n=3):
    keywords = ['electronics', 'fashion', 'home', 'beauty']
    keyword = random.choice(keywords)
    
    try:
        logger.debug(f"Attempting to fetch hot products with keyword: {keyword}")
        # Use the get_hotproducts method to search for products
        search_result = aliexpress.get_hotproducts(
            keywords=keyword,
            page_size=20  # Adjust as needed
        )
        logger.debug(f"Search result: {search_result}")
        
        if search_result and search_result.products:
            return random.sample(search_result.products, min(n, len(search_result.products)))
        else:
            logger.warning("No products found in the search result")
    except Exception as e:
        logger.error(f"Error searching for products: {str(e)}")
    return []

def post_product_to_channel(product):
    logger.info(f"Retrieved product: {product.product_title}")
    message = f"🔥 منتج جديد! 🔥\n\n"
    message += f"📌 {product.product_title}\n\n"
    
    # Get USD price
    price_usd = float(product.target_sale_price)
    
    # Get exchange rate
    usd_to_mad_rate = get_usd_to_mad_rate()
    
    if usd_to_mad_rate:
        # Calculate MAD price
        price_mad = price_usd * usd_to_mad_rate
        message += f"💰 السعر: ${price_usd:.2f} دولار / {price_mad:.2f} درهم\n"
    else:
        message += f"💰 السعر: ${price_usd:.2f} دولار\n"
    
    message += f"⭐ التقييم: {product.evaluate_rate}\n"
    
    # Get affiliate link for the product
    try:
        affiliate_links = aliexpress.get_affiliate_links(product.product_detail_url)
        if affiliate_links and affiliate_links[0].promotion_link:
            message += f"🔗 الرابط: {affiliate_links[0].promotion_link}\n\n"
        else:
            message += f"🔗 الرابط: {product.product_detail_url}\n\n"
    except Exception as e:
        logger.error(f"Error getting affiliate link: {str(e)}")
        message += f"🔗 الرابط: {product.product_detail_url}\n\n"
    
    # Add bot promotion message
    message += "استخدموا بوتنا الرائع للحصول على جميع الروابط والأسعار بسهولة: 🤖 t.me/AliExpressSaverBot\n\n"
    
    message += "@ShopAliExpressMaroc"
    try:
        bot.send_photo(CHANNEL_ID, product.product_main_image_url, caption=message)
        logger.info(f"Posted product: {product.product_title}")
    except Exception as e:
        logger.error(f"Error posting product: {str(e)}")

def post_products_to_channel():
    products = get_random_products(3)
    for product in products:
        post_product_to_channel(product)

if __name__ == "__main__":
    schedule.every(30).minutes.do(post_products_to_channel)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
