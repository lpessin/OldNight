import discord
from oldnight import Stream

# discord.py Client instance
Client = discord.Client()

# oldnight.py Stream instance
stream = Stream()


@Client.event
async def on_ready():
    """
        Login check

    """
    print('We have logged in as {0.user}'.format(Client))


async def run_stream():
    """
        This will turn on the stream and deliver notifications as new comments arrives.

    """
    await Client.wait_until_ready()

    while not Client.is_closed():
        for item in stream.get_comments(sleep=35):
            timestamp = item[0]
            claim = item[2]
            author = item[1]
            content = item[3]
            discord_ids = item[4]
            embed = discord.Embed(title="Old Night",
                                  description=f"Someone is talking to you:\n{author}\n\n",
                                  color=0xEE8700)
            embed.set_thumbnail(url=Client.user.avatar_url_as(format='png'))
            embed.add_field(name=f"{claim}", value=f"{timestamp}\n{content}")
            if isinstance(discord_ids, list):
                for discord_id in discord_ids:
                    discord_id = int(discord_id)
                    target = Client.get_user(discord_id)
                    await target.send(embed=embed)
            if isinstance(discord_ids, str):
                discord_ids = int(discord_ids)
                target = Client.get_user(discord_ids)
                await target.send(embed=embed)

# Run background loop
Client.loop.create_task(run_stream())


# Run discord Client
Client.run('NjczNzI1Njg1OTUyNTQ0NzY4.XjeOXA.lXXnGRVWUqmN5T5vn03zcGkmWG0')
