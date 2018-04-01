import discord
from discord.ext import commands
from .utils import checks

class Tagger:
	"""Raid Tagging for EKPogo Servers"""
	
	def __init__(self, bot):
		self.bot = bot
		self.tier_1 = ['Magikarp', 'Wailmer', 'Swablu', 'Snorunt']
		self.tier_2 = ['Slowbro', 'Exeggutor', 'Sableye', 'Mawile', 'Manectric']
		self.tier_3 = ['Machamp', 'Gengar', 'Jynx', 'Jolteon', 'Piloswine']
		self.tier_4 = ['Golem', 'Tyranitar', 'Aggron', 'Absol']
		self.tier_5 = ['Articuno', 'Zapdos', 'Moltres', 'Mewtwo', 'Mew', 'Raikou', 'Entei', 'Suicune', 'Lugia', 'Ho-Oh', 'Celebi', 'Kyogre', 'Groudon', 'Rayquaza']
		self.extra = ['margate','broadstairs','ramsgate','canterbury','hernebay','whitstable','sandwich','ashford', 'exraidgyms', 'raidtrain', 'Ditto', 'Ghosts', 'Magikarp']
		self.approved_roles = self.tier_1 + self.tier_2 + self.tier_3 + self.tier_4 + self.tier_5 + self.extra
		THANET_EXR_LOCS = ['Tribal Fields','Birchington Play Area', 'The Shelter', 'Millmead Road Childrens Adventure Playground', 'Cliftonville Library at Northdown Park', 'Thanet Wanderers RUFC', 'Pierremont Park Water Fountain', 'Newington Play', 'Ellington Park Bandstand', 'Manufacture of Innovative Medicines', 'Water Reservoir', 'The Waterfall', 'Edward Welby Pugin', 'Winterstoke Gardens']
		HB_WHIT_EXR_LOCS = ['Reculver 2000 Statue', 'Reculver Country Park Board', 'Avenue of Remembrance', 'Tankerton Skate Park']
		self.exrgyms = THANET_EXR_LOCS + HB_WHIT_EXR_LOCS
		self.ekpogo_watched = ('The Shelter', 'Millmead Road Childrens Adventure Playground', 'Cliftonville Library at Northdown Park', 'Ellington Park Bandstand',  'Edward Welby Pugin')
	
	@commands.command(pass_context=True)
	async def subscribe(self, ctx, species):
		role = None
		if species.lower() in (role.lower() for role in self.approved_roles):
			role = await self.find_role(ctx.message.server, species)
		if role is None:
			await self.bot.say("I couldn't find {}. Are you sure it's a valid role?".format(species.capitalize()))
			return
		
		try:
			await self.bot.add_roles(ctx.message.author, role)
		except discord.errors.Forbidden:
			await self.bot.edit_message(message, "Error: I don't have permission to set roles. Aborted!")
			return
		
		await self.bot.say("{}, you should find hot fresh {} tags in your inbox soon.".format(ctx.message.author.mention, role.name))
	
	@commands.command(pass_context=True)
	async def unsubscribe(self, ctx, species):
		if species.lower() in (role.lower() for role in self.approved_roles):
			role = await self.find_role(ctx.message.server, species)
		if role is None:
			await self.bot.say("I couldn't find {}. Are you sure it's a valid role?".format(species.capitalize()))
			return
		
		try:
			await self.bot.remove_roles(ctx.message.author, role)
		except discord.errors.Forbidden:
			await self.bot.edit_message(message, "Error: I don't have permission to set roles. Aborted!")
			return
		
		await self.bot.say("{}, no more {} tags for you!".format(ctx.message.author.mention, role.name))
	
	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_permissions(assign_roles=True)
	async def update_roles(self, ctx):
		for role in self.approved_roles:
			await self.find_role(ctx.message.server, role, create=True)
		await self.bot.say("Done")
	
	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_permissions(assign_roles=True)
	async def test_tag(self, ctx, message_id):
		message = await self.bot.get_message(ctx.message.channel, message_id)
		await self.tags(message)
	
	async def find_role(self, server, role_name, create=False):
		"""All role names are compared as `str.lower()`"""
		
		role = discord.utils.find(lambda x: x.name.lower() == role_name.lower(), server.roles)
		if not role and create == True:
			role = await self.bot.create_role(server, name=role_name, mentionable=True)
		if role:
			return role
		else:
			return None
	
	async def tags(self, message):
		if message.channel.name == 'raids' and (int(message.author.id) == 422735322057801729 and message.author.bot == True):
			raid = {}
			raid['pokemon'] = message.embeds[0]['title'].split(' ')[-1].lstrip()
			monster_role = await self.find_role(message.server, raid['pokemon'])
			raid['url'] = message.embeds[0]['url']
			for l in message.embeds[0]['description'].splitlines():
				if l.split(':')[0] == 'Moveset':
					raid['fast_move'], raid['charge_move'] = l.split(' / ')
				elif len(l.split(':')) == 3 and l.split(' ')[1] == 'until':
					raid['end_time'] = l.split(' ')[2].lstrip()
				elif l.split(' ')[0].replace("**", "") == 'Gym':
					raid['Gym'] = l.split(':')[1].replace("**", "").lstrip().rsplit(' ', 1)[0]
				elif len(l.split(':')) == 2:
					k, v = l.split(':')
					raid[k.replace("**", " ").lstrip()] = v.replace("**", " ").lstrip()
			print(raid)
			try:
				print(monster_role.mention)
				new_message = monster_role.mention
				print(raid['Area'])
				town_role = await self.find_role(message.server, raid['Area'])
			except AttributeError:
				return
			new_message += 'at '+raid['Gym']
			new_message += 'at '+raid['end_time']
			new_message += '\n'+town_role.mention
			if raid['Gym'] in self.exrgyms:
				exrrole = await self.find_role(message.server, 'ExRaidGyms')
				new_message += '\n'+exrrole.mention
				if raid['Gym'] in self.ekpogo_watched:
					await self.bot.send_message(self.bot.get_channel('405404234083991562'), new_message)
			await self.bot.send_message(message.channel, new_message)

def setup(bot):
	n = Tagger(bot)
	bot.add_cog(n)
	bot.add_listener(n.tags, 'on_message')
