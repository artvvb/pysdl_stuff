from manager import Manager, SceneBase, Resources
from constants import (TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_MAX_WEIGHT)
import sdl2
import sdl2.ext
import sdl2.surface
import random
from sprite_system import SpriteFactory, SpriteHandler, SpriteGroup, SpriteSystem, SurfaceFactory
from viewport_system import ViewportSystem
from texture_maps import TileTextureMap, ArrowTextureMap
from movement_system import MovementSystem, Position
from constants import find_element
random.seed()

LAYERS = {
	"HoverIndicatorGfx": 5,
	"UnitGfx": [4,3,2,1],
	"TileMapGfx": [0,1]
}
def get_layer(obj): return LAYERS[obj.__class__.__name__]

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
			self.scene.tile_texture_map,
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


		
class UnitGfx:
	def __init__(self, scene, unit):
		self.unit = unit
		self.scene = scene
		factory = scene.sprite_factory
		surface_factory = scene.surface_factory
		
		surf = scene.surface_factory.from_image('unit.png')
		#sdl2.surface.SDL_SetColorKey(surf, True, sdl2.ext.Color(255,0,0))
		self.unit_indicator = factory.from_surface(
			surf,
			[unit.position],
			get_layer(self)[0]
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
	def update_range(self):
		positions = [x['path'][-1] for x in self.unit.range]
		if self.scene.hover_indicator.position is None:
			key_func = lambda position: None
		elif not self.scene.hover_indicator.position in positions:
			key_func = lambda position: (False,False,False,False)
		else:
			hover_path = next(element['path'] for element in self.unit.range if element['path'][-1] == self.scene.hover_indicator.position)
			keys = {}
			for idx in range(len(hover_path)):
				deltas = [hover_path[idx]-hover_path[idx+d] for d in (-1,1) if idx+d >= 0 and idx+d < len(hover_path)]
				keys[hover_path[idx]] = ((0,1) in deltas, (0,-1) in deltas, (-1,0) in deltas, (1,0) in deltas) ## (U,D,L,R)
			for position in positions:
				if not position in keys:
					keys[position] = (False,False,False,False)
			key_func = lambda position: keys[position]	
		self.range_indicator_group = self.scene.sprite_factory.from_map(
			self.scene.arrow_texture_map,
			key_func,
			positions = positions,
			depth = get_layer(self)[3]
		)
		self.range_indicator_group.register()
	def update(self):
		self.unit_indicator.deregister()
		self.selected_indicator.deregister()
		self.moved_indicator.deregister()
		if not self.range_indicator_group is None:
			self.range_indicator_group.deregister()
		
		if self.unit.moved:
			self.moved_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.moved_indicator.register()
		elif self.unit.selected:
			self.selected_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.selected_indicator.register()
			self.update_range()
		else:
			self.unit_indicator.sprite.position = self.scene.map_to_screen_transform(self.unit.position)
			self.unit_indicator.register()
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
		self.range = self.scene.movement_system.get_range(self)
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
			self.range = self.scene.movement_system.get_range(self)
			self.gfx.update()
	def deselect(self):
		if self.selected:
			self.selected = False
		self.gfx.update()
	def in_range(self, position):
		return position in [x['path'][-1] for x in self.range]
		
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
		if self.scene.selected_unit is not None:
			self.scene.selected_unit.gfx.update()
		
class MyScene(SceneBase):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.viewport_system = ViewportSystem(self, position=(0,0), size=(SCREEN_WIDTH,SCREEN_HEIGHT))
		self.map_to_screen_transform = lambda position: self.viewport_system.map_to_screen_transform(position)
		self.screen_to_map_transform = lambda position: self.viewport_system.screen_to_map_transform(position)
		
		self.sprite_system = SpriteSystem(self)
		self.sprite_factory = SpriteFactory(self)
		self.surface_factory = SurfaceFactory()
		
		self.tile_texture_map = TileTextureMap()
		self.arrow_texture_map = ArrowTextureMap()
		
		#self.range_indicator_factory = RangeIndicatorFactory(self)
		self.tilemap = TileMap(self, self.screen_to_map_transform((SCREEN_WIDTH, SCREEN_HEIGHT)))
		self.hover_indicator = HoverIndicator(self)
		self.units = []
		
		self.movement_system = MovementSystem(self)
		
		self.units.append(Unit(self, (2,2), 4))
		self.units.append(Unit(self, (2,1), 4))
		self.selected_unit = None
		
		self.systems = [ # call order matters...
			self.viewport_system,
			self.sprite_system
		]
		
		for unit in self.units:
			unit.on_init()
			
		self.turn = 0
	def on_update(self):
		for unit in self.units:
			if not unit.moved:
				break
		else:
			self.end_turn()
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
			elif self.selected_unit.in_range(position):
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
		print('End Turn %d' % self.turn)
		self.turn += 1
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
	