import discord
from discord.ext import commands
import math
from core.database import database
from core.titles import TITLE_MISSIONS

MISSIONS_PER_PAGE = 5

class MisiView(discord.ui.View):
    def __init__(self, user: discord.Member, stats: dict, fans_count: int, purchased: set):
        super().__init__(timeout=180.0)
        self.user = user
        self.stats = stats
        self.fans_count = fans_count
        self.purchased = purchased
        
        self.all_missions = list(TITLE_MISSIONS.items())
        self.current_page = 1
        self.total_pages = math.ceil(len(self.all_missions) / MISSIONS_PER_PAGE)
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        prev_button = discord.ui.Button(
            emoji="◀️", 
            style=discord.ButtonStyle.secondary, 
            disabled=(self.current_page == 1)
        )
        prev_button.callback = self.prev_page_callback
        self.add_item(prev_button)

        next_button = discord.ui.Button(
            emoji="▶️", 
            style=discord.ButtonStyle.primary, 
            disabled=(self.current_page == self.total_pages)
        )
        next_button.callback = self.next_page_callback
        self.add_item(next_button)

    async def prev_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Ini daftar misi milik orang lain!", ephemeral=True)
            return
        
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Ini daftar misi milik orang lain!", ephemeral=True)
            return
        
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="📜 DAFTAR MISI TITLE KTP MAHA5",
            description=f"Berikut status pencapaian Title untuk {self.user.mention}:\n",
            color=discord.Color.from_rgb(88, 101, 242)
        )

        start = (self.current_page - 1) * MISSIONS_PER_PAGE
        end = start + MISSIONS_PER_PAGE
        page_missions = self.all_missions[start:end]

        for t_name, info in page_missions:
            unlocked = info["check"](self.stats, self.fans_count) or (t_name in self.purchased)
            status_tag = "✅ **TERBUKA**" if unlocked else "🔒 **TERKUNCI**"
            
            embed.add_field(
                name=f"{info['emoji']} {t_name} — {status_tag}",
                value=f"> **Misi:** {info['misi']}",
                inline=False
            )

        embed.set_footer(text=f"Halaman {self.current_page} dari {self.total_pages} • Gunakan !!ktp lalu klik ⚙️ untuk memasang!")
        return embed


class MisiCog(commands.Cog, name="Sistem Misi & Title"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="misi", aliases=["title", "titles"])
    async def misi_command(self, ctx):
        stats = await database.get_all_event_stats(ctx.author.id)
        fans_count = await database.get_fans_count(ctx.author.id)
        purchased = await database.get_user_title_inventory(ctx.author.id)

        view = MisiView(ctx.author, stats, fans_count, purchased)
        embed = view.build_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(MisiCog(bot))