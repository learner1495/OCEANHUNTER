"""
Telegram Bot — SOCKS5 Proxy Support
For OCEAN HUNTER V10.8.2
"""

import socket
import ssl
import json
import os
import logging
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("TELEGRAM")


class TelegramBot:
    """Telegram Bot via SOCKS5 proxy (Raw Socket)"""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
        self.proxy_port = int(os.getenv("PROXY_PORT", "1080"))
        self.use_proxy = os.getenv("USE_PROXY", "true").lower() == "true"
        self.api_host = "api.telegram.org"

    def _socks5_connect(self, target_host: str, target_port: int) -> socket.socket:
        """Connect via SOCKS5 proxy"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((self.proxy_host, self.proxy_port))

        sock.sendall(b"\x05\x01\x00")
        resp = sock.recv(2)
        if resp != b"\x05\x00":
            raise Exception(f"SOCKS5 handshake failed: {resp.hex()}")

        req = b"\x05\x01\x00\x03"
        req += bytes([len(target_host)]) + target_host.encode()
        req += target_port.to_bytes(2, "big")
        sock.sendall(req)

        resp = sock.recv(10)
        if resp[1] != 0:
            raise Exception(f"SOCKS5 connect failed: code {resp[1]}")

        return sock

    def _direct_connect(self, target_host: str, target_port: int) -> socket.socket:
        """Direct connection without proxy"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((target_host, target_port))
        return sock

    def _request(self, method: str, params: dict = None) -> dict:
        """Send request to Telegram API"""
        params = params or {}
        path = f"/bot{self.token}/{method}"

        if params:
            query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            path = f"{path}?{query}"

        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {self.api_host}\r\n"
        request += "Connection: close\r\n\r\n"

        try:
            if self.use_proxy:
                sock = self._socks5_connect(self.api_host, 443)
            else:
                sock = self._direct_connect(self.api_host, 443)

            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=self.api_host) as ssock:
                ssock.sendall(request.encode())
                response = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk

            text = response.decode("utf-8", errors="ignore")
            if "\r\n\r\n" in text:
                _, body = text.split("\r\n\r\n", 1)
            else:
                body = text

            for line in body.split("\r\n"):
                line = line.strip()
                if line.startswith("{"):
                    return json.loads(line)

            if body.strip().startswith("{"):
                return json.loads(body.strip())

            return {"ok": False, "raw": body[:200]}

        except Exception as e:
            logger.error(f"Telegram request failed: {e}")
            return {"ok": False, "error": str(e)}

    def send_message(self, text: str, chat_id: str = None) -> dict:
        """Send a text message"""
        return self._request("sendMessage", {
            "chat_id": chat_id or self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        })

    def send_alert(self, level: str, message: str) -> dict:
        """Send formatted alert"""
        emojis = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨", "SUCCESS": "✅"}
        emoji = emojis.get(level.upper(), "📌")
        text = f"{emoji} <b>{level.upper()}</b>\n{message}"
        return self.send_message(text)

    def test_connection(self) -> bool:
        """Test if bot can connect"""
        result = self._request("getMe")
        return result.get("ok", False)


_bot_instance = None

def get_bot() -> TelegramBot:
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramBot()
    return _bot_instance

def send_telegram(message: str, level: str = "INFO") -> bool:
    """Quick send function"""
    bot = get_bot()
    result = bot.send_alert(level, message)
    return result.get("ok", False)
