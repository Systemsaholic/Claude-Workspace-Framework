#!/usr/bin/env python3
"""
CLI for managing the Telegram Bridge service.

Usage:
    python cli.py setup-webhook    # Register webhook with Telegram
    python cli.py delete-webhook   # Remove webhook
    python cli.py webhook-info     # Show webhook status
    python cli.py test-message     # Send a test message
    python cli.py bot-info         # Show bot information
    python cli.py run              # Run the service
"""

import argparse
import asyncio

import httpx

from config import get_settings


async def setup_webhook(webhook_url: str = None):
    """Set up the Telegram webhook."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/setWebhook"

    target_url = webhook_url or settings.webhook_url

    payload = {
        "url": target_url,
        "allowed_updates": ["message", "edited_message", "callback_query"],
    }

    if settings.telegram_webhook_secret:
        payload["secret_token"] = settings.telegram_webhook_secret

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        result = response.json()
        print(f"Webhook URL: {target_url}")
        print(f"Result: {result}")
        return result


async def delete_webhook():
    """Delete the Telegram webhook."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/deleteWebhook"

    async with httpx.AsyncClient() as client:
        response = await client.post(url)
        result = response.json()
        print(f"Delete webhook result: {result}")
        return result


async def webhook_info():
    """Get webhook information."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/getWebhookInfo"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        result = response.json()
        print("Webhook Info:")
        if result.get("ok"):
            info = result.get("result", {})
            print(f"  URL: {info.get('url', 'Not set')}")
            print(f"  Pending updates: {info.get('pending_update_count', 0)}")
            print(f"  Last error: {info.get('last_error_message', 'None')}")
            print(f"  Max connections: {info.get('max_connections', 'Default')}")
        else:
            print(f"  Error: {result}")
        return result


async def test_message(message: str = None):
    """Send a test message."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendMessage"

    text = message or "Test message from Telegram Bridge CLI"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "chat_id": settings.telegram_chat_id,
                "text": text,
            },
        )
        result = response.json()
        print(f"Send message result: {result.get('ok', False)}")
        if not result.get("ok"):
            print(f"Error: {result.get('description')}")
        return result


async def bot_info():
    """Get bot information."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/getMe"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        result = response.json()
        print("Bot Info:")
        if result.get("ok"):
            bot = result.get("result", {})
            print(f"  Username: @{bot.get('username')}")
            print(f"  Name: {bot.get('first_name')}")
            print(f"  Bot ID: {bot.get('id')}")
        return result


def run_service():
    """Run the service."""
    from service import main
    main()


def main():
    parser = argparse.ArgumentParser(description="Telegram Bridge CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # setup-webhook
    webhook_parser = subparsers.add_parser("setup-webhook", help="Set up Telegram webhook")
    webhook_parser.add_argument("--url", help="Custom webhook URL")

    # delete-webhook
    subparsers.add_parser("delete-webhook", help="Delete Telegram webhook")

    # webhook-info
    subparsers.add_parser("webhook-info", help="Show webhook information")

    # bot-info
    subparsers.add_parser("bot-info", help="Show bot information")

    # test-message
    test_parser = subparsers.add_parser("test-message", help="Send a test message")
    test_parser.add_argument("--message", "-m", help="Message to send")

    # run
    subparsers.add_parser("run", help="Run the service")

    args = parser.parse_args()

    if args.command == "setup-webhook":
        asyncio.run(setup_webhook(args.url))
    elif args.command == "delete-webhook":
        asyncio.run(delete_webhook())
    elif args.command == "webhook-info":
        asyncio.run(webhook_info())
    elif args.command == "bot-info":
        asyncio.run(bot_info())
    elif args.command == "test-message":
        asyncio.run(test_message(args.message))
    elif args.command == "run":
        run_service()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
