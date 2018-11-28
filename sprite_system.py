import sdl2
import sdl2.ext
from manager import Resources

class SpriteFactory:
	def __init__(self, scene):
		self.sprite_system = scene.sprite_system
		self.color_factory = scene.factory.from_color
		self.image_factory = scene.factory.from_image
		self.map_to_screen_transform = scene.map_to_screen_transform
	def from_color(self, color, size, **kwargs):
		## kwargs = {positions OR position, depth}
		if 'positions' in kwargs and 'position' in kwargs:
			raise AttributeError('bad arguments passed to from_image')
		elif 'positions' in kwargs:
			sprites = []
			for position in kwargs['positions']:
				sprite = self.color_factory(color(position), size)
				sprite.position = self.map_to_screen_transform(position)
				if 'depth' in kwargs:
					sprite.depth = kwargs['depth']
				sprites.append(sprite)
			return SpriteGroup(self.sprite_system, sprites)
		else:
			sprite = self.color_factory(color, size)
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = self.map_to_screen_transform(kwargs['position'])
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.sprite_system, sprite)
	def from_image(self, filename, **kwargs):
		## kwargs = {positions OR position, depth}
		if 'positions' in kwargs and 'position' in kwargs:
			raise AttributeError('bad arguments passed to from_image')
		elif 'positions' in kwargs:
			sprites = []
			for position in kwargs['positions']:
				sprite = self.image_factory(Resources.get(filename))
				sprite.position = self.map_to_screen_transform(position)
				if 'depth' in kwargs:
					sprite.depth = kwargs['depth']
				sprites.append(sprite)
			return SpriteGroup(self.sprite_system, sprites)
		else:
			sprite = self.image_factory(Resources.get(filename))
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = self.map_to_screen_transform(kwargs['position'])
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.sprite_system, sprite)

class SpriteHandler:
	def __init__(self, sprite_system, sprite=None):
		self.sprite_system = sprite_system
		self.sprite = sprite
	def register(self):
		self.sprite_system.register(self.sprite)
	def deregister(self):
		self.sprite_system.deregister(self.sprite)

class SpriteGroup:
	""" class intended to make registration and deregistration of multiple sprites easier """
	def __init__(self, sprite_system, sprites=[]):
		self.sprite_system = sprite_system
		self.sprites = [SpriteHandler(self.sprite_system, sprite) for sprite in sprites]
	def register(self):
		for handler in self.sprites:
			self.sprite_system.register(handler.sprite)
	def deregister(self):
		for handler in self.sprites:
			self.sprite_system.deregister(handler.sprite)

class SpriteSystem:
	def __init__(self, scene, **kwargs):
		self.renderer = scene.manager.spriterenderer
		self.registered_sprites = []
	def on_update(self):
		self.renderer.render(sprites=self.registered_sprites)
	def register(self, sprite):
		if not sprite in self.registered_sprites:
			self.registered_sprites.append(sprite)
	def deregister(self, sprite):
		if sprite in self.registered_sprites:
			self.registered_sprites.remove(sprite)