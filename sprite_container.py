class SpriteContainer:
	def __init__(self, **kwargs):
		self.sprites = [(sprite, kwargs["layer"]) for sprite in kwargs["sprites"]]
		self.registered = False
	def register(self, scene):
		if not self.registered:
			self.registered = True
			for sprite in self.sprites:
				scene.sprites.append(sprite)
		scene.sprites.sort(key=lambda element: element[1])
	def deregister(self, scene):
		if self.registered:
			self.registered = False
			for sprite in self.sprites:
				scene.sprites.remove(sprite)
	