import os
import aiohttp
import datetime
from typing import Optional
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils
from utils.views import PaginatedHelpCommand

TOKEN = os.getenv('BOT_TOKEN')


class Scoala(commands.Bot):
    def __init__(self):
        super().__init__(
            max_messages=100000,
            help_command=PaginatedHelpCommand(),
            command_prefix=('!', '?', '.'),
            strip_after_prefix=True,
            case_insensitive=True,
            intents=disnake.Intents.all(),
            allowed_mentions=disnake.AllowedMentions(
                roles=False, everyone=False, users=True
            ),
            test_guilds=[983594507020951554]
        )
        self._owner_id = 938097236024360960

        self.execs = {}

        self.load_extension('jishaku')
        os.environ['JISHAKU_NO_DM_TRACEBACK'] = '1'
        os.environ['JISHAKU_FORCE_PAGINATOR'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK'] = '1'
        os.environ['JISHAKU_EMBEDDED_JSK_COLOR'] = 'blurple'

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')

        for filename in os.listdir('./reload_cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'reload_cogs.{filename[:-3]}')

    @property
    def _owner(self) -> disnake.User:
        if self._owner_id:
            return self.get_user(self._owner_id)

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        if not hasattr(self, '_session'):
            self._session = aiohttp.ClientSession(loop=self.loop)

        if not hasattr(self, '_presence_changed'):
            activity = disnake.Activity(type=disnake.ActivityType.watching, name='you study | !comenzi')
            await self.change_presence(status=disnake.Status.dnd, activity=activity)
            self._presence_changed = True

        print('Bot is ready!')

    async def process_commands(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def get_webhook(
        self,
        channel: disnake.TextChannel,
        *,
        name: str = "Școală",
        avatar: disnake.Asset = None,
    ) -> disnake.Webhook:
        """Returns the general bot hook or creates one."""

        webhooks = await channel.webhooks()
        webhook = disnake.utils.find(lambda w: w.name and w.name.lower() == name.lower(), webhooks)

        if webhook is None:
            webhook = await channel.create_webhook(
                name=name,
                avatar=await avatar.read() if avatar else None,
                reason="Used ``get_webhook`` but webhook didn't exist",
            )

        return webhook

    async def reference_to_message(
        self, reference: disnake.MessageReference
    ) -> Optional[disnake.Message]:
        if reference._state is None or reference.message_id is None:
            return None

        channel = reference._state.get_channel(reference.channel_id)
        if channel is None:
            return None

        if not isinstance(channel, (disnake.TextChannel, disnake.Thread)):
            return None

        try:
            return await channel.fetch_message(reference.message_id)
        except disnake.NotFound:
            return None

    async def inter_reraise(self, inter, item: disnake.ui.Item, error):
        disagree = '<:disagree:938412196663271514>'
        get_error = "".join(format_exception(error, error, error.__traceback__))
        em = disnake.Embed(description=f'```py\n{get_error}\n```')
        await self._owner.send(
            content="**An error occurred with a view for the user "
                    f"`{inter.author}` (**{inter.author.id}**), "
                    "here is the error:**\n"
                    f"`View:` **{item.view.__class__}**\n"
                    f"`Item Type:` **{item.type}**\n"
                    f"`Item Row:` **{item.row or '0'}**",
            embed=em
        )
        fmt = f'> {disagree} An error occurred'
        if inter.response.is_done():
            await inter.followup.send(fmt, ephemeral=True)
        else:
            await inter.response.send_message(fmt, ephemeral=True)

    async def get_context(self, message, *, cls=utils.Context):
        return await super().get_context(message, cls=cls)


Scoala().run(TOKEN)
