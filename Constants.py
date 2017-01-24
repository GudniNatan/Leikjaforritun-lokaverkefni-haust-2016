from pygame import USEREVENT

WHITE = (242, 242, 242)
BLACK = (25, 25, 25)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 102, 255)
ORANGE = (255, 153, 0)

#GRID_SIZE = [60, 60]     # Width and height of maze (can fit 355x635 if drawSize is 1)
startPoint = [14, 14]   # Starting position of generator (and player?)
drawSize = 25
halfDrawSize = drawSize / 2
window_size = window_width, window_height = 1280, 720

#Custom Events
pathfindingEvent = USEREVENT+1
updateGridEvent = USEREVENT+2
animationEvent = USEREVENT+3
swordSwingEvent = USEREVENT+4
walkEvent = USEREVENT+5
unstunEvent = USEREVENT+6
healthEvent = USEREVENT+7
actionEvent = USEREVENT+8
