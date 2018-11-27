import sdl2
import sdl2.ext
from manager import Resources

class SpriteFactory:
	def __init__(self, scene):
		self.scene = scene
		self.color_factory = scene.factory.from_color
		self.image_factory = scene.factory.from_image
	def from_color(self, color, size, **kwargs):
		## kwargs = {positions OR position, depth}
		if 'positions' in kwargs and 'position' in kwargs:
			raise AttributeError('bad arguments passed to from_image')
		elif 'positions' in kwargs:
			sprites = []
			for position in kwargs['positions']:
				sprite = self.color_factory(color(position), size)
				sprite.position = position
				if 'depth' in kwargs:
					sprite.depth = kwargs['depth']
				sprites.append(sprite)
			return SpriteGroup(self.scene, sprites)
		else:
			sprite = self.color_factory(color, size)
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = kwargs['position']
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.scene, sprite)
	def from_image(self, filename, **kwargs):
		## kwargs = {positions OR position, depth}
		if 'positions' in kwargs and 'position' in kwargs:
			raise AttributeError('bad arguments passed to from_image')
		elif 'positions' in kwargs:
			sprites = []
			for position in kwargs['positions']:
				sprite = self.image_factory(Resources.get(filename))
				sprite.position = position
				if 'depth' in kwargs:
					sprite.depth = kwargs['depth']
				sprites.append(sprite)
			return SpriteGroup(self.scene, sprites)
		else:
			sprite = self.image_factory(Resources.get(filename))
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = kwargs['position']
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.scene, sprite)

class SpriteHandler:
	def __init__(self, scene, sprite=None):
		self.scene = scene
		self.sprite = sprite
	def register(self):
		self.scene.sprite_system.register(self.sprite)
	def deregister(self):
		self.scene.sprite_system.deregister(self.sprite)

class SpriteGroup:
	""" class intended to make registration and deregistration of multiple sprites easier """
	def __init__(self, scene, sprites=[]):
		self.scene = scene
		self.sprites = [SpriteHandler(scene, sprite) for sprite in sprites]
	def register(self):
		for handler in self.sprites:
			self.scene.sprite_system.register(handler.sprite)
	def deregister(self):
		for handler in self.sprites:
			self.scene.sprite_system.deregister(handler.sprite)

class SpriteSystem:
	def __init__(self, scene, **kwargs):
		self.scene = scene
		self.registered_sprites = []
	def on_update(self):
		self.scene.manager.spriterenderer.render(sprites=self.registered_sprites)
	def register(self, sprite):
		if not sprite in self.registered_sprites:
			self.registered_sprites.append(sprite)
	def deregister(self, sprite):
		if sprite in self.registered_sprites:
			self.registered_sprites.remove(sprite)