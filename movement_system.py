from constants import find_element

class Position:
	def __init__(self, **kwargs):
		if 'x' in kwargs and 'y' in kwargs:
			self.x, self.y = kwargs['x'], kwargs['y']
		elif 'position' in kwargs:
			if type(kwargs['position']) is tuple:
				self.x, self.y = kwargs['position'][0], kwargs['position'][1]
			else:
				self.x, self.y = kwargs['position'].x, kwargs['position'].y
			if 'delta' in kwargs:
				if type(kwargs['delta']) is tuple:
					self.x += kwargs['delta'][0]
					self.y += kwargs['delta'][1]
				else:
					self.x += kwargs['delta'].x
					self.y += kwargs['delta'].y
		else:
			raise KeyError('bad position constructor %s' % (repr(kwargs)))
	def __hash__(self):
		return hash((self.x, self.y))
	def __eq__(self, other):
		if type(other) is Position:
			return self.x == other.x and self.y == other.y
		else:
			return self.x == other[0] and self.y == other[1]
	def __getitem__(self, idx):
		if idx == 0:
			return self.x
		elif idx == 1:
			return self.y
		else:
			raise KeyError('bad getitem argument')
	def __repr__(self):
		return "(%d, %d)" % (self.x, self.y)
class MovementSystem:
	def __init__(self, scene):
		self.units = scene.units
		self.tiles = scene.tilemap.tiles
	def get_range(self, unit):
		DELTAS = [(-1,0),(1,0),(0,-1),(0,1)]
		EDGE = [{
			'path':[Position(position=unit.position)],
			'weight':0
		}]
		RANGE = []
		while len(EDGE) > 0:
			range_element = EDGE.pop(0)
			RANGE.append(range_element)
			for delta in DELTAS:
				candidate = {
					'path': [x for x in range_element['path']],
					'weight': range_element['weight']
				}
				candidate['path'].append(Position(position=candidate['path'][-1], delta=delta))
				if not candidate['path'][-1] in self.tiles or candidate['weight'] > unit.move_range:
					continue # ELIMINATE CANDIDATE if out of range or tile does not exist
				
				candidate['weight'] += self.tiles[candidate['path'][-1]].weight
				if not find_element(RANGE, lambda element: element['path'][-1] == candidate['path'][-1]) is None:
					continue # ELIMINATE CANDIDATEif path already exists
				
				unit_at_position = find_element(self.units, lambda element: element.position == candidate['path'][-1])
				if not unit_at_position is None and not unit_at_position is unit:
					continue # ELIMINATE CANDIDATE
				
				try:
					idx = next(idx for idx in range(len(EDGE)) if EDGE[idx]['path'][-1] == candidate['path'][-1])
					EDGE[idx] = candidate
				except StopIteration:
					EDGE.append(candidate)
			EDGE.sort(key=lambda element: element['weight'])
		return RANGE