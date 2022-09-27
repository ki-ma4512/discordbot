import discord
from discord.ext import commands
from colorama import Fore,Back, Style
import youtube_dl
import json
from discord import Embed
import asyncio
#import bs4あつもり

#ファイルの読み込み
#botのconfigを読み込み
with open("config.json","r",encoding="utf-8_sig") as f:
	config = json.load(f)
#botのコマンド部分を読み込み
with open("mycommands.json","r",encoding="utf-8_sig") as f:
  mycommands = json.load(f)
#あつ森家具listを読み込み
#家具名前
with open("item.name.list.json","r",encoding="utf-8_sig") as f:
  furniture_name_list = json.load(f)
#家具画像URLを読み込み
with open("item.url.list.json","r",encoding="utf-8_sig") as f:
  furniture_url_list = json.load(f)


Intents = discord.Intents.all()

bot = commands.Bot(
  command_prefix=config['prefix'],
  help_command=None,
  case_insensitive=True,
  intents=Intents
)

color_GRREN = 0xff0000
coler_RED = 0xff0000
print("botの起動を開始します")
@bot.event
async def on_ready():
  for channel in bot.get_all_channels():
        print(Fore.WHITE + "チャンネル名:" + str(channel.name))
        print(Fore.WHITE + "チャンネルID:" + str(channel.id))
        print("-----------------------------------")
  print(Fore.GREEN + f"正常に起動しました\nBot:{bot.user}" + Fore.RESET)
  await bot.change_presence(activity=discord.Game(name=f"{config['prefix']}helpでコマンドが見れます。")) 


#helpコマンド
@bot.command(name=mycommands['help']['name'],aliases=mycommands['help']['aliases'])
async def help(ctx,info=None):
  p = config['prefix']
  if info == None:
    embed=discord.Embed(title=f"{bot.user.name}のコマンド",description=f"""
    `{p}help` `{p}join` `{p}stop` `{p}play` `{p}pause` `{p}resume` `{p}want`
    """,color=color_GRREN)
    embed.set_footer(text=f"詳しい使い方は{p}help <コマンド名>で確認できます")
    await ctx.send(embed=embed)
    return
  cmds = bot.get_command(info.lower())    
  if cmds == None:
    await ctx.send(f"コマンドが見つかりません\n使い方を見る場合は{p}を外して検索してください")
    return
  embed=discord.Embed(title=f"{info}の使い方",color=color_GRREN)
  embed.add_field(name="コマンド名",value=cmds.name,inline=False)
  embed.add_field(name="エイリアス",value="\n".join(mycommands[cmds.name]['aliases']),inline=False)
  embed.add_field(name="できること",value=mycommands[cmds.name]['usage'],inline=False)
  embed.add_field(name="エイリアスって何？",value=f"エイリアスはこれでも反応するよってやつです\n例でいうと{p}{mycommands['play']['name']}じゃなくて{p}{mycommands['play']['aliases'][0]}でも反応するよってことです")
  await ctx.send(embed=embed)

#音楽

@bot.command(name=mycommands['join']['name'],aliases=mycommands['join']['aliases'])
async def join(ctx):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return 
  if ctx.voice_client == None:
    await ctx.author.voice.channel.connect()
    await ctx.send("ボイスチャンネルに接続しました")
  else:
    await ctx.voice_client.move_to(ctx.author.voice.channel)

@bot.command(name=mycommands['stop']['name'],aliases=mycommands['stop']['aliases'])
async def stop(ctx):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return
  await ctx.voice_client.disconnect()
  await ctx("停止しました")

@bot.command(name=mycommands['play']['name'],aliases=mycommands['play']['aliases'])
async def play(ctx,*,music=None):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return
  if music == None:
    await ctx.send("曲がが指定されていません")
    return
  if ctx.voice_client == None:
    await ctx.author.voice.channel.connect()
  ctx.voice_client.stop()  
  ffmpeg_option = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  ytdl_option = {'format':'bestaudio','quiet':'true'}
  ytdl = youtube_dl.YoutubeDL(ytdl_option)
  if not "https://" in music or "http://" in music:
    await ctx.send(f"{music}を読み込み中です")
    music = ytdl.extract_info(f"ytsearch:{music}",download=False)['entries'][0]
    sound_source = music['url']
  else:
    await ctx.send(f"<{music}>を読み込み中です")
    music = ytdl.extract_info(music,download=False)
    sound_source = music['formats'][0]['url']
  embed=discord.Embed(title=music['title'],url=music['webpage_url'],color=color_GRREN)
  embed.set_author(name=music['uploader'])
  embed.set_image(url=music['thumbnail'])
  await ctx.send(embed=embed)
  ctx.voice_client.play(await discord.FFmpegOpusAudio.from_probe(sound_source,**ffmpeg_option))
    
@bot.command(name=mycommands['pause']['name'],aliases=mycommands['pause']['aliases'])
async def pause(ctx):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return
  ctx.voice_client.pause()
  await ctx.channel.send("曲の再生を一時停止しました")
    
@bot.command(name=mycommands['resume']['name'],aliases=mycommands['resume']['aliases'])
async def resume(ctx):
  if ctx.author.voice == None:
    await ctx.send("ボイスチャンネルに参加していません")
    return
  ctx.voice_client.resume()
  await ctx.channel.send("曲の再生を再開しました")



#投票
@bot.command(name=mycommands['want']['name'],aliases=mycommands['want']['aliases'])
                  #検索内容　#数
async def want(ctx,messages,quantit="1",color = "指定なし"):
  end_embed = Embed(
    title='投票を終了します',
    description=None,
    color=0x0000ff
    )
  #投票者のID＆mane
  voter = ctx.author
  voter_id = ctx.author.id
  try:
    #メイン本体 vote_embed
    if furniture_name_list[messages] == messages:

      vote_embed = Embed(
      title="欲しいもの",
      description=" " + messages,
      color=0x3bd415
                        )
    #追加
      vote_embed.add_field(
      name="欲しい数",
      value=" × "+ quantit,inline=False           
                 )
    #追加2
      vote_embed.add_field(
      name="カラー",
      value="  "+ color,inline=False           
                 )
    #画像を追加
      vote_embed.set_image( #画像URL
    url = furniture_url_list[messages]
                   )
          #送信message
      await ctx.send("@everyone""\n"f"{ctx.author.mention} からの募集")
      msg=await ctx.send(embed = vote_embed)
    #投票の作成
      await msg.add_reaction("🙆‍♂️")
      await msg.add_reaction("❌")
      await msg.pin()
      await asyncio.sleep(1)
      @bot.event
      async def on_reaction_add(reaction, user):
    
          if voter != user and user != bot.user:
              if reaction.emoji == "🙆‍♂️":
                await msg.edit(embed=end_embed)
                await ctx.send("@everyone \n <@{}>さんがいけるようだ！ 投票を終了します。".format(user.id))
                #print(reaction,user)
                await msg.clear_reactions()   
                await msg.unpin()      
          if voter == user and user != bot.user:
              if reaction.emoji == "❌":
                await msg.edit(embed=end_embed)
                await ctx.send("@everyone \n <@{}>さんが投票を辞退しました。 投票を終了します。".format(voter_id))
                await msg.unpin()
                #print(reaction,user)
                #print("投票を終了しました")

  #アイテムが見つからなかった時に実行する error_embed
  except KeyError:
    error_embed = Embed(
       title="MameError",
       description=" " + "アイテム名があっていないか、存在しません\n 正しい値を入力してください",
       color=coler_RED
     )
    error_embed.set_image( #画像URL
      url = "https://www.silhouette-illust.com/wp-content/uploads/2016/11/16770-300x300.jpg"
                    )
    await ctx.send(f"{ctx.author.mention} エラー \n Missing or nonexistent item name")
    msg=await ctx.send(embed = error_embed)
    await msg.add_reaction("⚠️")
    await msg.delete(delay=5)
  
@bot.command()
async def test(ctx):
    await ctx.send("HI!"+ ctx.author.mention)




bot.run(config['token'])
