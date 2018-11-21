from manager import Manager, SceneBase, Resources
from constants import (TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_MAX_WEIGHT)
import sdl2
import sdl2.ext
import random
from sprite_container import SpriteContainer
random.seed()

def find_element(L, func):
	for element in L:
		if func(element):
			return element
	return None
def weight_to_color(weight):
	sprite_size = (TILE_SIZE,TILE_SIZE)
	color = int(255 * weight / (TILE_MAX_WEIGHT-1))
	if color > 255: color = 255
	return sdl2.ext.Color(color, color, color)
def map2screen(map_position):
	return (map_position[0] * TILE_SIZE, map_position[1] * TILE_SIZE)
def screen2map(screen_position):
	return (screen_position[0] // TILE_SIZE, screen_position[1] // TILE_SIZE)

class Tile:
	def __init__(self, weight):
		self.weight = weight

class TileMap(SpriteContainer):
	def __init__(self, scene, max_position):
		self.tiles = {}
		sprites = []
		for x in range(max_position[0]):
			for y in range(max_position[1]):
				map_position = (x,y)
				weight=random.randrange(0, TILE_MAX_WEIGHT)
				self.tiles[map_position] = Tile(weight)
				sprite = scene.factory.from_color(weight_to_color(weight), (TILE_SIZE,TILE_SIZE))
				sprite.position = map2screen(map_position)
				sprites.append(sprite)
				# TODO: find way to automatically update sprite color when tile weight is changed
		super().__init__(layer=0, sprites=sprites)
		self.register(scene)
	
def get_range(scene, unit):
	DELTAS = [(-1,0),(1,0),(0,-1),(0,1)]
	EDGE = [[unit.position,0]]
	RANGE = []
	
	while len(EDGE) > 0:
		position, total_weight = EDGE.pop(0)
		RANGE.append(position)
		for delta in DELTAS:
			candidate_position = (position[0]+delta[0], position[1]+delta[1])
			if not candidate_position in scene.tilemap.tiles:
				continue # ELIMINATE CANDIDATE
			
			candidate_weight = total_weight + scene.tilemap.tiles[candidate_position].weight
			if candidate_weight > unit.move_range:
				continue # ELIMINATE CANDIDATE
			
			range_candidate_match = find_element(RANGE, lambda element: element == candidate_position)
			if not range_candidate_match is None:
				continue # ELIMINATE CANDIDATE
			
			unit_at_position = find_element(scene.units, lambda element: element.position == candidate_position)
			if not unit_at_position is None and not unit_at_position is unit:
				continue # ELIMINATE CANDIDATE
				
			edge_candidate_match = find_element(EDGE, lambda element: element[0] == candidate_position)
			if edge_candidate_match is None:
				EDGE.append([candidate_position, candidate_weight])
			elif candidate_weight < edge_candidate_match[1]:
				edge_candidate_match[1] = candidate_weight
		EDGE.sort(key=lambda element: element[1])
	return RANGE

class RangeIndicator(SpriteContainer):
	def __init__(self, scene, unit):
		self.map_positions = get_range(scene, unit)
		sprites = []
		for map_position in self.map_positions:
			sprite = scene.factory.from_image(Resources.get('in-range.png'))
			sprite.position = map2screen(map_position)
			sprites.append(sprite)
		super().__init__(layer=2, sprites=sprites)
		self.register(scene)

class SelectionIndicator(SpriteContainer):
	def __init__(self, scene, unit):
		sprite = scene.factory.from_image(Resources.get('unit-selected.png'))
		sprite.position = map2screen(unit.position)
		super().__init__(layer=2, sprites=[sprite])
		self.register(scene)
class Unit(SpriteContainer):
	def __init__(self, scene, position, move_range):
		self.position = position
		self.move_range = move_range
		
		sprite = scene.factory.from_image(Resources.get("unit.png"))
		sprite.position = map2screen(position)
		super().__init__(layer=1, sprites=[sprite])
		self.register(scene)
		self.range_indicator = None
		self.selected = False
	def move_unit(self, scene, position):
		self.position = position
		self.sprite.position = map2screen(position)
	@property
	def sprite(self):
		return self.sprites[0][0]
	def select(self, scene):
		if not self.selected:
			self.selected = True
			self.selection_indicator = SelectionIndicator(scene, self)
			self.selection_indicator.register(scene)
			self.range_indicator = RangeIndicator(scene, self)
			self.range_indicator.register(scene)
	def deselect(self, scene):
		if self.selected:
			self.selected = False
			self.selection_indicator.deregister(scene)
			self.range_indicator.deregister(scene)
	def in_range(self, position):
		return position in self.range_indicator.map_positions
		
class HoverIndicator(SpriteContainer):
	def __init__(self, scene):
		sprite = scene.factory.from_image(Resources.get('tile-selection.png'))
		super().__init__(layer=2, sprites=[sprite])
	def set_position(self, scene, position):
		self.sprites[0][0].position = map2screen(position)
		self.register(scene)
		
class MyScene(SceneBase):
	def __init__(self, **kwargs):
		"""Initialization."""
		# Nothing there for us but lets call super in case we implement
		# something later on, ok?
		super().__init__(**kwargs)
		self.sprites = []
		self.tilemap = TileMap(self, screen2map((SCREEN_WIDTH, SCREEN_HEIGHT)))
		self.hover_sprite = None
		self.hover_indicator = HoverIndicator(self)
		self.units = [
			Unit(self, (2,2), 4),
			Unit(self, (2,1), 4)
		]
		self.selected_unit = None
	def on_update(self):
		self.manager.spriterenderer.render(sprites=[element[0] for element in self.sprites])
	def on_mouse_motion(self, event, x, y, dx, dy):
		self.hover_indicator.set_position(self, screen2map((x,y)))
	def get_unit_at_position(self, position):
		return find_element(self.units, lambda element: element.position == position)
	def select_unit(self, unit):
		if not self.selected_unit is None:
			self.selected_unit.deselect(self)
		self.selected_unit = unit
		if not self.selected_unit is None:
			self.selected_unit.select(self)
	def on_mouse_press(self, event, x, y, button, double):
		position = screen2map((x,y))
		if button == "LEFT":
			unit = self.get_unit_at_position(position)
			if self.selected_unit is None:
				self.select_unit(unit)
			elif not unit is None and not unit is self.selected_unit:
				self.select_unit(unit)
			elif self.selected_unit.in_range(position):
				self.selected_unit.move_unit(self, position)
				self.select_unit(None)
				
				
if __name__ == '__main__':
	m = Manager(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
	m.set_scene(scene=MyScene)
	m.run()
	