import csv
import discord
from oldnight import OldNight

# discord.py instance
client = discord.Client()

# oldnight.py OldNight instance
oldnight = OldNight()


def check_id(discord_id):
    with open('channels_list', mode='r') as C:
        reader = csv.reader(C)
        for rows in reader:
            id = rows[0]
            if id == discord_id:
                return True


def add_channel(discord_id, channel):
    with open('channels_list', mode='a', newline='') as C:
        writer = csv.writer(C)
        writer.writerow([discord_id, channel])
        return True


def remove_channel(discord_id):
    with open('channels_list', mode='r') as C:
        rows = []
        read = csv.reader(C)
        for row in read:
            if discord_id != row[0]:
                rows.append(row)
    with open('channels_list', mode='w') as C:
        writer = csv.writer(C)
        for item in rows:
            writer.writerow(item)


@client.event
async def on_ready():
    """
        Login check

    """
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="~oldhelp"))
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        # Prevents reply to it self
        return
    if message.content.startswith('~addchannel'):
        # Deals with channels db
        channel = str(message.content).replace('~addchannel ', '')
        print(channel)
        if channel[0] == '@':
            if oldnight.get_channel_info(channel) is False:
                await message.channel.send(f"Failed: I can't find {channel} channel")
                return
            if check_id(discord_id=str(message.author.id)) is True:
                await message.channel.send('Failed: You already have a channel engaged.')
                await message.channel.send('To stop the service type ~delchannel')
            else:
                add_channel(discord_id=str(message.author.id), channel=channel)
                await message.channel.send("Success: I got you")
                await message.channel.send("To stop the service type ~delchannel")
        else:
            await message.channel.send('Failed:  "@" Must be included')
    if message.content.startswith('~delchannel'):
        remove_channel(discord_id=str(message.author.id))
        await message.channel.send("Success, type ~addchannel <@channel> to restart the service.")
    if message.content.startswith('~lookchannel'):
        channel = str(message.content).replace('~lookchannel ', '')
        if channel[0] == '@':
            data = oldnight.get_channel_info(channel)
            if data is False:
                await message.channel.send(f"Failed: I can't find {channel} channel")
                return
            embed = discord.Embed(title=channel, description="Channel Info", color=0xEE8700)
            if data[20][0] != 'none':
                embed.set_thumbnail(url=data[20][0])
            for item in data:
                if item[0]:
                    embed.add_field(name=item[1], value=item[0], inline=False)
                else:
                    embed.add_field(name=item[1], value='None', inline=False)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send('Failed:  "@" Must be included')
    if message.content.startswith('~lookpub'):
        pub = str(message.content).replace('~lookpub ', '')
        data = oldnight.get_claim_info(pub)
        if data is False:
            await message.channel.send(f"Failed: I can't find {pub}. Try: <<lbry://@Channel#7/your-publish-here#6>> ")
            return
        embed = discord.Embed(title="Look Publish", description=pub, color=0xEE8700)
        if data[15][0] != 'none':
            embed.set_thumbnail(url=data[15][0])
        for item in data:
            if item[0]:
                embed.add_field(name=item[1], value=f"{item[0]}", inline=False)
            else:
                embed.add_field(name=item[1], value='None', inline=False)
        await message.channel.send(embed=embed)
    if message.content.startswith('~trending'):
        tr = str(message.content).replace('~trending ', '')
        data = oldnight.get_claim_info(tr)
        if data is False:
            await message.channel.send(f"Failed: I can't find {tr}. Try: <<lbry://@Channel#7/your-publish-here#6>> ")
            return
        embed = discord.Embed(title="LBRY Trending", description=tr, color=0xEE8700)
        trlist = data[5][0]
        for value in trlist:
            embed.add_field(name=value[1], value=f"{value[0]:.3f}", inline=False)
        await message.channel.send(embed=embed)
    if message.content.startswith('~oldhelp'):
        embed = discord.Embed(title="Old Night", description="Welcome LBRYian! \n"
                                                             "- Add a channel to receive new comments notifications\n"
                                                             "- Look deep inside a publish or a channel\n"
                                                             "- Check Trending Index\n\n",
                              color=0xEE8700)
        embed.set_thumbnail(url=client.user.avatar_url_as(format='png'))
        embed.add_field(name='~addchannel <@channel>', value='This you will turn on the notification service.',
                        inline=False)
        embed.add_field(name='~delchannel', value='This will stop the notification service', inline=False)
        embed.add_field(name='~lookchannel <@channel>', value='Look deep inside a channel', inline=False)
        embed.add_field(name='~lookpub <<lbry://>>', value='Look deep inside a publish')
        embed.add_field(name='~trending <<lbry://>>', value='Check trending index of a publish')
        await message.channel.send(embed=embed)


# Run discord client
client.run('token')
