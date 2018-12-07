import sdl2
import sdl2.ext
from manager import Resources
from constants import TILE_MAX_WEIGHT
class TileTextureMap:
	def __init__(self):
		filenames = {
			0: 'tile0.png',
			1: 'tile1.png',
			2: 'tile2.png',
			3: 'tile3.png',
			4: 'tile4.png'
		}
		self.textures = []
		for key in filenames:
			self.textures.append(sdl2.ext.load_image(Resources.get(filenames[key])))
	def get_surface(self, tile):
		return self.textures[TILE_MAX_WEIGHT-tile.weight-1]

class ArrowTextureMap:
	def __init__(self):
		filenames = {
			(False, False, False, False): 'arrow_0000.png',
			(False, True,  False, False): 'arrow_0001.png',
			(False, False, True,  False): 'arrow_0010.png',
			(False, False, False, True ): 'arrow_0100.png',
			(True,  False, False, False): 'arrow_1000.png',
			(False, True,  True,  False): 'arrow_0011.png',
			(False, True,  False, True ): 'arrow_0101.png',
			(False, False, True,  True ): 'arrow_0110.png',
			(True,  True,  False, False): 'arrow_1001.png',
			(True,  False, True,  False): 'arrow_1010.png',
			(True,  False, False, True ): 'arrow_1100.png'
		}
		self.textures = {}
		for key in filenames:
			self.textures[key] = sdl2.ext.load_image(Resources.get(filenames[key]))
	def get_surface(self, key):
		if key is not None:
			return self.textures[key]