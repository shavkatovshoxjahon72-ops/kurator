import re
import pytesseract
from PIL import Image
from telethon import TelegramClient, events, errors
from sympy import sympify
from sympy.core.sympify import SympifyError
import asyncio
import os

channel_username = 'izatlox1'

# Tesseract yo'lini sozlash (serverda bo'lmasa olib tashlash mumkin)
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

accounts = [

    {"session": "account1", "api_id": 29183260, "api_hash": "3e5ece984e7df9cc5780f3f5731fabcf", "message": "1351342197"},
    {"session": "account32", "api_id": 29183260, "api_hash": "3e5ece984e7df9cc5780f3f5731fabcf", "message": "1351334703"},
    {"session": "account33", "api_id": 29183261, "api_hash": "3e5ece984e7df9cc5780f3f5731fabca", "message": "1351335267"},
    {"session": "account35", "api_id": 29669738, "api_hash": "d480c63bb0308c784c66148ddf2964be", "message": "1351335907"},
    {"session": "account36", "api_id": 26781933, "api_hash": "c6778de80590bdd2e5a48b8a82e1f0d8", "message": "1351336445"},
    {"session": "account37", "api_id": 21389183, "api_hash": "9fb3b8614540338dde990192a9727965", "message": "1351337225"},
    {"session": "account38", "api_id": 25329833, "api_hash": "a9f0de2cd34383f0394671f5bda230e1", "message": "1351338033"},
    {"session": "account39", "api_id": 24570607, "api_hash": "7edf55c9745bf9fb39c1fca0495c5f1a", "message": "1351338943"},
    {"session": "account40", "api_id": 13077838, "api_hash": "0cc439b15d37530865711b6af55e69ff", "message": "1351339867"},
    {"session": "account41", "api_id": 27349823, "api_hash": "1fe08a0904aef83c94ff96d6417708ed", "message": "1351340629"},
    {"session": "account42", "api_id": 21324381, "api_hash": "a17e0edd6aedb523ebcf480af199d8f3", "message": "1351341421"},
  ]

clients = []

def extract_expression(text):
    text = re.sub(r'(?<=\d)\s*[xX]\s*(?=\d)', '*', text)
    pattern = r'[\d\s\+\-\*/\^\(\)]+'
    matches = re.findall(pattern, text)
    if matches:
        for m in matches:
            clean = m.strip()
            if clean.isdigit():
                continue
            if any(op in clean for op in ['+', '-', '*', '/', '^']):
                return clean
    return None

async def handle_event(client):
    @client.on(events.NewMessage(chats=channel_username))
    async def handler(event):
        raw_text = event.raw_text

        if raw_text.strip():
            expr = extract_expression(raw_text)
        else:
            file_path = await event.download_media()
            if file_path:
                try:
                    img = Image.open(file_path)
                    raw_text = pytesseract.image_to_string(img)
                    expr = extract_expression(raw_text)
                finally:
                    os.remove(file_path)
            else:
                expr = None

        if not expr:
            print(f"[{client.session.filename}] ℹ️ Matematik ifoda topilmadi.")
            return

        try:
            result = sympify(expr)
            await client.send_message(
                entity=channel_username,
                message=f"{result}",
                comment_to=event.id
            )
            print(f"[{client.session.filename}] ✅ Izoh yuborildi: {expr} = {result}")
        except SympifyError:
            print(f"[{client.session.filename}] ❌ Noto‘g‘ri ifoda: {expr}")
        except Exception as e:
            print(f"[{client.session.filename}] ⚠️ Xatolik: {e}")

async def check_subscription(client, interval=60):
    """Har interval sekundda kanalga obuna bo‘lishini tekshiradi"""
    while True:
        try:
            participant = await client.get_participant(channel_username, 'me')
            if participant:
                print(f"[{client.session.filename}] ✅ Kanalga obuna bo‘lingan")
        except errors.UserNotParticipantError:
            print(f"[{client.session.filename}] ❌ Kanalga obuna emas")
        except Exception as e:
            print(f"[{client.session.filename}] ⚠️ Xatolik obuna tekshirishda: {e}")
        await asyncio.sleep(interval)
async def start_client(acc):
    client = TelegramClient(acc['session'], acc['api_id'], acc['api_hash'])
    await client.start()
    await handle_event(client)
    # Har 60 soniyada obuna tekshiruvchi task
    asyncio.create_task(check_subscription(client))
    print(f"🔗 {acc['session']} ulandi va obuna tekshirish boshlandi.")
    return client

async def main():
    global clients
    clients = await asyncio.gather(*(start_client(acc) for acc in accounts))
    print("🤖 Hammasi ishga tushdi. Kanal kuzatilyapti...")
    await asyncio.gather(*(client.run_until_disconnected() for client in clients))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



