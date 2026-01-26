"""
Telegram Bridge Service - Full MCP-Enabled 2-Way Conversations

This service enables true 2-way conversations between Telegram and Claude
with FULL access to workspace MCP tools.

Architecture:
    Telegram -> Webhook -> This Service -> Claude API + MCP Tools -> Telegram
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel

from config import get_settings
from mcp_client import MCPManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram-bridge")

# FastAPI app
app = FastAPI(
    title="Telegram Bridge (MCP-Enabled)",
    description="2-way conversation bridge with full MCP tool access",
    version="2.0.0",
)

# MCP Manager - connects to all MCP servers
mcp_manager = MCPManager()

# Conversation history storage (in-memory; use Redis for production)
conversation_history: dict[str, list[dict]] = {}
MAX_HISTORY_LENGTH = 20


class TelegramUpdate(BaseModel):
    """Telegram webhook update model."""
    update_id: int
    message: Optional[dict] = None
    edited_message: Optional[dict] = None
    callback_query: Optional[dict] = None


def get_system_prompt() -> str:
    """Load the system prompt for Claude with MCP context."""
    settings = get_settings()

    # Load CLAUDE.md from workspace if it exists
    claude_md = Path(settings.workspace_path) / "CLAUDE.md"
    context = claude_md.read_text() if claude_md.exists() else ""

    # Or load custom system prompt file
    if settings.system_prompt_file:
        prompt_path = Path(settings.system_prompt_file)
        if prompt_path.exists():
            context = prompt_path.read_text()

    # Get available tools summary
    tools = mcp_manager.get_all_tools()
    tool_summary = "\n".join([f"- {t['name']}: {t['description'][:80]}..." for t in tools[:20]])
    if len(tools) > 20:
        tool_summary += f"\n- ... and {len(tools) - 20} more tools"

    return f"""You are Claude, an AI Assistant communicating via Telegram.

You have access to the following workspace tools:
{tool_summary}

Current date/time: {datetime.now().strftime("%Y-%m-%d %H:%M")}

IMPORTANT GUIDELINES:
1. You CAN and SHOULD use tools to help the user
2. Keep responses concise and mobile-friendly (Telegram)
3. When using tools, briefly explain what you're doing
4. Confirm important actions before executing (especially emails, deletions)

{f"Workspace Context:{chr(10)}{context[:3000]}" if context else ""}
"""


async def send_telegram_message(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    reply_to_message_id: Optional[int] = None,
) -> dict:
    """Send a message via Telegram API."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendMessage"

    max_length = 4000
    chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    messages_sent = []

    async with httpx.AsyncClient() as client:
        for i, chunk in enumerate(chunks):
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": parse_mode,
            }
            if reply_to_message_id and i == 0:
                payload["reply_to_message_id"] = reply_to_message_id

            try:
                response = await client.post(url, json=payload)
                result = response.json()
                if not result.get("ok"):
                    # Retry without parse_mode if markdown fails
                    payload.pop("parse_mode", None)
                    response = await client.post(url, json=payload)
                    result = response.json()
                messages_sent.append(result)
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")

    return messages_sent[-1] if messages_sent else {}


async def send_typing_action(chat_id: str) -> None:
    """Send typing indicator to Telegram."""
    settings = get_settings()
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendChatAction"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "action": "typing"})


async def process_with_claude(chat_id: str, user_message: str) -> str:
    """Process a message through Claude API with MCP tools."""
    settings = get_settings()

    # Get or initialize conversation history
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    history = conversation_history[chat_id]
    history.append({"role": "user", "content": user_message})

    # Trim history if too long
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]
        conversation_history[chat_id] = history

    # Get available tools
    tools = mcp_manager.get_all_tools()

    # Call Claude API
    client = AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())

    try:
        # Initial request
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.max_tokens,
            system=get_system_prompt(),
            messages=history,
            tools=tools if tools else None,
        )

        # Handle tool use loop
        max_iterations = 10
        iteration = 0

        while response.stop_reason == "tool_use" and iteration < max_iterations:
            iteration += 1

            # Extract tool calls
            tool_results = []
            assistant_content = response.content

            for block in assistant_content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    logger.info(f"Calling tool: {tool_name}")

                    # Call the MCP tool
                    try:
                        result = await mcp_manager.call_tool(tool_name, tool_input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": str(result) if result else "Tool executed successfully"
                        })
                    except Exception as e:
                        logger.error(f"Tool error: {e}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })

            # Add assistant message and tool results to history
            history.append({"role": "assistant", "content": assistant_content})
            history.append({"role": "user", "content": tool_results})

            # Continue the conversation
            response = await client.messages.create(
                model=settings.claude_model,
                max_tokens=settings.max_tokens,
                system=get_system_prompt(),
                messages=history,
                tools=tools if tools else None,
            )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        # Add final response to history
        history.append({"role": "assistant", "content": response.content})
        conversation_history[chat_id] = history

        return final_text or "I completed the task but have no text response."

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


async def handle_telegram_message(update: TelegramUpdate) -> None:
    """Handle an incoming Telegram message."""
    message = update.message or update.edited_message
    if not message:
        return

    chat_id = str(message.get("chat", {}).get("id"))
    text = message.get("text", "")
    message_id = message.get("message_id")
    user = message.get("from", {})
    username = user.get("username", user.get("first_name", "User"))

    # Security: Only respond to authorized chat
    settings = get_settings()
    if chat_id != settings.telegram_chat_id:
        logger.warning(f"Unauthorized chat attempt from {chat_id}")
        return

    if not text:
        return

    logger.info(f"Message from {username}: {text[:50]}...")

    # Send typing indicator
    await send_typing_action(chat_id)

    # Handle commands
    if text.startswith("/"):
        if text == "/start":
            tools_count = len(mcp_manager.get_all_tools())
            await send_telegram_message(
                chat_id,
                f"AI Assistant ready!\n\n"
                f"I have access to {tools_count} tools.\n\n"
                f"Just tell me what you need!",
            )
            return
        elif text == "/clear":
            conversation_history[chat_id] = []
            await send_telegram_message(chat_id, "Conversation cleared.", reply_to_message_id=message_id)
            return
        elif text == "/status":
            status = mcp_manager.get_server_status()
            status_text = "MCP Server Status:\n"
            for name, info in status.items():
                emoji = "✅" if info["running"] else "❌"
                status_text += f"• {name}: {emoji} ({info['tools_count']} tools)\n"
            await send_telegram_message(chat_id, status_text)
            return
        elif text == "/tools":
            tools = mcp_manager.get_all_tools()
            tools_text = f"Available Tools ({len(tools)}):\n\n"
            for t in tools[:30]:
                name_parts = t["name"].split("__")
                tool_name = name_parts[1] if len(name_parts) > 1 else t["name"]
                tools_text += f"• {tool_name}\n"
            if len(tools) > 30:
                tools_text += f"\n...and {len(tools) - 30} more"
            await send_telegram_message(chat_id, tools_text)
            return
        elif text == "/help":
            await send_telegram_message(
                chat_id,
                "*AI Assistant*\n\n"
                "Commands:\n"
                "/start - Welcome message\n"
                "/status - MCP server status\n"
                "/tools - List available tools\n"
                "/clear - Clear conversation\n"
                "/help - This help\n\n"
                "Just send any message to chat with me!"
            )
            return

    # Process with Claude + MCP tools
    response = await process_with_claude(chat_id, text)
    await send_telegram_message(chat_id, response, reply_to_message_id=message_id)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming Telegram webhook."""
    settings = get_settings()

    if settings.telegram_webhook_secret:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.telegram_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        data = await request.json()
        update = TelegramUpdate(**data)
        background_tasks.add_task(handle_telegram_message, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "telegram-bridge",
        "mcp_servers": len(mcp_manager.servers),
        "tools_available": len(mcp_manager.get_all_tools()),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Telegram Bridge",
        "version": "2.0.0 (MCP-Enabled)",
        "status": "running",
        "mcp_servers": list(mcp_manager.servers.keys()),
    }


@app.on_event("startup")
async def startup_event():
    """Start MCP servers on startup."""
    logger.info("Starting Telegram Bridge with MCP support...")
    await mcp_manager.start_servers()
    logger.info(f"MCP servers started: {list(mcp_manager.servers.keys())}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop MCP servers on shutdown."""
    logger.info("Shutting down MCP servers...")
    mcp_manager.stop_servers()


def main():
    """Run the service."""
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "service:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
