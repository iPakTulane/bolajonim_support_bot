import logging
import smtplib
from email.mime.text import MIMEText

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def send_email(subject, body):
    """Sends an email using the configured Outlook account."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.OUTLOOK_EMAIL
    msg["To"] = config.OUTLOOK_EMAIL

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(config.OUTLOOK_EMAIL, config.OUTLOOK_PASSWORD)
            server.sendmail(config.OUTLOOK_EMAIL, [config.OUTLOOK_EMAIL], msg.as_string())
        logger.info(f"Email sent successfully to {config.OUTLOOK_EMAIL}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Welcome to the Bolajonim Support Bot! Send me a message and I will forward it to our support team.")


async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forwards user messages to the support email."""
    user = update.message.from_user
    user_info = f"User: {user.full_name} (@{user.username}, ID: {user.id})"
    message_text = update.message.text

    subject = f"New message from {user.full_name}"
    body = f"{user_info}\n\nMessage:\n{message_text}"

    send_email(subject, body)

    await update.message.reply_text("Your message has been forwarded to our support team. We will get back to you shortly.")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    application.run_polling()


if __name__ == "__main__":
    main()
