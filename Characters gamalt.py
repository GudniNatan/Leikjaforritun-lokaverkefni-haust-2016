import pygame
from pygame.locals import *
from pathfinderAStar import AStar
from Constants import *
from Objects import *


class Character(object):
    def __init__(self, rect):
        self.rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.rect.x
        self.realY = self.rect.y
        self.startPoint = [self.rect.x, self.rect.y]
        self.gridPos = [self.rect.center[0] / drawSize, self.rect.center[1] / drawSize]
        self.baseSpeed = 0.08
        self.health = 3

    def update_speed(self):
        pass

    def update_position(self, time, collidables):
        if time > 20:
            time = 20
        if time == 0:
            pygame.time.wait(1)
            time = 1
        self.update_speed()
        original_x = self.realX
        original_y = self.realY
        self.realX += self.vx * time
        self.realY += self.vy * time
        next_location = pygame.Rect(int(self.realX), int(self.realY), self.rect.w, self.rect.h)

        for object in collidables:
            if (max(self.rect.center[0], object.rect.center[0]) - min(self.rect.center[0], object.rect.center[0]) > max(self.rect.w, object.rect.w) * 2 or
                    max(self.rect.center[1], object.rect.center[1]) - min(self.rect.center[1], object.rect.center[1]) > max(self.rect.h, object.rect.h) * 2):
                continue
            if object.rect.colliderect(next_location):
                    # Flats
                    if self.vx > 0 and object.rect.colliderect(pygame.Rect(next_location.left + next_location.w, self.rect.top, 0, next_location.h)):    # Left
                        self.realX = original_x
                    if self.vx < 0 and object.rect.colliderect(pygame.Rect(next_location.right - next_location.w, self.rect.top, 0, next_location.h)):    # right
                        self.realX = original_x
                    if self.vy > 0 and object.rect.colliderect(pygame.Rect(self.rect.left, next_location.top + next_location.h, next_location.w, 0)):    # top
                        self.realY = original_y
                    if self.vy < 0 and object.rect.colliderect(pygame.Rect(self.rect.left, next_location.bottom - next_location.h, next_location.w, 0)):    # bottom
                        self.realY = original_y
                    # Corners
                    if object.rect.collidepoint(self.rect.topleft[0] + 0.1, self.rect.topleft[1] + 0.1):
                        [self.realX, self.realY] = [original_x + 0.1, original_y + 1.1]
                    if object.rect.collidepoint(self.rect.bottomleft[0] + 0.1, self.rect.bottomleft[1] - 0.1):
                        [self.realX, self.realY] = [original_x + 1.1, original_y - 0.1]
                    if object.rect.collidepoint(self.rect.topright[0] - 0.1, self.rect.topright[1] + 0.1):
                        [self.realX, self.realY] = [original_x - 0.1, original_y + 1.1]
                    if object.rect.collidepoint(self.rect.bottomright[0] - 0.1, self.rect.bottomright[1] - 0.1):
                        [self.realX, self.realY] = [original_x - 1.1, original_y - 0.1]

            if object.rect.collidepoint(self.rect.center):   # Moves you out if fully inside a block
                [self.realX, self.realY] = self.startPoint
        self.rect.x = self.realX
        self.rect.y = self.realY
        self.gridPos = [self.rect.center[0] / drawSize, self.rect.center[1] / drawSize]


class Player(Character):
    def __init__(self, rect, charset):
        super(Player, self).__init__(rect)
        self.score = 5
        self.kitCount = 0
        self.direction = 180
        self.charset = charset
        self.sprite = pygame.Surface((0, 0))
        self.set_sprite()

    def set_sprite(self):
        sprite = 0
        direction = self.direction
        height = 18
        if 45 > (direction % 360) or (direction % 360) >= 315:
            sprite = self.charset.subsurface(pygame.Rect(0, height * 0, 16, 18))
        elif 225 <= (direction % 360) < 315:
            sprite = self.charset.subsurface(pygame.Rect(0, height * 1, 16, 18))
        elif 135 <= (direction % 360) < 225:
            sprite = self.charset.subsurface(pygame.Rect(0, height * 2, 16, 18))
        elif 45 <= (direction % 360) < 135:
            sprite = self.charset.subsurface(pygame.Rect(0, height * 3, 16, 18))
        sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * 24 / height, sprite.get_rect().h * 24 / height))
        self.sprite = sprite

    def update_speed(self):
        keys = pygame.key.get_pressed()
        speed = self.baseSpeed
        if not (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT]):
            self.vy = 0
            self.vx = 0
        else:
            if keys[K_UP]:
                self.vy = -speed
                self.direction = 0
            if keys[K_DOWN]:
                self.vy = speed
                self.direction = 180
            if keys[K_LEFT]:
                self.vx = -speed
                self.direction = 90
            if keys[K_RIGHT]:
                self.vx = speed
                self.direction = 270
            if keys[K_UP] and keys[K_RIGHT]:
                self.direction = 315
            if keys[K_UP] and keys[K_LEFT]:
                self.direction = 45
            if keys[K_DOWN] and keys[K_RIGHT]:
                self.direction = 225
            if keys[K_DOWN] and keys[K_LEFT]:
                self.direction = 135
            if keys[K_UP] == keys[K_DOWN]:
                self.vy = 0
            if keys[K_RIGHT] == keys[K_LEFT]:
                self.vx = 0
            self.set_sprite()


class NPC(Character):
    def __init__(self, rect):
        super(NPC, self).__init__(rect)
        self.path = list()
        self.pathBricks = list()
        self.pathfinder = AStar()

    def update_path(self, grid, position, destination):
        # NPC Pathfinding
        p = self.pathfinder.find_path(grid, position, destination, 8)
        path = list()
        if p is not None:
            self.path = p.nodes
            for n in p.nodes:
                path.append(Brick(n.value[0] * drawSize, n.value[1] * drawSize, drawSize))
            self.pathBricks = path


class Stalker(NPC):
    def __init__(self, rect):
        super(Stalker, self).__init__(rect)
        self.baseSpeed = 0.03

    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            return
        speed = self.baseSpeed
        rect = self.rect
        next_square = path[0].value
        if next_square[0] < rect.right / drawSize:
            self.vx = -speed
        elif next_square[0] > rect.left / drawSize:
            self.vx = speed
        else:
            self.vx = 0
        if next_square[1] < rect.bottom / drawSize:
            self.vy = -speed
        elif next_square[1] > rect.top / drawSize:
            self.vy = speed
        else:
            self.vy = 0

        '''if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7
            self.vy *= 0.7'''
        if self.vx == self.vy == 0:
            self.path.pop(0)
