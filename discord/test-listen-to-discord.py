import discord
import discord.discord_config as discord_config


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
@client.event
async def on_message(message):
    my_dev_channel = client.get_channel(discord_config.my_dev_channel)
    if message.author == client.user:
        return

    if message.channel != my_dev_channel:
        return

    print('Message from {0.author}: {0.content}'.format(message))
    f = open("message.txt", "w")
    f.write(message.content.strip())
    f.close()

client.run(discord_config.house_bot_token)
