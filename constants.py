"""Game constants."""

TILE_SIZE = 32
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
LIMIT_FPS = 30
WINDOW_COLOR = (0, 0, 0, 255)
TILE_MAX_WEIGHT = 5

def find_element(L, func):
	for element in L:
		if func(element):
			return element
	return None