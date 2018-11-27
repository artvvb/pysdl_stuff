from manager import Manager, SceneBase, Resources
from constants import (TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_MAX_WEIGHT)
import sdl2
import sdl2.ext
import random
from sprite_system import Sprite, SpriteGroup, SpriteSystem
random.seed()

LAYERS = {
	"HoverIndicator": 3,
	"RangeIndicatorFactory": 2,
	"UnitGfx": 1,
	"TileMap": 0
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
def map2screen(map_position):
	return (map_position[0] * TILE_SIZE, map_position[1] * TILE_SIZE)
def screen2map(screen_position):
	return (screen_position[0] // TILE_SIZE, screen_position[1] // TILE_SIZE)

class Tile:
	def __init__(self, weight):
		self.weight = weight

class TileMap(SpriteGroup):
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
		super().__init__(scene, layer=LAYERS[self.__class__.__name__], sprites=sprites)
		self.register()
	
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

class RangeIndicatorFactory:
	def __init__(self, scene):
		self.scene = scene
	def from_position(self, position):
		sprite = self.scene.factory.from_image(Resources.get('in-range.png'))
		sprite.position = map2screen(position)
		return (sprite, get_layer(self))
		
class UnitGfx:
	def __init__(self, scene, unit):
		# TODO: Some worry about memory leaks from this nonsense:
		self.unit = unit
		self.scene = scene
		
		self.unit_indicator = Sprite(self.scene, layer=get_layer(self), sprite=self.scene.factory.from_image(Resources.get("unit.png")))
		self.selected_indicator = Sprite(self.scene, layer=get_layer(self), sprite=self.scene.factory.from_image(Resources.get("unit-selected.png")))
		self.moved_indicator = Sprite(self.scene, layer=get_layer(self), sprite=self.scene.factory.from_image(Resources.get("unit-moved.png")))
		self.range_indicator_group = SpriteGroup(self.scene)
		self.range_indicator_factory = lambda position: self.scene.range_indicator_factory.from_position(position)
	def update_range(self):
		if self.unit.selected:
			self.range_indicator_group.deregister()
			self.range_indicator_group.data.clear()
			self.range_indicator_group.data = [ self.range_indicator_factory(position) for position in self.unit.range]
			self.range_indicator_group.register()
		else:
			self.range_indicator_group.deregister()
	def update(self):
		self.deregister()
		self.unit_indicator.sprite.position = map2screen(self.unit.position)
		self.selected_indicator.sprite.position = map2screen(self.unit.position)
		self.moved_indicator.sprite.position = map2screen(self.unit.position)
		self.update_range()
		self.register()
		
	def register(self):
		self.update_range()
		
		if self.unit.moved:
			self.moved_indicator.register()
		else:
			self.unit_indicator.register()
			
		if self.unit.selected:
			self.selected_indicator.register()
			
	def deregister(self):
		self.unit_indicator.deregister()
		self.selected_indicator.deregister()
		self.moved_indicator.deregister()
		self.range_indicator_group.deregister()
		
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
		
class HoverIndicator(SpriteGroup):
	def __init__(self, scene):
		super().__init__(scene, layer=get_layer(self), sprites=[scene.factory.from_image(Resources.get('tile-selection.png'))])
	def on_mouse_motion(self, event, x, y, dx, dy):
		self.set_position(screen2map((x,y)))
	def set_position(self, position):
		for sprite, layer in self.data:
			sprite.position = map2screen(position)
		self.register()
		
class MyScene(SceneBase):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.sprite_system = SpriteSystem(self)
		self.range_indicator_factory = RangeIndicatorFactory(self)
		self.tilemap = TileMap(self, screen2map((SCREEN_WIDTH, SCREEN_HEIGHT)))
		self.hover_sprite = None
		self.hover_indicator = HoverIndicator(self)
		self.units = [
			Unit(self, (2,2), 4),
			Unit(self, (2,1), 4)
		]
		self.selected_unit = None
		
		for unit in self.units:
			unit.on_init()
	def on_update(self):
		self.sprite_system.on_update()
		
	def on_mouse_motion(self, event, x, y, dx, dy):
		self.hover_indicator.on_mouse_motion(event, x, y, dx, dy)
		
	def get_unit_at_position(self, position):
		return find_element(self.units, lambda element: element.position == position)
	def select_unit(self, unit):
		if not self.selected_unit is None:
			self.selected_unit.deselect()
		self.selected_unit = unit
		if not self.selected_unit is None:
			self.selected_unit.select()
	def on_mouse_press(self, event, x, y, button, double):
		print('hey there')
		position = screen2map((x,y))
		if button == "LEFT":
			unit = self.get_unit_at_position(position)
			if self.selected_unit is None:
				self.select_unit(unit)
			elif not unit is None and not unit is self.selected_unit:
				self.select_unit(unit)
			elif position in self.selected_unit.range:
				self.selected_unit.move_unit(position)
				self.select_unit(None)
	def end_turn(self):
		for unit in self.units:
			unit.on_end_turn()
	def on_key_press(self, event, sym, mod):
		if sym == ord('\r'):
			if mod.alt: return
			if mod.ctrl: return
			if mod.shift: return
			self.end_turn()
				
if __name__ == '__main__':
	m = Manager(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
	m.set_scene(scene=MyScene)
	m.run()
	