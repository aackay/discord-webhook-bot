import os
from tinydb import TinyDB, Query
import discord
from discord_webhook import DiscordWebhook
import json

db = TinyDB('db.json')

with open("whitelist.json", "r") as f:
	whitelisted_ids = json.loads(f.read())

with open("config.json", "r") as f:
	config = json.loads(f.read())
	
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def get_channel_webhook(channel):
	hook_channel = Query()
	if not (db.contains(hook_channel.channel_id == channel.id)):
		webhook_url = (await channel.create_webhook(name="just a webhook dw about it")).url
		db.insert({'channel_id': channel.id, 'webhook_URL': webhook_url})
		print("created webhook")
	else:
		webhook_url = db.get(hook_channel.channel_id == channel.id)["webhook_URL"]
		print("fetched webhook")

	print(webhook_url)
	return webhook_url

@client.event
async def on_ready():
	print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
	if not message.author.id in whitelisted_ids:
		return

	await message.delete()
	url = await get_channel_webhook(message.channel)
	webhook = DiscordWebhook(url=url, content=message.content, username=config["username"], avatar_url=config["avatar_url"])
	response = webhook.execute()

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')

client.run(os.environ['token'])
