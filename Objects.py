import pygame
from Constants import *
from pygame.locals import *


class Brick(object):
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)


class Box(object):
    def __init__(self, rect):
        self.rect = rect


class Block(pygame.sprite.Sprite): # Simple block
    def __init__(self, rect, color):
        super(Block, self).__init__()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft


class SimpleSprite(pygame.sprite.Sprite):  # Molds rect to sprite
    def __init__(self, top_left_point, surface):
        super(SimpleSprite, self).__init__()
        self.image = surface
        self.rect = surface.get_rect()
        self.rect.topleft = top_left_point


class SimpleRectSprite(pygame.sprite.Sprite):  # Molds sprite to rect, either by cropping or rescaling
    def __init__(self, rect, surface, scale=False):
        super(SimpleRectSprite, self).__init__()
        self.rect = pygame.Rect(rect)
        self.image = surface
        rect.topleft = (0, 0)
        if not scale:
            self.image = surface.subsurface(rect)
        else:
            self.image = pygame.transform.scale(surface, (rect.w, rect.h))



'''class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft

    def rot_center(self, angle):
        """rotate an image while keeping its center"""
        self.rotation += angle
        rot_image = pygame.transform.rotate(self.image, self.rotation).convert_alpha()
        rot_rect = rot_image.get_rect(center=self.originalRect.center)
        rot_rect.x = self.originalRect.bottomright[0] - rot_rect.bottomright[0]
        rot_rect.y = self.originalRect.bottomright[1] - rot_rect.bottomright[1]
        self.rect = pygame.Rect(self.originalRect.x + rot_rect.x, self.originalRect.y + rot_rect.y, self.originalRect.w - rot_rect.x * 2, self.originalRect.h - rot_rect.y * 2)
        self.surface = pygame.transform.flip(rot_image, True, False)

    def update_pos(self, pos):
        self.originalRect.center = pos
        self.rect.center = pos'''


class Animation(object):
    def __init__(self, name, params=dict()):
        self.name = name
        self.params = params
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __eq__(self, other):
        return self.name == other.name


class Grid(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = []

    def make_grid(self):
        grid_size = self.grid_size
        grid = [[0 for i in range((grid_size[1] * 2) + 1)] for j in range((grid_size[0] * 2) + 1)]
        self.grid = grid

    def update_grid(self, collidables, resolution=1):
        self.make_grid()
        grid = self.grid
        for obj in collidables:
            # Faster, but less reliable
            if resolution <= 1:
                for x in xrange(obj.rect.left / drawSize, obj.rect.right / drawSize):
                    for y in xrange(obj.rect.top / drawSize, obj.rect.bottom / drawSize):
                        if 0 < x <= self.grid_size[0] * 2 and 0 < y <= self.grid_size[1] * 2:
                            grid[x][y] = 1
            # Slower, but more reliable
            else:
                for x in xrange(resolution * obj.rect.left / drawSize, resolution * obj.rect.right / drawSize):
                    for y in xrange(resolution * obj.rect.top / drawSize, resolution * obj.rect.bottom / drawSize):
                        x2 = int(x / (resolution * 1.0))
                        y2 = int(y / (resolution * 1.0))
                        if 0 <= x2 <= self.grid_size[0] * 2 and 0 <= y2 <= self.grid_size[1] * 2:
                            grid[x2][y2] = 1
        self.grid = grid
