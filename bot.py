import telebot
import requests
import json
import logging
import os
from typing import Dict, Optional
from config import Config
from utils import is_valid_url, format_file_size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BestDebridBot:
    def __init__(self):
        self.bot = telebot.TeleBot(Config.BOT_TOKEN)
        self.user_ips: Dict[int, str] = {}
        self.setup_handlers()

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        return user_id in Config.AUTHORIZED_USERS

    def get_user_ip(self, user_id: int) -> Optional[str]:
        """Get stored IP for user"""
        return self.user_ips.get(user_id)

    def unrestrict_link(self, hoster_link: str, client_ip: str) -> dict:
        """Call BestDebrid API to unrestrict a link"""
        try:
            url = "https://bestdebrid.com/api/v1/generateLink"

            params = {'auth': Config.BESTDEBRID_API_KEY}
            data = {'link': hoster_link, 'ip': client_ip}

            response = requests.post(url, params=params, data=data, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": 1, "message": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": 1, "message": "Invalid API response"}

    def setup_handlers(self):
        """Setup all message handlers"""

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            user_id = message.from_user.id

            if not self.is_authorized(user_id):
                self.bot.reply_to(
                    message, 
                    "❌ <b>Access Denied</b>\nYou are not authorized to use this bot.",
                    parse_mode='HTML'
                )
                return

            help_text = """
🔗 <b>Debrid Link Generator Bot by @medusaXD</b>

<b>Available Commands:</b>
• <code>/set_ip &lt;IP_ADDRESS&gt;</code> - Set your IP address
• <code>/gen &lt;LINK&gt;</code> - Generate direct download link
• <b>Send any link directly</b> - Bot will automatically process it

<b>Example Usage:</b>
• <code>/set_ip your_ip</code>
• <code>/gen https://rapidgator.net/file/...</code>

<b>Supported Hosters:</b>
<i>RapidGator, Uploaded, 1fichier, Turbobit, and many more!</i>

ℹ️ <b>Note:</b> You must set your IP address first using <code>/set_ip</code>
            """

            self.bot.reply_to(message, help_text, parse_mode='HTML')

        @self.bot.message_handler(commands=['set_ip'])
        def set_ip_command(message):
            user_id = message.from_user.id

            if not self.is_authorized(user_id):
                self.bot.reply_to(
                    message, 
                    "❌ <b>Access Denied</b>\nYou are not authorized to use this bot. Contact @medusaXD",
                    parse_mode='HTML'
                )
                return

            try:
                command_parts = message.text.split()
                if len(command_parts) != 2:
                    self.bot.reply_to(
                        message, 
                        "❌ <b>Invalid Usage</b>\nPlease use: <code>/set_ip &lt;IP_ADDRESS&gt;</code>\n\n<b>Example:</b> <code>/set_ip 88.209.137.26</code>",
                        parse_mode='HTML'
                    )
                    return

                ip_address = command_parts[1]

                # Basic IP validation
                if not ip_address.replace('.', '').replace(':', '').isalnum():
                    self.bot.reply_to(
                        message, 
                        "❌ <b>Invalid IP Address</b>\nPlease provide a valid IP address.",
                        parse_mode='HTML'
                    )
                    return

                self.user_ips[user_id] = ip_address

                self.bot.reply_to(
                    message, 
                    f"✅ <b>IP Address Set Successfully</b>\nYour IP: <code>{ip_address}</code>\n\nYou can now use <code>/gen</code> command or send links directly!",
                    parse_mode='HTML'
                )

            except Exception as e:
                logger.error(f"Error in set_ip_command: {e}")
                self.bot.reply_to(
                    message, 
                    "❌ <b>Error</b>\nFailed to set IP address. Please try again."
                )

        @self.bot.message_handler(commands=['gen'])
        def generate_link_command(message):
            user_id = message.from_user.id

            if not self.is_authorized(user_id):
                self.bot.reply_to(
                    message, 
                    "❌ <b>Access Denied</b>\nYou are not authorized to use this bot. Contact @medusaXD",
                    parse_mode='HTML'
                )
                return

            client_ip = self.get_user_ip(user_id)
            if not client_ip:
                self.bot.reply_to(
                    message, 
                    "❌ <b>IP Not Set</b>\nPlease set your IP address first using <code>/set_ip &lt;IP_ADDRESS&gt;</code>",
                    parse_mode='HTML'
                )
                return

            try:
                command_parts = message.text.split(' ', 1)
                if len(command_parts) != 2:
                    self.bot.reply_to(
                        message, 
                        "❌ <b>Invalid Usage</b>\nPlease use: <code>/gen &lt;LINK&gt;</code>\n\n<b>Example:</b> <code>/gen https://rapidgator.net/file/...</code>",
                        parse_mode='HTML'
                    )
                    return

                hoster_link = command_parts[1].strip()

                if not is_valid_url(hoster_link):
                    self.bot.reply_to(
                        message, 
                        "❌ <b>Invalid URL</b>\nPlease provide a valid HTTP/HTTPS URL.",
                        parse_mode='HTML'
                    )
                    return

                processing_msg = self.bot.reply_to(
                    message, 
                    "🔄 <b>Processing Link...</b>\nPlease wait while I generate your direct download link.",
                    parse_mode='HTML'
                )

                result = self.unrestrict_link(hoster_link, client_ip)

                try:
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                except:
                    pass

                if result['error'] == 0:
                    response_text = f"""
✅ <b>Link Generated Successfully! by @medusaXD</b>

📁 <b>Filename:</b> <code>{result.get('filename', 'N/A')}</code>
📊 <b>Size:</b> <code>{result.get('size', 'N/A')}</code>
🌐 <b>Hoster:</b> <code>{result.get('hoster', 'N/A')}</code>

🔗 <b>Direct Download Link:</b>
<pre>{result['link']}</pre>
                    """

                    if 'streammp4' in result:
                        response_text += f"\n🎥 <b>Stream MP4:</b> <pre>{result['streammp4']}</pre>"
                    if 'mp3' in result:
                        response_text += f"\n🎵 <b>Audio (MP3):</b> <pre>{result['mp3']}</pre>"

                    self.bot.reply_to(message, response_text, parse_mode='HTML')
                else:
                    self.bot.reply_to(
                        message, 
                        f"❌ <b>Error:</b> {result.get('message', 'Unknown error occurred')}",
                        parse_mode='HTML'
                    )

            except Exception as e:
                logger.error(f"Error in generate_link_command: {e}")
                self.bot.reply_to(
                    message, 
                    "❌ <b>Error</b>\nFailed to process your request. Please try again.",
                    parse_mode='HTML'
                )

        @self.bot.message_handler(func=lambda message: True)
        def handle_direct_links(message):
            user_id = message.from_user.id

            if not self.is_authorized(user_id):
                return

            text = message.text or ""
            if not is_valid_url(text.strip()):
                return

            client_ip = self.get_user_ip(user_id)
            if not client_ip:
                self.bot.reply_to(
                    message, 
                    "❌ <b>IP Not Set</b>\nPlease set your IP address first using <code>/set_ip &lt;IP_ADDRESS&gt;</code>",
                    parse_mode='HTML'
                )
                return

            try:
                hoster_link = text.strip()

                processing_msg = self.bot.reply_to(
                    message, 
                    "🔄 <b>Auto-Processing Link...</b>\nDetected URL in your message. Generating direct download link...",
                    parse_mode='HTML'
                )

                result = self.unrestrict_link(hoster_link, client_ip)

                try:
                    self.bot.delete_message(message.chat.id, processing_msg.message_id)
                except:
                    pass

                if result['error'] == 0:
                    response_text = f"""
✅ <b>Auto-Generated Link! @medusaXD</b>

📁 <b>Filename:</b> <code>{result.get('filename', 'N/A')}</code>
📊 <b>Size:</b> <code>{result.get('size', 'N/A')}</code>
🌐 <b>Hoster:</b> <code>{result.get('hoster', 'N/A')}</code>

🔗 <b>Direct Download Link:</b>
<pre>{result['link']}</pre>
                    """

                    if 'streammp4' in result:
                        response_text += f"\n🎥 <b>Stream MP4:</b> <pre>{result['streammp4']}</pre>"
                    if 'mp3' in result:
                        response_text += f"\n🎵 <b>Audio (MP3):</b> <pre>{result['mp3']}</pre>"

                    self.bot.reply_to(message, response_text, parse_mode='HTML')
                else:
                    self.bot.reply_to(
                        message, 
                        f"❌ <b>Auto-Processing Failed:</b> {result.get('message', 'Unknown error occurred')}",
                        parse_mode='HTML'
                    )

            except Exception as e:
                logger.error(f"Error in handle_direct_links: {e}")
                self.bot.reply_to(
                    message, 
                    "❌ <b>Auto-Processing Error</b>\nFailed to process your link automatically.",
                    parse_mode='HTML'
                )

        @self.bot.message_handler(commands=['status'])
        def status_command(message):
            user_id = message.from_user.id

            if not self.is_authorized(user_id):
                self.bot.reply_to(message, "❌ <b>Access Denied</b>", parse_mode='HTML')
                return

            client_ip = self.get_user_ip(user_id)
            ip_status = f"✅ Set: <code>{client_ip}</code>" if client_ip else "❌ Not Set"

            status_text = f"""
📊 <b>Bot Status</b>

👤 <b>User ID:</b> <code>{user_id}</code>
🌐 <b>IP Address:</b> {ip_status}
🔑 <b>API:</b> Connected to BestDebrid
⚡ <b>Status:</b> Online &amp; Ready

💡 <b>Tip:</b> Use <code>/set_ip</code> if IP is not set, then send any hoster link!
            """

            self.bot.reply_to(message, status_text, parse_mode='HTML')

        @self.bot.message_handler(func=lambda message: True, content_types=['document', 'photo', 'video', 'audio', 'voice', 'sticker'])
        def handle_non_text(message):
            user_id = message.from_user.id
            if self.is_authorized(user_id):
                self.bot.reply_to(
                    message, 
                    "ℹ️ <b>Text Links Only</b>\nPlease send text messages containing download links.",
                    parse_mode='HTML'
                )

    def run(self):
        """Start the bot"""
        logger.info("Starting BestDebrid Telegram Bot...")
        logger.info(f"Authorized users: {len(Config.AUTHORIZED_USERS)}")

        try:
            self.bot.infinity_polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            raise

if __name__ == "__main__":
    bot = BestDebridBot()
    bot.run()
