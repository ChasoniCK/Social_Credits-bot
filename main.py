import discord
from discord.ext import commands
from discord import Intents
import sqlite3

bot = commands.Bot(command_prefix='!', intents=Intents.all())
bot.remove_command("help")

connection = sqlite3.connect("economy.db")
cursor = connection.cursor()

@bot.event
async def on_ready():
    cursor.execute('''CREATE TABLE IF NOT EXISTS economy
             (name TEXT, id INT, balance BIGINT)''')
    connection.commit()
    
    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM economy WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f"INSERT INTO economy VALUES ('{member}', {member.id}, 0)")
            else:
                pass
    connection.commit()

@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM economy WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO economy VALUES ('{member}', {member.id}, 0)")
        connection.commit()
    else:
        pass
    
@bot.command(aliases=['social_credit', 'social_credits', 'social', 'credits', 'credit'])
async def __social_credit(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed=discord.Embed(
            description=f"""Социальный рейтинг **{ctx.author}** равен **{cursor.execute(f"SELECT balance FROM economy WHERE id = {ctx.author.id}").fetchone()[0]}**"""
        ))
    else:
        await ctx.send(embed=discord.Embed(
            description=f"""Социальный рейтинг **{member}** равен **{cursor.execute(f"SELECT balance FROM economy WHERE id = {member.id}").fetchone()[0]}**"""
        ))

@commands.has_role("Голова дракона x 龙的头")
@bot.command(aliases=['update_table'])
async def __create_table(ctx):
    await __update_table(ctx.guild)
        
async def __update_table(guild):
    channel = discord.utils.get(guild.channels, name="社会信用-социальный-кредит-社会信用")
    if channel:
        triad_role = discord.utils.get(guild.roles, name="Триадовец [三合会士兵]")  
        if triad_role:
            found_message = None
            async for message in channel.history(limit=10):
                if message.author == bot.user:
                    found_message = message
                    break

            triads_scores = {}
            role = bot.get_guild(1157801985362378802).get_role(1180609972455870474)
            triad_members = role.members
                    
            for member in triad_members:
                balance = cursor.execute(f"SELECT balance FROM economy WHERE id = {member.id}").fetchone()[0]
                triads_scores[member.display_name] = balance
            total_score = sum(triads_scores.values())
            table_content = "```Markdown\n"
            table_content += f"ТРИАДЫ                              Общий счёт триадцев: {total_score}\n"
            for member, balance in triads_scores.items():
                table_content += f"{member:<35} {balance}\n"
            table_content += "```"
            
            if found_message:
                await found_message.edit(content=table_content)
            else:
                await channel.send(table_content)
        else:
            await channel.send(f"Роль Триадовец [三合会士兵] не найдена.")
    else:
        await guild.owner.send(f"Канал 社会信用-социальный-кредит-社会信用 не найден.")


@commands.has_role("Голова дракона x 龙的头")
@bot.command(aliases=['give'])
async def __give(ctx, member: discord.Member = None, amount: int = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете дать социальных кредитов")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму социальных кредитов, которую хотите начислить пользователю")
        elif amount < 1:
            await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 ")
        else:
            cursor.execute(f"UPDATE economy SET balance = balance + ? WHERE id = ? ", (amount, member.id))
            connection.commit()
            
            await ctx.message.add_reaction('🇨🇳')
            
            await __create_table(ctx)
    

@commands.has_role("Голова дракона x 龙的头")
@bot.command(aliases=['take'])
async def __take(ctx, member: discord.Member = None, amount = None):
    if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому желаете дать социальных кредитов")
    else:
        if amount is None:
            await ctx.send(f"**{ctx.author}**, укажите сумму социальных кредитов, которую хотите начислить пользователю")
        elif amount == 'all':
            cursor.execute(f"UPDATE economy SET balance = 0 WHERE id = {member.id}")
            connection.commit()
            
            await ctx.message.add_reaction('🇨🇳')
        elif int(amount) < 1:
            await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 ")
        else:
            cursor.execute(f"UPDATE economy SET balance = balance - ? WHERE id = ? ", (int(amount), member.id))
            connection.commit()
            
            await ctx.message.add_reaction('🇨🇳')
            
            await __create_table(ctx)


bot.run('MTIwNTkyNjY4ODIxMTQ2ODM5MA.G7q8jl.7WLhFWK2S27knLA8a57ityrVFmYAUc11WmmRXI')