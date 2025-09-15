
import discord
from discord.ext import commands
from datetime import datetime, timezone
from keep_alive import keep_alive

keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True
intents.messages = True
intents.presences = True    # needed for online status
intents.invites = True    # needed for online status
intents.message_content = True   # required to read member messages

bot = commands.Bot(command_prefix="!", intents=intents)

invites_cache = {}

# === VERIFICATION ===
# === Replace these IDs with your server info ===
TICKET_CATEGORY_ID = 1415761389426970644
VERIFIED_ROLE_ID = 1415070546479284275
UNVERIFIED_ROLE_ID = 1415738532693016586
MOD_ROLE_ID = 1415068252266041465

# === Ready event ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("Bot is ready and listening for tickets.")

# === When a new ticket channel is created ===
@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.TextChannel) and channel.category_id == TICKET_CATEGORY_ID:
        # Find the ticket member (first non-mod, non-bot)
        guild = channel.guild
        mod_role = guild.get_role(MOD_ROLE_ID)
        ticket_member = None
        for m in channel.members:
            if mod_role not in m.roles and not m.bot:
                ticket_member = m
                break

        # # Post verification message
        # if ticket_member:
        #     message = await channel.send(
        #         f"✨ Welcome {ticket_member.mention}! Please send a selfie holding a paper with your Discord username.\n"
        #         "Mods will approve or decline using the reactions below.\n\n"
        #         "✅ Approve\n❌ Decline"
        #     )

# === Reaction handler for mods approving/declining ===
# @bot.event
# async def on_raw_reaction_add(payload):
#     if payload.user_id == bot.user.id:
#         return

#     guild = bot.get_guild(payload.guild_id)
#     member = guild.get_member(payload.user_id)  # mod who reacted
#     channel = guild.get_channel(payload.channel_id)
#     message = await channel.fetch_message(payload.message_id)
#     emoji = str(payload.emoji)

#     # Only mods can react
#     mod_role = guild.get_role(MOD_ROLE_ID)
#     if mod_role not in member.roles:
#         return  # ignore reactions from non-mods

#     # Check if the message author is the ticket member (not bot, not mod)
#     if message.author.bot or mod_role in message.author.roles:
#         return

#     ticket_member = message.author

#     # Get roles
#     verified_role = guild.get_role(VERIFIED_ROLE_ID)
#     unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)

#     try:
#         if emoji == "✅":
#             await ticket_member.add_roles(verified_role)
#             await ticket_member.remove_roles(unverified_role)
#             await channel.send(f"✅ {ticket_member.mention} has been verified!")
#         elif emoji == "❌":
#             await channel.send(f"❌ {ticket_member.mention}'s verification was declined.")
#     except discord.Forbidden:
#         await channel.send("⚠️ I don't have permission to assign/remove roles.")

# Buttons view
class VerificationView(discord.ui.View):
    def __init__(self, ticket_member):
        super().__init__(timeout=None)
        self.ticket_member = ticket_member

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        mod_role = guild.get_role(MOD_ROLE_ID)

        # ✅ Check: only mods can approve
        if mod_role not in interaction.user.roles:
            await interaction.response.send_message("⚠️ Only moderators can use this button.", ephemeral=True)
            return

        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)

        try:
            await self.ticket_member.add_roles(verified_role)
            await self.ticket_member.remove_roles(unverified_role)
            await interaction.response.send_message(
                f"✅ {self.ticket_member.mention} has been verified!", ephemeral=False
            )

        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Missing permissions.", ephemeral=True)
        
        await interaction.channel.send(
            "Please go to the first text in this channel and press on **Close Ticket** button to close this ticket."
        )
    @discord.ui.button(label="❌ Deny", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        mod_role = guild.get_role(MOD_ROLE_ID)

        # ✅ Check: only mods can deny
        if mod_role not in interaction.user.roles:
            await interaction.response.send_message("⚠️ Only moderators can use this button.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"❌ {self.ticket_member.mention}'s verification was declined.", ephemeral=False
        )

        await interaction.channel.send(
            "Please go to the first text in this channel and press on **Close Ticket** button to close this ticket."
        )

# Trigger when someone sends an image in their ticket channel
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Only act inside ticket category
    if message.channel.category_id == TICKET_CATEGORY_ID:
        # Check if the message has attachments (images)
        if message.attachments:
            image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp")
            for attachment in message.attachments:
                if attachment.filename.lower().endswith(image_extensions):
                    # Found an image, send verification buttons
                    await message.channel.send(
                        f"Moderators, please review {message.author.mention}'s verification selfie:",
                        view=VerificationView(message.author)
                    )
                    break  # stop after first valid image

    # Still process commands if any
    await bot.process_commands(message)


# ---------------- SERVER STATS ----------------
# Replace with your channel IDs
TOTAL_MEMBERS_CHANNEL_ID = 1415968351557255181
ONLINE_MEMBERS_CHANNEL_ID = 1415970246770036786
# TEXT_CHANNELS_CHANNEL_ID = 333333333333333333
# ROLE_COUNT_CHANNEL_ID = 444444444444444444
BOT_COUNT_CHANNEL_ID = 1415977834001727498   # 🤖 Bot Count
SERVER_AGE_CHANNEL_ID = 1415977874770366524  # 📅 Server Age
UNVERIFIED_CHANNEL_ID = 1415977988327211008  # 🔒 Unverified Members
VERIFIED_CHANNEL_ID = 1415978027854073876    # ✅ Verified Members

# Replace with your role IDs
VERIFIED_ROLE_ID = 1415070546479284275
UNVERIFIED_ROLE_ID = 1415738532693016586

async def update_stats_channels(guild):
    # Count bots
    bot_count = len([m for m in guild.members if m.bot])

    # Server age (in days)
    server_age_days = (datetime.now(timezone.utc) - guild.created_at).days

    # Count verified/unverified
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)
    verified_count = len(verified_role.members) if verified_role else 0
    unverified_count = len(unverified_role.members) if unverified_role else 0

    total_members = guild.member_count
    online_members = len([m for m in guild.members if not m.bot and m.status != discord.Status.offline])
    text_channels = len(guild.text_channels)
    role_count = len(guild.roles)

    await guild.get_channel(TOTAL_MEMBERS_CHANNEL_ID).edit(name=f"👥 Total Members: {total_members}")
    await guild.get_channel(ONLINE_MEMBERS_CHANNEL_ID).edit(name=f"💻 Online: {online_members}")
    # await guild.get_channel(TEXT_CHANNELS_CHANNEL_ID).edit(name=f"📝 Text Channels: {text_channels}")
    # await guild.get_channel(ROLE_COUNT_CHANNEL_ID).edit(name=f"🎭 Roles: {role_count}")
    await guild.get_channel(BOT_COUNT_CHANNEL_ID).edit(name=f"🤖 Bots: {bot_count}")
    await guild.get_channel(SERVER_AGE_CHANNEL_ID).edit(name=f"📅 Age: {server_age_days}d")
    await guild.get_channel(UNVERIFIED_CHANNEL_ID).edit(name=f"🔒 Unverified: {unverified_count}")
    await guild.get_channel(VERIFIED_CHANNEL_ID).edit(name=f"✅ Verified: {verified_count}")

@bot.event
async def on_member_join(member):
    await update_stats_channels(member.guild)

@bot.event
async def on_member_remove(member):
    await update_stats_channels(member.guild)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        await update_stats_channels(guild)
    print(f"✅ Logged in as {bot.user}")


# === Run the bot ===
bot.run("DISCORD_TOKEN")


