from aiohttp import ClientSession
from traceback import format_exception

import disnake
from disnake.ext import commands

import utils

__all__ = ('Context',)


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self) -> ClientSession:
        return self.bot.session

    @disnake.utils.cached_property
    def replied_reference(self) -> disnake.MessageReference | None:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, disnake.Message):
            return ref.resolved.to_reference()
        return None

    async def trigger_typing(self) -> None:
        try:
            channel = await self._get_channel()
            await self._state.http.send_typing(channel.id)
        except disnake.Forbidden:
            pass

    async def better_reply(self, *args, **kwargs) -> disnake.Message:
        if self.replied_reference is not None:
            try:
                del kwargs['reference']
            except KeyError:
                pass
            return await self.send(*args, reference=self.replied_reference, **kwargs)
        else:
            return await super().reply(*args, **kwargs)

    async def check_channel(self) -> bool:
        if self.channel.id not in (
            983612117158600714, 983596968456618004
        ) \
                and self.author.id != 938097236024360960:
            await utils.try_delete(self.message, delay=10.0)
            await self.reply(
                'Scuze! Această comandă poate fi folosită numai în <#983612117158600714>',
                delete_after=10.0
            )
            return False
        return True

    async def check_perms(
        self,
        member: disnake.Member,
        *,
        reason: str = 'Acest membru are același statut ca tine, sau mai mare.'
    ) -> bool:
        if self.author.id == 938097236024360960:
            return True
        elif self.author.top_role <= member.top_role:
            await self.reply(f'{reason}')
            return False
        return True

    async def reraise(self, error):
        if isinstance(error, commands.NotOwner):
            await self.reply(
                'Nu poți folosi această comandă deoarece nu deții acest bot.',
                delete_after=8
            )
            await utils.try_delete(self.message, delay=8)
            return

        elif isinstance(error, commands.CommandOnCooldown):
            if error.retry_after > 60.0:
                time = utils.time_phaser(error.retry_after)
            else:
                time = f'{error.retry_after:.2f} secunde'
            return await self.reply(
                f'Ești in cooldown, mai ai **`{time}`**.'
            )

        elif isinstance(error, commands.DisabledCommand):
            self.command.reset_cooldown(self)
            return await self.reply('Această comandă este dezactivată!')

        elif isinstance(error, commands.MaxConcurrencyReached):
            await utils.try_delete(self.message, delay=5.0)
            await self.reply(
                'Deja folosești această comandă.',
                delete_after=5.0
            )
            return

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            _missing_args = list(self.command.clean_params)
            missing_args = [f'`{arg}`' for arg in _missing_args[_missing_args.index(error.param.name):]]
            return await self.reply(
                f"Îți lipsesc următorii parametri:\n "
                f"\u2800\u2800{utils.human_join(missing_args, final='și')}\n\n"
                "Dacă nu știi cum se folosește această comandă, scrie "
                f"`!comenzi {self.command.qualified_name}` pentru mai multe informații."
            )

        elif isinstance(error, commands.errors.MemberNotFound):
            await self.reply("Nu s-a putut găsi acel membru.")
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.errors.UserNotFound):
            await self.reply("Nu s-a putut găsi acel user.")
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.errors.CheckFailure):
            self.command.reset_cooldown(self)
            return

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            self.command.reset_cooldown(self)
            return await self.reply(f'Îți lipsește `{error.close_quote}` la sfârșit.')

        elif isinstance(error, commands.InvalidEndOfQuotedStringError):
            self.command.reset_cooldown(self)
            return await self.reply(f'Îți lipsește un spațiu după ghilimele, nu `{error.char}`')

        elif (
            isinstance(error, commands.TooManyArguments) or
            isinstance(error, commands.BadArgument) or
            isinstance(error, commands.CommandNotFound)
        ):
            return

        else:
            get_error = "".join(format_exception(error, error, error.__traceback__))
            em = disnake.Embed(description=f'```py\n{get_error}\n```')
            await self.bot._owner.send(
                content=f"**An error occurred with the command `{self.command}`, "
                        "here is the error:**",
                embed=em
            )
            await self.reply(
                'A apărut o eroare. Această informație a fost trimisă creatorului meu'
                'pentru a fi rezolvată'
            )
