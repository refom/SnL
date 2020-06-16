import discord, io, asyncio, aiohttp
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from random import randint

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    active = discord.Activity(name="Snake and Ladder", type=0)
    await client.change_presence(status=discord.Status.online, activity=active)
    print('Bot is ready now!')

#	Variable
room = {}
my_id = # YOUR BOT ID IN HERE
map_game = Image.open("./image/map.png").convert("RGBA")
size = map_game.size
coordinate = {
	0 : (64, 1300),
	1 : (208, 1120),
	2 : (278, 1045),
	3 : (190, 915),
	4 : (316, 913),
	5 : (348, 811),
	6 : (377, 707),
	7 : (412, 595),
	8 : (343, 522),
	9 : (426, 436),
	10 : (367, 343),
	11 : (217, 336),
	12 : (243, 210),
	13 : (434, 129),
	14 : (473, 263),
	15 : (539, 353),
	16 : (634, 449),
	17 : (752, 370),
	18 : (827, 288),
	19 : (870, 203),
	20 : (1009, 210),
	21 : (1222, 136),
	22 : (1031, 354),
	23 : (918, 389),
	24 : (820, 472),
	25 : (896, 595),
	26 : (1073, 591),
	27 : (1182, 714),
	28 : (1138, 875),
	29 : (1141, 978),
	30 : (1197, 1050),
	31 : (1035, 1077),
	32 : (969, 963),
	33 : (920, 869),
	34 : (808, 926),
	35 : (774, 786),
	36 : (750, 666),
	37 : (605, 670),
	38 : (554, 786),
	39 : (536, 926),
	40 : (428, 1007)}
words = [
	"Fell into a hole somewhere",
	"Banana slips",
	"Thrown by the wind",
	"His tongue was bitten",
	"His feet don't want to follow his wishes"]
no_reakt = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(5)]

def resize(scale, image):
	scaled_size = tuple([x * scale for x in image.size])
	image2 = image.resize(scaled_size)
	return image2

async def zooms(file, no=0):
	img = Image.open(file).convert("RGBA")
	w, h = img.size
	img2 = resize(2, img)

	files = io.BytesIO()

	if no == 1:
		img3 = img2.crop((0, 0, w, h))
		img3.save(files, format="PNG")
	elif no == 2:
		img3 = img2.crop((w, 0, img2.width, h))
		img3.save(files, format="PNG")
	elif no == 3:
		img3 = img2.crop((0, h, w, img2.height))
		img3.save(files, format="PNG")
	elif no == 4:
		img3 = img2.crop((w, h, img2.width, img2.height))
		img3.save(files, format="PNG")
	files.seek(0)
	return files

async def reakt(chat):
	await chat.add_reaction("🎲")	#	Dice
	await chat.add_reaction("❌")	#	exit
	for i in no_reakt:
		await chat.add_reaction(i)

async def skill_2(self, game):
	channel = client.get_channel(game.get_room_id())
	chat = await channel.send(f"> `Mention/tag someone`")
	players = game.list_player()

	def chek(message):
		if message.author.id == self.player_id:
			return True

	while True:
		try:
			message = await client.wait_for("message", timeout=60, check=chek)
		except asyncio.TimeoutError:
			await chat.delete()
			break
		else:
			mentioned = message.mentions
			if mentioned:
				for pl in players:
					if pl.player_id != self.player_id:
						if pl.player_id == mentioned[0].id:
							pl.position -= 5
							if pl.position < 0:
								pl.position = 0
							await chat.edit(content=f"> `{pl.player_name} {words[randint(0,4)]}`\n> `so that makes him walk 5 Step Backward`")
							await asyncio.sleep(3)
							await chat.delete()
							break

class GameSnL():
	def __init__(self, channel_id):
		self.room_id = channel_id
		self.start = False
		self.player = []
		self.__turns = 0

	def get_room_id(self):
		return self.room_id

	def game_state(self):
		return self.start

	def join(self, player_obj):
		self.player.append(player_obj)

	def list_player(self):
		return self.player

	def dice(self, player):
		roll = randint(1,6)
		return roll

	def get_turns(self):
		return self.__turns

	def update_turns(self):
		self.__turns += 1
		if self.__turns > len(self.player)-1:
			self.__turns = 0
		return self.__turns

	def skill_1(self):
		self.__turns -= 1
		if self.__turns < 0:
			self.__turns = len(self.player)-1

	def game_start(self):
		self.start = True

	def game_stop(self):
		self.start = False

class Player():
	def __init__(self, user, room):
		self.player_name = user.display_name
		self.avatar = user.avatar_url
		self.player_id = user.id
		self.room_id = room
		self.position = 0
		self.skill = 0
		self.skill_done = 0
		self.nameSkill = {
			1: "***`Time Travel Skill 🕙 - Back to The Past`***",
			2: "***`Punishment Skill 👊 - 5 Step Backward to Someone`***"}

	def update_position(self, pos):
		self.position += pos

	def gacha_skill(self):
		chance = randint(0, 100)

		if self.skill_done == 1:
			chance += 50
		elif self.skill_done == 2:
			chance += 80
		elif self.skill_done > 2:
			chance = 0
			self.skill_done = 0

		if chance <= 100 and chance > 29:
			self.skill = randint(0,2)
			self.skill_done += 1
			return
		self.skill = 0

	async def skill_activate(self, game):
		if self.skill == 1:
			game.skill_1()
		elif self.skill == 2:
			await skill_2(self, game)
		x = f"> `Skill `{self.nameSkill[self.skill]}` has been used`"
		return x

async def get_image(player):
	async with aiohttp.ClientSession() as session:
		async with session.get(str(player.avatar)) as r:
			file = io.BytesIO(await r.read())
			img = Image.open(file).convert("RGBA")
			img.thumbnail((32, 32))
		return img

async def Screen(game, player_now=None):
	mapnya = Image.new("RGBA", size)
	mapnya.paste(map_game)
	player = game.list_player()
	addCor = 16

	for pl in player:
		avatar = await get_image(pl)
		x, y = coordinate[pl.position]
		position = (x,y)
		if player_now:
			if player_now.player_id != pl.player_id:
				if player_now.position == pl.position:
					position = (x + addCor, y)
					addCor += 16
		mapnya.paste(avatar, position, avatar)

	file = io.BytesIO()
	mapnya.save(file, format="PNG")
	file.seek(0)
	return file

async def render_map(channel, screenss, game):
	players = game.list_player()
	embed = discord.Embed(
		title=f"**Room {channel.name}**",
		color=discord.Colour(0x3498db),
		description="🐍 `Map` 🎲")
	embed.set_image(url="attachment://map.png")
	for pl in players:
		embed.add_field(name=f"**{pl.player_name}**", value=f"⏩ = ***`{pl.position}`***" + "-"*5)
	embed.add_field(name=f"**===============**", value=f"***`Turn`*** = ***`{players[game.get_turns()].player_name}`***", inline=False)
	chat = await channel.send(file=discord.File(screenss, "map.png") , embed=embed)
	return chat

async def skill_want_to_activate(player_now, info, game, channal):
	if player_now.skill != 0:
		await info.edit(content=f"> `{player_now.player_name} Got` {player_now.nameSkill[player_now.skill]}\n> `Want to use` ?")
		await info.add_reaction("🇾") # YES
		await info.add_reaction("🇳") # NO

		def chek(reaction, user):
			if user.id == player_now.player_id and reaction.message.id == info.id:
				return True
		while True:
			try:
				reaction, user = await client.wait_for("reaction_add", timeout=60, check=chek)
			except asyncio.TimeoutError:
				await info.clear_reactions()
				break
			else:
				await info.clear_reactions()
				if str(reaction.emoji) == "🇾":	#	Yes
					xxx = await player_now.skill_activate(game)
					info3 = await channal.send(xxx)
					await asyncio.sleep(2)
					await info3.delete()
					break
				elif str(reaction.emoji) == "🇳":	#	NO
					break

async def win_won(game, player, channel):
	champions = {}

	for pl in game.list_player():
		if pl.player_id != player.player_id:
			champions[pl.player_name] = pl.position

	sorting = reversed(sorted(champions.keys()))
	number = 2

	embed = discord.Embed(
		title=f" 👑 **The Winner is** {player.player_name} ",
		color=discord.Colour(0x3498db),
		description="🐍 **Congratulations for winning the game** 🥳")
	for i in sorting:
		embed.add_field(name=f"***Juara {number}***", value=f"**{i}**")
		number += 1
	await channel.send(embed=embed)
	room.pop(game.get_room_id(), None)

async def player_playing(game, player_now, infonya, chat, channal):
	jalannya = game.dice(player_now)
	game.update_turns()
	await infonya.delete()
	info2 = await channal.send(f"> `{player_now.player_name} {jalannya} Steps forward`")
	await asyncio.sleep(1)
	await chat.delete()
	for i in range(jalannya):
		player_now.update_position(1)

		#	City 3
		if player_now.position == 3:
			screenss = await Screen(game, player_now=player_now)
			chat2 = await render_map(channal, screenss, game)
			await info2.delete()
			info2 = await channal.send(f"> `{player_now.player_name} Arrived at Sukasuka City`")
			await asyncio.sleep(5)
			player_now.gacha_skill()
			await skill_want_to_activate(player_now, info2, game, channal)
			await chat2.delete()

	if player_now.position >= 8 and player_now.position <= 39:
		player_now.gacha_skill()
		await skill_want_to_activate(player_now, info2, game, channal)

	await info2.edit(content=f"> `{player_now.player_name} {jalannya} Steps forward`")

	#	Win Condition
	if player_now.position > 39:
		game.game_stop()
		player_now.position = 40
		await info2.delete()
		await win_won(game, player_now, channal)
		return

	screenss = await Screen(game, player_now=player_now)
	chat = await render_map(channal, screenss, game)
	return chat, info2

async def play_game(game):
	channel = client.get_channel(game.get_room_id())
	screenss = await Screen(game)
	if not game.game_state():
		await channel.send("Game Over")
		return

	chat = await render_map(channel, screenss, game)
	await reakt(chat)
	infonya = await channel.send("> ***`GAME START`***")

	def check(reaction, user):
		if user.id == player_now.player_id and reaction.message.id == chat.id:
			if str(reaction.emoji) == "🎲" or str(reaction.emoji) == "❌" or str(reaction.emoji) in no_reakt:
				return True

	while game.game_state():
		try:
			players = game.list_player()
			turn = game.get_turns()
			player_now = players[turn]
			reaction, user = await client.wait_for("reaction_add", timeout=120, check=check)
		except asyncio.TimeoutError:
			await chat.clear_reactions()
			game.game_stop()
			room.pop(game.get_room_id(), None)
		else:
			channal = reaction.message.channel
			if str(reaction.emoji) == "🎲":	# dice
				chat, infonya = await player_playing(game, player_now, infonya, chat, channal)
				if game.game_state():
					await reakt(chat)

			elif str(reaction.emoji) == no_reakt[0]:	#	0
				await chat.delete()
				screenss = await Screen(game, player_now)
				chat = await render_map(channal, screenss, game)
				await reakt(chat)

			elif str(reaction.emoji) == no_reakt[1]:	#	1
				await chat.delete()
				screenss = await Screen(game, player_now)
				screenss2 = await zooms(screenss, no=1)
				chat = await render_map(channal, screenss2, game)
				await reakt(chat)

			elif str(reaction.emoji) == no_reakt[2]:	#	2
				await chat.delete()
				screenss = await Screen(game, player_now)
				screenss2 = await zooms(screenss, no=2)
				chat = await render_map(channal, screenss2, game)
				await reakt(chat)

			elif str(reaction.emoji) == no_reakt[3]:	#	3
				await chat.delete()
				screenss = await Screen(game, player_now)
				screenss2 = await zooms(screenss, no=3)
				chat = await render_map(channal, screenss2, game)
				await reakt(chat)

			elif str(reaction.emoji) == no_reakt[4]:	#	4
				await chat.delete()
				screenss = await Screen(game, player_now)
				screenss2 = await zooms(screenss, no=4)
				chat = await render_map(channal, screenss2, game)
				await reakt(chat)

			elif str(reaction.emoji) == "❌":
				await chat.edit(content="Game Over", embed=None)
				await chat.clear_reactions()
				game.game_stop()
				room.pop(game.get_room_id(), None)

async def room_game(game):
	channel = client.get_channel(game.get_room_id())

	embed = discord.Embed(
		title="**Join to the Game**",
		color=discord.Colour(0x3498db),
		description="🐍")
	embed.add_field(name=f"**Room** **{channel.name}**", value=" 🎮 = `Join`\n ▶️ = `Play`\n ❌ = `Exit`", inline=False)
	in_room = await channel.send(embed=embed)
	await in_room.add_reaction("🎮")	# Join
	await in_room.add_reaction("▶️")	# Play
	await in_room.add_reaction("❌")	# Exit

	def check(reaction, user):
		if user.id != my_id and reaction.message.id == in_room.id:
			if str(reaction.emoji) == "▶️" or str(reaction.emoji) == "❌" or str(reaction.emoji) == "🎮":
				return True

	async def cek2(game, user, channel):
		if game.list_player():
			if user.player_id not in game.list_player():
				game.join(user)
				await channel.send(f"> `{user.player_name} Joined the Game`")
		else:
			game.join(user)
			await channel.send(f"> `{user.player_name} Joined the Game`")

	while True:
		try:
			reaction, user = await client.wait_for("reaction_add", timeout=120, check=check)
		except asyncio.TimeoutError:
			await in_room.clear_reactions()
			room.pop(game.get_room_id(), None)
			break
		else:
			if str(reaction.emoji) == "▶️":	# Play
				if len(game.list_player()) < 1:
					await in_room.edit(content="No one in the room :(", embed=None)
					await in_room.clear_reactions()
					break
				game.game_start()
				await in_room.delete()
				await play_game(game)
				break
			if str(reaction.emoji) == "❌":	# Exit
				await in_room.delete()
				room.pop(game.get_room_id(), None)
				break
			if str(reaction.emoji) == "🎮":	# Join
				userss = Player(user, game.get_room_id())
				await cek2(game, userss, channel)

@client.group()
async def snl(ctx):
	if ctx.invoked_subcommand is None:
		embed = discord.Embed(
			title="🐍 **Snake and Ladder**",
			color=discord.Colour(0x3498db),
			timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=ctx.guild.icon_url)
		embed.set_author(name=ctx.guild.name)
		embed.add_field(name="***Menu***", value=" ⚔️ = `Play`\n ❌ = `Exit`", inline=False)
		chat = await ctx.send(embed=embed)
		await chat.add_reaction("⚔️")
		await chat.add_reaction("❌")

		channel = chat.channel
		chans = channel.id
		if chans in room.keys():
			await chat.edit(content="> `There is already room here, wait for it to finish or reset it`", embed=None)
			await chat.clear_reactions()
		else:
			def check(reaction, user):
				if user == ctx.message.author and reaction.message.id == chat.id:
					if str(reaction.emoji) == "⚔️" or str(reaction.emoji) == "❌":
						return True

			while True:
				try:
					reaction, user = await client.wait_for("reaction_add", timeout=120, check=check)
				except asyncio.TimeoutError:
					await chat.clear_reactions()
					break
				else:
					if str(reaction.emoji) == "⚔️":
						room[channel.id] = channel.id
						game = GameSnL(channel.id)
						await chat.delete()
						await room_game(game)
						break
					elif str(reaction.emoji) == "❌":
						await chat.delete()
						break

@snl.command()
async def reset(ctx):
	channel = ctx.message.channel.id
	room.pop(channel, None)
	await ctx.send("Room has been reset")

client.run("YOUR TOKEN HERE")