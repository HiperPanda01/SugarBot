import discord
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True

def load_config():
    with open("data.json", "r") as f:
        return json.load(f)
    
def save_config(config):
    with open("data.json", 'w') as f:
        json.dump(config, f, indent=4)

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(name="ban_emoji", description="Set the emoji to auto-remove when someone reacts with it.")
@discord.app_commands.describe(emoji="The emoji to remove (type or paste it)")
async def setemoji(interaction: discord.Interaction, emoji: str):
    data = load_config()
    for server in data['servers']:
        if server['server_id'] == str(interaction.guild_id) and emoji not in server['banned_reactions']:
            server['banned_reactions'].append(emoji)
    save_config(data)
    await interaction.response.send_message(f"✅ The emoji `{emoji}` will now be removed from reactions.", ephemeral=False)

@tree.command(name="set_reaction_ban_channel", description="Add a channel in which the reaction ban applies.")
@discord.app_commands.describe(channel="Channel ID")
async def reaction_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    data = load_config()
    for server in data['servers']:
        if server['server_id'] == str(interaction.guild_id):
            channel_id_str = str(channel.id)
            if channel_id_str not in server['reaction_channels']:
                server['reaction_channels'].append(channel_id_str)
    save_config(data)
    await interaction.response.send_message(f"✅ The channel {channel.mention} is now in the scope of the reaction bans.", ephemeral=False)

@client.event
async def on_guild_join(guild):
    data = load_config()
    if not any(server['server_id'] == str(guild.id) for server in data['servers']):
        new_entry = {
            "server_id": str(guild.id),
            "banned_reactions": [],
            "reaction_channels": [],
            "reply_channels": []
        }
        data['servers'].append(new_entry)
        save_config(data)

@client.event
async def on_guild_remove(guild):
    data = load_config()
    data['servers'] = [server for server in data['servers'] if server["server_id"] != str(guild.id)]
    save_config(data)

@client.event
async def on_ready():
    await tree.sync()
    activity = discord.Activity(type=discord.ActivityType.watching, name="Watching over Discord kingdoms.")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print(f'We have logged in as {client.user}')

@client.event
async def on_reaction_add(reaction, user):
    member = await reaction.message.guild.fetch_member(user.id)
    if member.guild_permissions.manage_guild:
        return
    data = load_config()
    for server in data['servers']:
        if server['server_id'] == str(reaction.message.guild.id) and str(reaction.emoji) in server['banned_reactions'] and str(reaction.message.channel.id) in server['reaction_channels']:
            await reaction.remove(user)

client.run(os.getenv('DISCORD_TOKEN')) 








