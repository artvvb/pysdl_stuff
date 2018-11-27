#def _register(sprite_container, scene):
#	if not sprite_container.registered:
#		sprite_container.registered = True
#		for element in sprite_container.get_data():
#			scene.spritesystem.register(element)
#def _deregister(sprite_container, scene):
#	if sprite_container.registered:
#		sprite_container.registered = False
#		for data in sprite_container.get_data():
#			scene.spritesystem.deregister(data)

class Sprite:
	def __init__(self, scene, **kwargs):
		self.scene = scene
		if "sprite" in kwargs and "layer" in kwargs:
			self.data = (kwargs["sprite"], kwargs["layer"])
		else:
			self.data = None
		self.registered = False
	
	def register(self): self.scene.sprite_system.register(self)
	def deregister(self): self.scene.sprite_system.deregister(self)
	
	@property
	def sprite(self): return self.data[0]
	@property
	def layer(self): return self.data[1]
		
	def get_data(self):
		yield self.data

class SpriteGroup:
	""" class intended to make registration and deregistration of multiple sprites easier """
	def __init__(self, scene, **kwargs):
		self.scene = scene
		if "layer" in kwargs and "sprites" in kwargs:
			self.data = [(sprite, kwargs["layer"]) for sprite in kwargs["sprites"]]
		else:
			self.data = []
		self.registered = False
	def register(self): self.scene.sprite_system.register(self)
	def deregister(self): self.scene.sprite_system.deregister(self)
	def get_data(self):
		for data in self.data:
			yield data

class SpriteSystem:
	def __init__(self, scene, **kwargs):
		self.scene = scene
		self.data = []
		if "layer" in kwargs and "sprites" in kwargs:
			for sprite in kwargs["sprites"]:
				self.data.append((sprite, kwargs["layer"]))
	def on_update(self):
		self.scene.manager.spriterenderer.render(sprites=self.sprites)
	@property
	def sprites(self):
		self.data.sort(key=lambda data: data[1]) # sort by layer
		for sprite, layer in self.data:
			yield sprite
	def register(self, container):
		for data in container.get_data():
			if not data in self.data:
				self.data.append(data)
	def deregister(self, container):
		for data in container.get_data():
			if data in self.data:
				self.data.remove(data)