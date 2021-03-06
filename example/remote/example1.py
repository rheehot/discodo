"""

This example isn't recommended in production.
Just use it only to learn the structure.
This code is not perfect and can be complex.

"""


import logging

import discord

import discodo

logging.basicConfig(level=logging.INFO)

app = discord.Client()
Audio = discodo.DPYClient(app)
Audio.register_node("ws://yourwonderfulnode:prettyport", password="hellodiscodo")


@app.event
async def on_ready():
    print("bot is now ready.")


@app.event
async def on_message(message):
    await app.wait_until_ready()

    if message.content.startswith("!join"):
        if not message.author.voice:
            return await message.channel.send("Join the voice channel first.")

        await Audio.connect(message.author.voice.channel)
        return await message.channel.send(
            f"connected to {message.author.voice.channel.mention}."
        )

    if message.content.startswith("!stop"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        await vc.destroy()

        return await message.channel.send(f"player stopped and cleaned the queue.")

    if message.content.startswith("!play"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        Song = await vc.loadSong(message.content[5:].strip())

        if isinstance(Song, list):
            return await message.channel.send(
                f'{len(Song) - 1} songs except {Song[0]["title"]} added.'
            )
        else:
            return await message.channel.send(f'{Song["title"]} added.')

    if message.content.startswith("!skip"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = int(message.content[5:].strip()) if message.content[5:].strip() else 1

        Remain = await vc.skip(offset)

        return await message.channel.send(f"{offset} skipped. {Remain}songs remain")

    if message.content.startswith("!remove"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = int(message.content[7:].strip()) if message.content[7:].strip() else 1

        Data = await vc.remove(offset)

        return await message.channel.send(f'{Data["removed"]["title"]} removed.')

    if message.content.startswith("!volume"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            int(message.content[7:].strip()) if message.content[7:].strip() else 100
        )

        Volume = await vc.setVolume(offset)

        return await message.channel.send(f"set volume to {Volume}%.")

    if message.content.startswith("!crossfade"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            int(message.content[10:].strip()) if message.content[10:].strip() else 10
        )

        Crossfade = await vc.setCrossfade(offset)

        return await message.channel.send(
            f"set crossfade seconds to {Crossfade} seconds."
        )

    if message.content.startswith("!autoplay"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            int(message.content[9:].strip()) if message.content[9:].strip() else "on"
        )
        offset = {"on": True, "off": False}.get(offset, True)

        autoplay = await vc.setAutoplay(offset)

        return await message.channel.send(
            f'auto related play {"enabled" if autoplay else "disabled"}.'
        )

    if message.content.startswith("!repeat"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            int(message.content[7:].strip()) if message.content[7:].strip() else "on"
        )
        offset = {"on": True, "off": False}.get(offset, True)

        repeat = await vc.setRepeat(offset)

        return await message.channel.send(
            f'repeat {"enabled" if repeat else "disabled"}.'
        )

    if message.content.startswith("!np"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        Data = await vc.getState()

        return await message.channel.send(
            f'Now playing: {Data["current"]["title"]} `{Data["position"]["duration"]}:{Data["current"]["duration"]}`'
        )

    if message.content.startswith("!shuffle"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        await vc.shuffle()

        return await message.channel.send("shuffle the queue.")

    if message.content.startswith("!queue"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        State = await vc.getState()
        Queue = await vc.getQueue()
        QueueText = "\n".join(
            [str(Queue.index(Item) + 1) + ". " + Item["title"] for Item in Queue]
        )

        return await message.channel.send(
            f"""
Now playing: {State["current"]["title"]} `{State["position"]["duration"]}:{State["current"]["duration"]}`

{QueueText}
"""
        )

    if message.content.startswith("!bassboost"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            int(message.content[10:].strip()) if message.content[10:].strip() else 0
        )
        filter = discodo.equalizer.bassboost(offset) if offset != 0 else {}

        await vc.setFilter(filter)

        return await message.channel.send(f"set bassboost level {offset}%.")

    if message.content.startswith("!tempo"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = (
            float(message.content[6:].strip()) if message.content[6:].strip() else 1.0
        )

        await vc.setFilter({"atempo": str(offset)})

        return await message.channel.send(f"set tempo to {offset}.")

    if message.content.startswith("!seek"):
        vc = Audio.getVC(message.guild)

        if not vc:
            return await message.channel.send("Please type `!join` first.")

        offset = int(message.content[5:].strip()) if message.content[5:].strip() else 1

        await vc.seek(offset)

        return await message.channel.send(f"seek to {offset}.")


app.run("SUPERRRSECRETTOKENNNNNN")
