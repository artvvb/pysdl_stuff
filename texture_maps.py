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
			((None,None),(None,None)): 'arrow_0000.png',
			((0,1),(None,None)):       'arrow_0001.png',
			((1,0),(None,None)):       'arrow_0010.png',
			((1,0),(None,None)):       'arrow_0100.png',
			((0,1),(None,None)):       'arrow_1000.png',
			((0,1),(-1,0)):            'arrow_0011.png',
			((1,0),(0,1)):             'arrow_0101.png',
			((1,0),(1,0)):             'arrow_0110.png',
			((0,1),(0,1)):             'arrow_1001.png',
			((0,1),(1,0)):             'arrow_1010.png',
			((1,0),(0,-1)):            'arrow_1100.png'
		}
		textures = {}
		for key in filenames:
			textures[key] = sdl2.ext.load_image(Resources.get(filenames[key]))
	def get_surface(self, from_delta, to_delta):
		return self.textures[(from_delta, to_delta)]