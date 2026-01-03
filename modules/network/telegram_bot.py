#!/usr/bin/env python3
"""Telegram Bot Stub"""
import os

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    def send(self, msg):
        print(f"[TG] {msg}")
        return True
