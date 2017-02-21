import pygame
from Constants import *
from pygame.locals import *
#from Characters_sprites import Character


class Brick(object):
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)


class Box(object):
    def __init__(self, rect):
        self.rect = rect


class Block(pygame.sprite.DirtySprite): # Simple block
    def __init__(self, rect, color=BLACK):
        super(Block, self).__init__()
        self.image = pygame.Surface([rect.w, rect.h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft


class SimpleSprite(pygame.sprite.DirtySprite):  # Molds rect to sprite
    def __init__(self, top_left_point, surface):
        super(SimpleSprite, self).__init__()
        self.image = surface
        self.rect = surface.get_rect()
        self.rect.topleft = top_left_point


class SimpleRectSprite(pygame.sprite.DirtySprite):  # Molds sprite to rect, either by cropping or rescaling
    def __init__(self, rect, surface, scale=False):
        super(SimpleRectSprite, self).__init__()
        self.rect = pygame.Rect(rect)
        self.image = surface
        rect.topleft = (0, 0)
        if not scale:
            self.image = surface.subsurface(rect)
        else:
            self.image = pygame.transform.scale(surface, (rect.w, rect.h))

    def move(self, (x, y)):
        self.rect.x += x
        self.rect.y += y

    def move_to(self, (x, y)):
        self.move((x - self.rect.x, y - self.rect.y))

    def rotate_90_degrees_N_times(self, n=1):
        self.image = pygame.transform.rotate(self.image, 90 * n)
        if n % 2 == 1:
            self.rect.size = (self.rect.height, self.rect.width)



class ConjoinedSpriteGroup(pygame.sprite.DirtySprite):
    def __init__(self, spriteGroup=pygame.sprite.Group()):
        super(ConjoinedSpriteGroup, self).__init__()
        rects = [sprite.rect for sprite in spriteGroup]
        self.rect = rects[0].unionall(rects)
        self.image = pygame.Surface(self.rect.size)
        for sprite in spriteGroup:
            self.image.blit(sprite.image, (sprite.rect.x - self.rect.x, sprite.rect.y - self.rect.y))


class ActionObject(SimpleRectSprite):
    def __init__(self, rect, surface, scale=True):
        super(ActionObject, self).__init__(rect, surface, scale)

    def move(self, (x, y)):
        self.rect.x += x
        self.rect.y += y

    def move_to(self, (x, y)):
        self.move((x - self.rect.x, y - self.rect.y))

class Door(SimpleRectSprite):
    def __init__(self, rect, surface, rotation, parent_surface, locked=False, is_open=False, scale=False):
        super(Door, self).__init__(rect, surface, scale)
        self.is_open = is_open
        self.rotation = rotation
        self.locked = locked
        if is_open:
            self.toggle()
        self.parent_surface = parent_surface

    def toggle(self):
        if self.locked:
            return
        if self.is_open:
            if self.rotation % 180 == 0:
                self.move(((self.rotation-90)/90 * drawSize * 3, 0))
            else:
                self.move((0, -(self.rotation-180)/90 * drawSize * 3))
        else:
            if self.rotation % 180 == 0:
                self.move((-(self.rotation-90)/90 * drawSize * 3, 0))
            else:
                self.move((0, (self.rotation-180)/90 * drawSize * 3))
        self.is_open = not self.is_open

    def unlock(self):
        if not self.locked:
            return
        if self.rotation % 180 == 0:
            self.image = self.parent_surface.subsurface(pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()))
        else:
            self.image = self.parent_surface.subsurface(pygame.Rect(0, 0, self.image.get_height(), self.image.get_width()))
            self.image = pygame.transform.rotate(self.image, self.rotation)
        self.locked = False


class Chest(SimpleRectSprite):
    def __init__(self, top_left_point, surface, opened=False):
        self.surface = surface
        surface = surface.subsurface(pygame.Rect(0, 0, surface.get_width() / 2, surface.get_height() / 2))
        super(Chest, self).__init__(pygame.Rect(top_left_point[0], top_left_point[1], drawSize, drawSize), self.surface, True)
        self.opened = opened
        self.topleft = top_left_point

    def open(self):
        self.surface =  pygame.transform.flip(self.surface, True, False)
        super(Chest, self).__init__(pygame.Rect(self.topleft[0], self.topleft[1], drawSize, drawSize), self.surface, True)
        self.opened = True

class Arrow(SimpleRectSprite):
    def __init__(self, direction, rect, surface, sender, speed=1, scale=True):
        super(Arrow, self).__init__(rect, surface, scale)
        self.direction = round(90 * round(float(direction)/90), 2)
        self.rotate_90_degrees_N_times(self.direction / 90)
        self.sender = sender
        self.speed = speed

    def update_position(self, time, sprites, collidables):
        if self.vx == 0 and self.vy == 0:
            return
        if time == 0:
            pygame.time.wait(1)
            time = 1
        original_x = self.realX
        original_y = self.realY
        pixellimit = drawSize / 4  # should not ever be higher than drawsize / 2
        if -pixellimit < self.vx * time < pixellimit:
            self.realX += self.vx * time
        elif self.vx < 0:
            self.realX -= pixellimit
        else:
            self.realX += pixellimit
        if -pixellimit < self.vy * time < pixellimit:
            self.realY += self.vy * time
        elif self.vy < 0:
            self.realY -= pixellimit
        else:
            self.realY += pixellimit
        rect = self.collision_rect
        next_location = pygame.Rect(int(self.realX), int(self.realY), rect.w, rect.h)
        self.next_location = next_location

        for object in collidables:
            if object.rect.colliderect(next_location):
                if object == self.collision_rect:
                    continue

                if isinstance(object) is Character:
                    #Hit character
                    pass
                # Flats, reverse velocity based on side hit of collidable
                if self.vx > 0 and object.rect.colliderect(
                        pygame.Rect(next_location.left + next_location.w, rect.top, 0, next_location.h)):  # Left
                    self.realX = object.rect.left - next_location.w
                elif self.vx < 0 and object.rect.colliderect(
                        pygame.Rect(next_location.right - next_location.w, rect.top, 0, next_location.h)):  # right
                    self.realX = object.rect.right
                if self.vy > 0 and object.rect.colliderect(
                        pygame.Rect(rect.left, next_location.top + next_location.h, next_location.w, 0)):  # top
                    self.realY = object.rect.top - next_location.h
                elif self.vy < 0 and object.rect.colliderect(
                        pygame.Rect(rect.left, next_location.bottom - next_location.h, next_location.w, 0)):  # bottom
                    self.realY = object.rect.bottom

                if object.rect.collidepoint(rect.center):   # Moves you out if fully inside a collidable object
                    (self.realX, self.realY) = self.startPoint
        rect.x = self.realX
        rect.y = self.realY
        self.gridPos = [self.collision_rect.centerx / drawSize, self.collision_rect.centery / drawSize]
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)



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


class Trigger(object):  # Very similar to Animation
    def __init__(self, name, rect, params=dict()):
        super(Trigger, self).__init__()
        self.name = name
        self.rect = rect
        self.params = params
        for key, value in params.iteritems():
            setattr(self, key, value)

    def set_place(self, level):  # Will search for tags and make a big trigger box
        try:
            for i in range(len(level)):
                for j in range(len(level[i])):
                    if self.placeWhere in level[i][j]:
                        if self.rect.size == (0, 0):
                            self.rect = pygame.Rect(j * drawSize, i * drawSize, drawSize, drawSize)
                        else:
                            self.rect = self.rect.union(pygame.Rect(j * drawSize, i * drawSize, drawSize, drawSize))
        except AttributeError:
            print("The placeWhere attribute is not set in " + str(self))


class Timer(object):
    def __init__(self, event, time):
        self.event = event
        self.rate = time
        self.time = time


class Grid(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.grid = []

    def make_grid(self):
        grid_size = self.grid_size
        grid = [[0 for i in xrange(grid_size[1])] for j in xrange(grid_size[0])]
        self.grid = grid

    def update_grid(self, collidables, resolution=1):
        self.make_grid()
        grid = self.grid
        for obj in collidables:
            # Faster, but less reliable
            if resolution <= 1:
                for x in xrange(obj.rect.left / drawSize, obj.rect.right / drawSize):
                    for y in xrange(obj.rect.top / drawSize, obj.rect.bottom / drawSize):
                        if 0 < x < self.grid_size[0] and 0 < y < self.grid_size[1]:
                            grid[x][y] = 1
            # Slower, but more reliable
            else:
                for x in xrange(resolution * obj.rect.left / drawSize, resolution * obj.rect.right / drawSize):
                    for y in xrange(resolution * obj.rect.top / drawSize, resolution * obj.rect.bottom / drawSize):
                        x2 = int(x / (resolution * 1.0))
                        y2 = int(y / (resolution * 1.0))
                        if 0 <= x2 <= self.grid_size[0] and 0 <= y2 <= self.grid_size[1]:
                            grid[x2][y2] = 1
        self.grid = grid
