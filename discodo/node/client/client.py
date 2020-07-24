import asyncio
from logging import getLogger
from traceback import print_exc

import websockets

from ...utils import EventEmitter
from .gateway import NodeConnection
from .voice_client import VoiceClient

log = getLogger("discodo.client")


class Node:
    def __init__(self, URL=None, password='hellodiscodo', user_id=None, reconnect=True):
        self.ws = None
        self.emitter = EventEmitter()

        self.loop = asyncio.get_event_loop()
        self.user_id = user_id
        self.reconnect = reconnect

        self.URL = URL
        self.password = password

        self.voiceClients = {}
        self.emitter.onAny(self.onAnyEvent)

        self._polling = None
        self.loop.create_task(self.connect())

    async def connect(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()

        self.ws = await NodeConnection.connect(self)

        if not self._polling or self._polling.done():
            self._polling = self.loop.create_task(self.pollingWs())

        if self.user_id:
            await self.send("IDENTIFY", {"user_id": self.user_id})

    async def pollingWs(self):
        while True:
            try:
                Operation, Data = await self.ws.poll()
            except (asyncio.TimeoutError, websockets.ConnectionClosedError):
                if self.ws.closed and self.reconnect:
                    await self.connect()
                    continue

                if self.ws and not self.ws.closed:
                    await self.ws.close()

                self.ws = None
                return
            else:
                log.debug(f"event {Operation} dispatched from websocket with {Data}")

                try:
                    self.emitter.dispatch(Operation, Data)
                except:
                    print_exc()

    def send(self, *args, **kwargs):
        if not self.ws:
            raise ValueError

        return self.ws.send(*args, **kwargs)

    async def onAnyEvent(self, Operation, Data):
        if Operation == "VC_CREATED":
            guild_id = int(Data["guild_id"])
            self.voiceClients[guild_id] = VoiceClient(self, guild_id)

        if Data and isinstance(Data, dict) and "guild_id" in Data:
            vc = self.getVC(Data["guild_id"])
            if vc:
                vc.emitter.dispatch(Operation, Data)

        if Operation == "VC_DESTROYED":
            guild_id = int(Data["guild_id"])
            if guild_id in self.voiceClients:
                self.voiceClients[guild_id].__del__()

    def getVC(self, guildID):
        return self.voiceClients.get(int(guildID))

    async def discordDispatch(self, payload):
        if not payload["t"] in [
            "READY",
            "RESUME",
            "VOICE_STATE_UPDATE",
            "VOICE_SERVER_UPDATE",
        ]:
            return

        return await self.send("DISCORD_EVENT", payload)

    async def getStat(self):
        await self.send("GET_STAT", None)

        return await self.emitter.wait_for("STAT")
