from manager import Manager, SceneBase, Resources
from constants import (TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_MAX_WEIGHT)
import sdl2
import sdl2.ext
import random
random.seed()

def find_element(L, func):
	for element in L:
		if func(element):
			return element
	return None
class Tile:
	def __init__(self, position, sprites, weight):
		self.position = position
		self.sprites = sprites
		self.weight = weight
	def get_sprites(self):
		for sprite in self.sprites:
			yield sprite

def tile_factory(scene, tile_position):
	tile_weight = random.randrange(0, TILE_MAX_WEIGHT)

	sprite_size = (TILE_SIZE,TILE_SIZE)
	color = int(255 * tile_weight / (TILE_MAX_WEIGHT-1))
	if color > 255: color = 255
	sprite_color = sdl2.ext.Color(color, color, color)
	tile_sprite = scene.factory.from_color(sprite_color, sprite_size)
	tile_sprite.position = (tile_position[0] * TILE_SIZE, tile_position[1] * TILE_SIZE)
	
	scene.sprites.append((tile_sprite,0))
	
	return Tile(tile_position, [tile_sprite], tile_weight)
		
class TileMap:
	def __init__(self, scene, max_position):
		self.tiles = {}
		for x in range(max_position[0]):
			for y in range(max_position[1]):
				self.tiles[(x,y)] = tile_factory(scene, (x, y))
	def get_sprites(self):
		for key in self.tiles:
			self.tiles[key].get_sprites()
			#for sprite in self.tiles[key].sprites
			#	yield sprite
	
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

class Unit:
	def __init__(self, position, sprite, move_range):
		self.position = position
		self.move_range = move_range
		self.sprite = sprite

	
def unit_factory(scene, unit_position, unit_move_range):
	sprite_size = (TILE_SIZE, TILE_SIZE)
	unit_sprite = scene.factory.from_image(Resources.get("unit.png"))
	unit_sprite.position = (unit_position[0] * TILE_SIZE, unit_position[1] * TILE_SIZE)
	scene.sprites.append((unit_sprite, 1))
	return Unit(unit_position, unit_sprite, unit_move_range)
	
class Range:
	def __init__(self):
		self.map_positions = []
		self.sprites = []
	def get_sprites(self):
		for sprite in self.sprites:
			yield sprite
	def clear(self, scene):
		self.map_positions.clear()
		for sprite in self.sprites:
			scene.sprites.remove(find_element(scene.sprites, lambda element: element[0] == sprite))
		self.sprites.clear()
def range_factory(scene, unit):
	range = Range()
	for map_position in get_range(scene, unit):
		sprite = scene.factory.from_image(Resources.get('in-range.png'))
		sprite.position = (map_position[0] * TILE_SIZE, map_position[1] * TILE_SIZE)
		scene.sprites.append((sprite, 3))
		
		range.map_positions.append(map_position)
		range.sprites.append(sprite)
	return range
	
class MyScene(SceneBase):
	def __init__(self, **kwargs):
		"""Initialization."""
		# Nothing there for us but lets call super in case we implement
		# something later on, ok?
		super().__init__(**kwargs)
		
		# TODO: add sortable layers to sprites list entries
		
		self.sprites = []
		
		tile_max_position = (SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
		self.tilemap = TileMap(self, tile_max_position)
		
		self.hover_sprite = None
		
		self.units = []
		self.units.append(unit_factory(self, (2,2), 4))
		self.units.append(unit_factory(self, (2,1), 4))
		
		self.selected_unit = None
		self.selection_sprite = self.factory.from_image(Resources.get('unit-selected.png'))
		self.in_range = Range()
	def on_update(self):
		"""Graphical logic."""
		# use the render method from manager's spriterenderer
		self.manager.spriterenderer.render(sprites=[element[0] for element in self.sprites])
	def on_mouse_motion(self, event, x, y, dx, dy):
		if self.hover_sprite is None:
			self.hover_sprite = self.factory.from_image(Resources.get('tile-selection.png'))
			self.hover_sprite.position = ((x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE)
			self.sprites.append((self.hover_sprite, 2))
		else:
			self.hover_sprite.position = ((x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE)
	def on_mouse_press(self, event, x, y, button, double):
		if button == "LEFT":
			sprite_position = (x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE
			map_position = (x // TILE_SIZE), (y // TILE_SIZE)
			if self.selected_unit is None:
				self.selected_unit = find_element(self.units, lambda element: element.position == map_position)
				if not self.selected_unit is None:
					self.selection_sprite.position = self.selected_unit.sprite.position
					self.sprites.append((self.selection_sprite, 4))
					self.fill_range(self.selected_unit)
			else:
				if map_position in self.in_range.map_positions:
					self.selected_unit.sprite.position = sprite_position
					self.selected_unit.position = map_position
					
				# Find selection_sprite in sprites
				self.sprites.remove(find_element(self.sprites, lambda element: element[0] == self.selection_sprite))
				self.selected_unit = None
				self.in_range.clear(self)
				
	def fill_range(self, unit):
		self.in_range.clear(self)
		self.in_range = range_factory(self, unit)
if __name__ == '__main__':
	m = Manager(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
	m.set_scene(scene=MyScene)
	m.run()
	