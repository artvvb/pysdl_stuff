from constants import TILE_SIZE
import sdl2

class ViewportSystem:
	def __init__(self, scene):
		#scale = (TILE_SIZE, TILE_SIZE)
		self.offset = (0,0)
	#def on_mouse(...):
	def on_key_press(self, event, sym, mod):
		print(sym, sdl2.SDLK_DOWN)
		if sym == sdl2.SDLK_DOWN:
			self.offset = (self.offset[0], self.offset[1] - TILE_SIZE)
		elif sym == sdl2.SDLK_UP:
			self.offset = (self.offset[0], self.offset[1] + TILE_SIZE)
		elif sym == sdl2.SDLK_LEFT:
			self.offset = (self.offset[0] - TILE_SIZE, self.offset[1])
		elif sym == sdl2.SDLK_RIGHT:
			self.offset = (self.offset[0] + TILE_SIZE, self.offset[1])
	#def on_mouse_drag(...):
	#def on_mouse_scroll(...):
	def map_to_screen_transform(self, position):
		return (
			position[0] * TILE_SIZE + self.offset[0],
			position[1] * TILE_SIZE + self.offset[1]
		)
	def screen_to_map_transform(self, position):
		return (
			(position[0] - self.offset[0]) // TILE_SIZE,
			(position[1] - self.offset[1]) // TILE_SIZE
		)
	#def issue_update():
		## force an update of each registered object