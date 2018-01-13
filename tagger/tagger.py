import discord
from discord.ext import commands
from .utils import checks

class Tagger:
	"""ERaid Tagging for EKPogo Servers"""
	
	def __init__(self, bot):
		self.bot = bot
		self.approved_roles = ('ivysaur','charmeleon','wartortle','metapod','cloyster','tentacruel','sandslash','magneton','marowak','machamp','alakazam','omastar','gengar','scyther','ninetales','porygon','tyranitar','snorlax','golem','lapras','poliwrath','nidoking','nidoqueen','mewtwo','ho-oh','lugia','entei','raikou','zapdos','moltres','celebi','mew','articuno','suicune','absol','mawile','margate','broadstairs','ramsgate','canterbury','hernebay','whitstable','sandwich','ashford', 'groudon', 'wailmer', 'kyogre', 'exraidgyms')
		self.exrgyms = ['Avenue of Remembrance', 'The Downs', 'Herne Meadow', 'Tankerton Coastal Protection Works', 'In Memory of Victor Algar', 'Tankerton Slopes', 'Cannons and Boat Mast', 'Whitstable Castle', 'Chestfield', 'Birchington Play Area', 'Quex Lake Sculptures', 'W and B Golf Club', 'George V. Silver Jubilee Memorial', 'Strokes Adventure Golf', 'Band Rotunda', 'Cliftonville Library at Northdown Park', 'One Day a Woodland', 'Thanet Wanderers RUFC', 'Pierremont Park Water Fountain', 'Ellington Park Bandstand', 'The Waterfall', 'Manufacture of Innovative Medicines', 'Newington Play', 'Water Reservoir', 'Tankerton Skate Park', 'Whitstable Castle Gate House','Reculver Country Park Board']
	
	@commands.command(pass_context=True)
	async def subscribe(self, ctx, species):
		role = None
		if species.lower() in self.approved_roles:
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
		if species.lower() in self.approved_roles:
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
	async def add_role(self, ctx, species):
		role = await self.find_role(ctx.message.server, species, create=True)
		await self.bot.say("Role {} enabled.".format(role.mention))
	
	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_permissions(assign_roles=True)
	async def test_tag(self, ctx, message_id):
		message = await self.bot.get_message(ctx.message.channel, message_id)
		await self.tags(message)
	
	async def find_role(self, server, role_name, create=False):
		"""All role names are compared as `str.lower()`"""
		
		role = discord.utils.find(lambda x: x.name.lower() == role_name.lower(), server.roles)
		if not role and create == True:
			role = await self.bot.create_role(server, name__lower=role_name.lower(), mentionable=True)
		if role:
			return role
		else:
			return None
	
	async def tags(self, message):
		if message.channel.name == 'raids' and (int(message.author.discriminator) == 0 and message.author.bot == True and message.author.name != 'Egg'):
			role = await self.find_role(message.server, message.author.name.split(' ')[0])
			raid = {}
			raid['url'] = message.embeds[0]['url']
			for l in message.embeds[0]['description'].splitlines():
				if len(l.split(':')) == 1:
					raid['fast_move'], raid['charge_move'] = l.split(' / ')
				elif len(l.split(':')) == 3:
					raid['end_time'] = l.split(' ')[3].lstrip()
				else:
					k, v = l.split(':')
					raid[k] = v.lstrip()
			try:
				new_message = role.mention
			except AttributeError:
				new_message = message.author.name.split(' ')[0]
			new_message += ' '+raid['Gym']
			new_message += ' '+raid['end_time']
			new_message += '\n'+raid['url']
			if raid['Gym'] in self.exrgyms:
				exrrole = await self.find_role(message.server, 'ExRaidGyms')
				new_message += '\n'+exrrole.mention
			await self.bot.send_message(message.channel, new_message)

def setup(bot):
	n = Tagger(bot)
	bot.add_cog(n)
	bot.add_listener(n.tags, 'on_message')
