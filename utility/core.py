import discord
import datetime
import humanize
import time
import pkg_resources

from tabulate import tabulate
from lavalink import node
from redbot.core import commands
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import (
    box
)


async def parse_llnode_stat(stats: node.NodeStats, stat_name: str):
    stat = getattr(stats, stat_name)
    if isinstance(stat, int) and stat_name.startswith("memory_"):
        stat = humanize.naturalsize(stat, binary=True)
    if stat_name == "uptime":
        stat = chat.humanize_timedelta(seconds=stat / 1000)
    if "load" in stat_name:
        stat = f"{round(stat*100, 2)} %"
    return stat


class Utility(commands.Cog):
    """Utility commands to use."""

    __version__ = "1.4.4"
    __author__ = ["MAX", "Fixator10"]

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nAuthors: {', '.join(self.__author__)}\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def statsinfo(self, ctx):
        """Shows some stats for [botname]."""
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        version = pkg_resources.get_distribution("discord.py").version
        servers = str(len(self.bot.guilds))
        users = str(len(self.bot.users))
        emb = discord.Embed(
            title=f"Botstats for {self.bot.user.name}:", color=await ctx.embed_color()
        )
        emb.add_field(
            name="Users:",
            value=(
                f"{servers} servers\n{total_members} total members\n{total_unique} unique members"
            ),
            inline=True,
        )
        emb.add_field(
            name="Channels:",
            value=(f"{text + voice} total\n{text} text\n{voice} voice"),
            inline=True,
        )
        emb.set_footer(text=f"Discord.py v{version}")
        emb.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=emb)

    @commands.command(aliases=["cmdstats"])
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def cmdstat(self, ctx):
        """Shows how many commands available on [botname]
        
        This only shows from cogs loaded."""
        commands = len(set(self.bot.walk_commands()))

        emb = discord.Embed(
            title=f"cmdstat on {self.bot.user.name}", color=await ctx.embed_color()
        )
        emb.add_field(name="Commands available:", value=commands, inline=True)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.is_owner()
    async def llnodestats(self, ctx):
        """Lavalink nodestats.
        
        This require audio loaded before you using this command."""
        nodes = node.get_nodes_stats()
        if not nodes:
            await ctx.send(chat.info("No nodes found. This require audio loaded and wait for lavalink to connect for this to work."))
            return
        stats = [stat for stat in dir(nodes[0]) if not stat.startswith("_")]
        tabs = []
        for i, n in enumerate(nodes, start=1):
            tabs.append(
                f"Node {i}/{len(nodes)}\n"
                + chat.box(
                    tabulate(
                        [
                            (
                                stat.replace("_", " ").title(),
                                await parse_llnode_stat(n, stat),
                            )
                            for stat in stats
                        ],
                    ),
                    "ml",
                )
            )
        await menu(ctx, tabs, DEFAULT_CONTROLS)

    @commands.command(hidden=True) # hidden to avoide being used for spam which it's not made for.
    @commands.guild_only()
    @commands.cooldown(1, 500, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def commands(self, ctx):
        """This will show where commands are for [botname]."""
        if ctx.channel.permissions_for(ctx.me).embed_links:
            embed = discord.Embed(
                description=f"Use `{ctx.clean_prefix}help` to see all my commands.",
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"> Use `{ctx.clean_prefix}help` to see all my commands.")
