import sdl2
import sdl2.ext
from manager import Resources
from constants import TILE_SIZE, TILE_MAX_WEIGHT

class SurfaceFactory:
	def __init__(self):
		pass
	def from_image(self, filename):
		return sdl2.ext.load_image(Resources.get(filename))

class SpriteFactory:
	def __init__(self, scene):
		self.sprite_system = scene.sprite_system
		self.viewport_system = scene.viewport_system
		self.color_factory = scene.factory.from_color
		self.surface_factory = scene.factory.from_surface
		self.image_factory = scene.factory.from_image
		self.map_to_screen_transform = scene.map_to_screen_transform
	def combine(self, src, dest):
		## Assume that both are the same size
		sdl2.surface.SDL_BlitSurface(src, None, dest, None)
	def from_surface(self, surface, positions, depth):
		sprites = []
		for position in positions:
			sprite = self.surface_factory(surface)
			sprite.position = self.map_to_screen_transform(position)
			sprite.depth = depth
			sprites.append(sprite)
		if len(positions) == 1:
			return SpriteHandler(self.sprite_system, self.viewport_system, sprites[0])
		else:
			return SpriteGroup(self.sprite_system, self.viewport_system, sprites)
		## args: positions
	def from_map(self, texture_map, key_func, **kwargs):
		sprites = []
		for position in kwargs['positions']:
			surf = texture_map.get_surface(key_func(position))
			if surf is not None:
				sprite = self.surface_factory(surf)
				sprite.position = self.map_to_screen_transform(position)
				sprite.depth = kwargs['depth']
				sprites.append(sprite)		
		return SpriteGroup(self.sprite_system, self.viewport_system, sprites)
		
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
			return SpriteGroup(self.sprite_system, self.viewport_system, sprites)
		else:
			sprite = self.color_factory(color, size)
			
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = self.map_to_screen_transform(kwargs['position'])
			elif 'screen_position' in kwargs and kwargs['screen_position'] is not None:
				sprite.position = kwargs['screen_position']
			
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.sprite_system, self.viewport_system, sprite)
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
			return SpriteGroup(self.sprite_system, self.viewport_system, sprites)
		else:
			sprite = self.image_factory(Resources.get(filename))
			if 'position' in kwargs and kwargs['position'] is not None:
				sprite.position = self.map_to_screen_transform(kwargs['position'])
			if 'depth' in kwargs:
				sprite.depth = kwargs['depth']
			return SpriteHandler(self.sprite_system, self.viewport_system, sprite)

class SpriteHandler:
	def __init__(self, sprite_system, viewport_system, sprite=None):
		self.sprite_system = sprite_system
		self.viewport_system = viewport_system
		self.sprite = sprite
	def register(self):
		self.sprite_system.register(self.sprite)
		self.viewport_system.register(self.sprite)
	def deregister(self):
		self.sprite_system.deregister(self.sprite)
		self.viewport_system.deregister(self.sprite) # deregistration required when deleting an object, may not maintain proper position if re-registered

class SpriteGroup:
	def __init__(self, sprite_system, viewport_system, sprites=[]):
		self.sprite_system = sprite_system
		self.viewport_system = viewport_system
		self.sprites = [SpriteHandler(self.sprite_system, self.viewport_system, sprite) for sprite in sprites]
	def register(self):
		for handler in self.sprites:
			self.sprite_system.register(handler.sprite)
			self.viewport_system.register(handler.sprite)
	def deregister(self):
		for handler in self.sprites:
			self.sprite_system.deregister(handler.sprite)
			self.viewport_system.deregister(handler.sprite)

class SpriteSystem:
	def __init__(self, scene, **kwargs):
		self.renderer = scene.manager.spriterenderer
		self.registered_objects = []
	def on_update(self):
		self.renderer.render(sprites=self.registered_objects)
	def register(self, obj):
		if not obj in self.registered_objects:
			self.registered_objects.append(obj)
	def deregister(self, obj):
		if obj in self.registered_objects:
			self.registered_objects.remove(obj)

		
				