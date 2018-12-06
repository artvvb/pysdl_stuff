from constants import TILE_SIZE
import sdl2

class ViewportSystem:
	def __init__(self, scene, **kwargs):
		self.position = kwargs['position']
		self.size = kwargs['size']
		self.registered_objects = []
	def update_object_positions(self, dx, dy):
		for obj in self.registered_objects:
			if hasattr(obj, 'x') and hasattr(obj, 'y'):
				obj.position = (obj.position.x + dx, obj.position.y + dy)
			else:
				obj.position = (obj.position[0] + dx, obj.position[1] + dy)
	def on_key_press(self, event, sym, mod):
		deltas = {
			sdl2.SDLK_LEFT: (-TILE_SIZE//2,0),
			sdl2.SDLK_RIGHT: (TILE_SIZE//2,0),
			sdl2.SDLK_UP: (0,-TILE_SIZE//2),
			sdl2.SDLK_DOWN: (0,TILE_SIZE//2)
		}
		if sym in deltas:
			self.update_object_positions(deltas[sym][0], deltas[sym][1])
	def on_mouse_drag(self, event, x, y, dx, dy, button):
		if button == "RIGHT":
			self.update_object_positions(dx, dy)
	def register(self, obj):
		if not obj in self.registered_objects:
			self.registered_objects.append(obj)
	def deregister(self, obj):
		if obj in self.registered_objects:
			self.registered_objects.remove(obj)
	def map_to_screen_transform(self, position):
		return (
			position[0] * TILE_SIZE + self.position[0],
			position[1] * TILE_SIZE + self.position[1]
		)
	def screen_to_map_transform(self, position):
		return (
			(position[0] - self.position[0]) // TILE_SIZE,
			(position[1] - self.position[1]) // TILE_SIZE
		)
		