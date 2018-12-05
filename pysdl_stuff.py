from manager import Manager, SceneBase, Resources
from constants import (TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_MAX_WEIGHT)
import sdl2
import sdl2.ext
import random
from sprite_system import SpriteFactory, SpriteHandler, SpriteGroup, SpriteSystem
from viewport_system import ViewportSystem
random.seed()

LAYERS = {
	"HoverIndicatorGfx": 5,
	"UnitGfx": [4,3,2,1],
	"TileMapGfx": [0,1]
}
def get_layer(obj): return LAYERS[obj.__class__.__name__]

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

class Tile:
	def __init__(self, weight):
		self.weight = weight

class TileMapGfx:
	def __init__(self, scene, tile_map):
		self.scene = scene
		sprites = []
		self.border = scene.sprite_factory.from_color(
			sdl2.ext.Color(0,0,255), # BLUE
			(SCREEN_WIDTH + TILE_SIZE, SCREEN_HEIGHT + TILE_SIZE),
			screen_position = (-TILE_SIZE//2, -TILE_SIZE//2),
			depth = get_layer(self)[0]
		)
		self.border.register()
		self.sprite_group = scene.sprite_factory.from_map(
			lambda position: tile_map.tiles[position],
			positions = tile_map.tiles,
			depth = get_layer(self)[1]
		)
		self.sprite_group.register()																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																													
	def update(self):
		pass
class TileMap:
	def __init__(self, scene, max_position):
		self.scene = scene
		self.tiles = {}
		sprites = []
		for x in range(max_position[0]):
			for y in range(max_position[1]):
				self.tiles[(x,y)] = Tile(random.randrange(0, TILE_MAX_WEIGHT))
		self.gfx = TileMapGfx(self.scene, self)
	
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

class UnitGfx:
	def __init__(self, scene, unit):
		# TODO: Some worry about memory leaks from this nonsense:
		self.unit = unit
		self.scene = scene
		factory = scene.sprite_factory
		
		self.unit_indicator = factory.from_image(
			'unit.png',
			position = unit.position,
			depth = get_layer(self)[0]
		)
		
		self.selected_indicator = factory.from_image(
			'unit-selected.png',
			position = unit.position,
			depth = get_layer(self)[1]
		)
		
		self.moved_indicator = factory.from_image(
			'unit-moved.png',
			position = unit.position,
			depth = get_layer(self)[2]
		)
		
		self.range_indicator_group = None
	def update(self):
		self.unit_indicator.deregister()
		self.selected_indicator.deregister()
		self.moved_indicator.deregister()
		if not self.range_indicator_group is None:
			self.range_indicator_group.deregister()
		
		if self.unit.moved:
			self.moved_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.moved_indicator.register()
		else:
			self.unit_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.unit_indicator.register()
		if self.unit.selected:
			self.selected_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.selected_indicator.register()
			
			self.range_indicator_group = self.scene.sprite_factory.from_image(
				'in-range.png',
				positions = self.unit.range,
				depth = get_layer(self)[3]
			)
			self.range_indicator_group.register()
class Unit:
	def __init__(self, scene, position, move_range):
		self.scene = scene
		self.position = position
		self.move_range = move_range
		self.moved = False
		self.selected = False
		self.range = None
		self.gfx = UnitGfx(self.scene, self)
	def on_init(self):
		self.range = get_range(self.scene, self)
		self.gfx.update()
	def on_end_turn(self):
		if self.moved:
			self.moved = False
		self.gfx.update()
	def move_unit(self, position):
		if not self.moved:
			self.position = position
			self.gfx.update()
			self.moved = True
	def select(self):
		if not self.selected and not self.moved:
			self.selected = True
			self.range = get_range(self.scene, self)
			self.gfx.update()
	def deselect(self):
		if self.selected:
			self.selected = False
		self.gfx.update()
	def in_range(self, position):
		return position in self.range
		
class HoverIndicatorGfx:
	def __init__(self, scene, hover_indicator):
		self.hover_indicator = hover_indicator
		self.scene = scene
		self.sprite_handler = scene.sprite_factory.from_image(
			'tile-selection.png',
			position = None,
			depth = get_layer(self)
		)
	def update(self):
		self.sprite_handler.deregister()
		self.sprite_handler.sprite.position = self.scene.map_to_screen_transform(self.hover_indicator.position)
		self.sprite_handler.register()
class HoverIndicator:
	def __init__(self, scene):
		self.scene = scene
		self.gfx = HoverIndicatorGfx(self.scene, self)
		self.position = None
	def update(self, event, position):
		self.position = position
		self.gfx.update()
		
class MyScene(SceneBase):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.viewport_system = ViewportSystem(self, position=(0,0), size=(SCREEN_WIDTH,SCREEN_HEIGHT))
		self.map_to_screen_transform = lambda position: self.viewport_system.map_to_screen_transform(position)
		self.screen_to_map_transform = lambda position: self.viewport_system.screen_to_map_transform(position)
		
		self.sprite_system = SpriteSystem(self)
		self.sprite_factory = SpriteFactory(self)
		
		#self.range_indicator_factory = RangeIndicatorFactory(self)
		self.tilemap = TileMap(self, self.screen_to_map_transform((SCREEN_WIDTH, SCREEN_HEIGHT)))
		self.hover_indicator = HoverIndicator(self)
		self.units = [
			Unit(self, (2,2), 4),
			Unit(self, (2,1), 4)
		]
		self.selected_unit = None
		
		self.systems = [ # call order matters...
			self.viewport_system,
			self.sprite_system
		]
		
		for unit in self.units:
			unit.on_init()
	def on_update(self):
		for system in self.systems:
			op = getattr(system, "on_update", None)
			if op is not None and callable(op):
				op()
	def on_mouse_motion(self, event, x, y, dx, dy):
		self.hover_indicator.update(event, self.screen_to_map_transform((x,y)))
		for system in self.systems:
			op = getattr(system, "on_mouse_motion", None)
			if op is not None and callable(op):
				op(event, x, y, dx, dy)
	def get_unit_at_position(self, position):
		return find_element(self.units, lambda element: element.position == position)
	def select_unit(self, unit):
		if not self.selected_unit is None:
			self.selected_unit.deselect()
		self.selected_unit = unit
		if not self.selected_unit is None:
			self.selected_unit.select()
	def on_mouse_press(self, event, x, y, button, double):
		position = self.screen_to_map_transform((x,y))
		if button == "LEFT":
			unit = self.get_unit_at_position(position)
			if self.selected_unit is None:
				self.select_unit(unit)
			elif not unit is None and not unit is self.selected_unit:
				self.select_unit(unit)
			elif position in self.selected_unit.range:
				self.selected_unit.move_unit(position)
				self.select_unit(None)
		for system in self.systems:
			op = getattr(system, "on_mouse_press", None)
			if op is not None and callable(op):
				op(event, x, y, button, double)
	def on_mouse_drag(self, event, x, y, dx, dy, button):
		for system in self.systems:
			op = getattr(system, "on_mouse_drag", None)
			if op is not None and callable(op):
				op(event, x, y, dx, dy, button)
	def end_turn(self):
		for unit in self.units:
			unit.on_end_turn()
	def on_key_press(self, event, sym, mod):
		if sym == ord('\r'):
			if mod.alt: return
			if mod.ctrl: return
			if mod.shift: return
			self.end_turn()
		for system in self.systems:
			op = getattr(system, "on_key_press", None)
			if op is not None and callable(op):
				op(event, sym, mod)
				
if __name__ == '__main__':
	m = Manager(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
	m.set_scene(scene=MyScene)
	m.run()
	