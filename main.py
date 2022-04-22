import discord
from discord.ext import commands
import requests
import json
import io
import os
import qrcode
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
bot = commands.Bot(command_prefix="&")


@bot.event
async def on_ready():
    print(">> Bot is online <<")


@bot.command()
async def image(ctx, msg):
    try:
        if len(msg) == 4:
            deck_code_url = f"https://shadowverse-portal.com/api/v1/deck/import?format=json&deck_code={msg}"
            deck_detal = requests.get(deck_code_url)

            deck_hash = json.loads(deck_detal.text)["data"]["hash"]
        else:
            deck_hash = msg.split("?")[0].split("/")[-1]
        deck_image = "https://shadowverse-portal.com/image/1?lang=zh-tw"
        hash_url = f"https://shadowverse-portal.com/deck/{deck_hash}"
        image = requests.get(deck_image, headers={"referer": hash_url})
        if b"<!DOCTYPE html>" in image.content:
            hash_url = f"https://shadowverse-portal.com/deck_co/{deck_hash}"
            image = requests.get(deck_image, headers={"referer": hash_url})
        pic = discord.File(fp=io.BytesIO(image.content), filename="image.png")
        await ctx.send(file=pic)
    except:
        await ctx.send("error")


@bot.command()
async def code(ctx, msg):
    hash_code = msg.split("?")[0].split("/")[-1]
    reqUrl = (
        "https://shadowverse-portal.com/api/v1/deck_code/publish?format=json&lang=zh-tw"
    )

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.io)",
        "Content-Type": "multipart/form-data; boundary=kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A",
    }

    payload = f'--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name="hash"\r\n\r\n{hash_code}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name="csrf_token"\r\n\r\n\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n'

    response = requests.request("POST", reqUrl, data=payload, headers=headersList)
    data = json.loads(response.text)
    try:
        await ctx.send(f'deck_code = {data["data"]["deck_code"]}')
    except:
        await ctx.send("error")


@bot.command()
async def qr(ctx, msg):
    try:
        if len(msg) == 4:
            reqUrl = f"https://shadowverse-portal.com/api/v1/deck/import?format=json&deck_code={msg}"
            json_obj = json.loads(requests.request("GET", reqUrl).text)
            deck_hash = json_obj["data"]["hash"]
            sub_clan = json_obj["data"]["sub_clan"]
            if sub_clan == 0:
                hash_url = f"https://shadowverse-portal.com/deck/{deck_hash}?lang=zh-tw"
            else:
                hash_url = (
                    f"https://shadowverse-portal.com/deck_co/{deck_hash}?lang=zh-tw"
                )
        else:
            hash_url = msg
        img = qrcode.make(hash_url)
        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename="image.png"))
    except:
        await ctx.send("error")

if __name__ == "__main__":
    bot.run(os.getenv('BOT_KEY'))
