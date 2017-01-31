import pygame
from pygame.locals import *
from pathfinderAStar import AStar
from Constants import *
from Objects import *
from Methods import *


class Character(pygame.sprite.Sprite):
    def __init__(self, rect, charset, sprite_size_rect):
        super(Character, self).__init__()
        self.collision_rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.collision_rect.x
        self.realY = self.collision_rect.y
        self.startPoint = [self.collision_rect.x, self.collision_rect.y]
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.baseSpeed = 0.08
        self.health = 3
        self.maxHealth = self.health
        self.charset = charset
        self.sprite_size_rect = sprite_size_rect
        self.image = pygame.Surface((0, 0))
        self.direction = 180
        self.last_direction = None
        self.directionLock = False
        self.set_sprite_direction()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)
        self.collision_rect.w = 20
        self.walking_phase = 1
        self.moving = False
        self.stunned = False
        self.next_location = self.collision_rect
        self.red_blink = False

    def set_sprite_direction(self):
        vx = self.vx
        vy = self.vy
        if vx == 0 and vy == 0 and self.last_direction is not None:
            self.moving = False
            self.walking_phase = 1
            return
        if self.directionLock:
            self.last_direction = -1
            if vx == 0 and vy == 0:
                self.moving = False
                self.walking_phase = 1
            else:
                self.moving = True
            self.update_sprite()
            return
        direction = 180
        if vx and vy:
            if vy < 0 and vx < 0:
                direction = 315
            if vy < 0 and vx > 0:
                direction = 45
            if vy > 0 and vx < 0:
                direction = 225
            if vy > 0 and vx > 0:
                direction = 135
        else:
            if vx > 0:
                direction = 90
            if vx < 0:
                direction = 270
            if vy > 0:
                direction = 180
            if vy < 0:
                direction = 0
        if vx == 0 and vy == 0:
            self.moving = False
            self.walking_phase = 1
        else:
            self.moving = True
        if direction == self.last_direction:
            return
        self.direction = direction
        self.last_direction = direction
        self.update_sprite()

    def update_sprite(self):
        sprite = 0
        direction = self.direction
        (width, height, desired_width) = self.sprite_size_rect
        self.walking_phase %= 4
        phase = int(self.walking_phase)
        if phase == 3:
            phase = 1

        if 45 > (direction % 360) or (direction % 360) >= 315:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 0, width-1, height))
        elif 45 <= (direction % 360) < 135:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 1, width-1, height))
        elif 135 <= (direction % 360) < 225:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 2, width-1, height))
        elif 225 <= (direction % 360) < 315:
            sprite = self.charset.subsurface(pygame.Rect(phase * width, height * 3, width-1, height))
        #sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * 24 / height, sprite.get_rect().h * 24 / height)
        sprite = aspect_scale(sprite, (desired_width, 100))
        self.image = sprite

    def update_speed(self):
        pass

    def update_position(self, time, collidables):
        if self.vx == 0 and self.vy == 0:
            return
        if time == 0:
            pygame.time.wait(1)
            time = 1
        original_x = self.realX
        original_y = self.realY
        pixellimit = 6 # should not ever be higher than drawsize / 2
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
            if object == self.collision_rect:
                continue
            if object.rect.colliderect(next_location):
                # Flats
                if self.vx > 0 and object.rect.colliderect(
                        pygame.Rect(next_location.left + next_location.w, rect.top, 0, next_location.h)):  # Left
                    self.realX = object.rect.left - next_location.w
                if self.vx < 0 and object.rect.colliderect(
                        pygame.Rect(next_location.right - next_location.w, rect.top, 0, next_location.h)):  # right
                    self.realX = object.rect.right
                if self.vy > 0 and object.rect.colliderect(
                        pygame.Rect(rect.left, next_location.top + next_location.h, next_location.w, 0)):  # top
                    self.realY = object.rect.top - next_location.h
                if self.vy < 0 and object.rect.colliderect(
                        pygame.Rect(rect.left, next_location.bottom - next_location.h, next_location.w, 0)):  # bottom
                    self.realY = object.rect.bottom
                # Corners
                if object.rect.collidepoint(rect.topleft[0] + 0.1, rect.topleft[1] + 0.1):
                    [self.realX, self.realY] = [original_x + 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomleft[0] + 0.1, rect.bottomleft[1] - 0.1):
                    [self.realX, self.realY] = [original_x + 1.1, original_y - 0.1]
                if object.rect.collidepoint(rect.topright[0] - 0.1, rect.topright[1] + 0.1):
                    [self.realX, self.realY] = [original_x - 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomright[0] - 0.1, rect.bottomright[1] - 0.1):
                    [self.realX, self.realY] = [original_x - 1.1, original_y - 0.1]

            if object.rect.collidepoint(rect.center):   # Moves you out if fully inside a block
                [self.realX, self.realY] = self.startPoint
        rect.x = self.realX
        rect.y = self.realY
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)

    def get_collision_box(self):
        return Box(self.collision_rect)

    def hit(self, damage=1):
        if self.stunned:
            return
        self.stunned = True
        self.health -= damage
        pygame.event.post(pygame.event.Event(healthEvent))
        pygame.time.set_timer(unstunEvent, 500)


class Player(Character):
    def __init__(self, rect, charset, sprite_size_rect):
        super(Player, self).__init__(rect, charset, sprite_size_rect)
        self.score = 5
        self.direction = 180
        self.displayHealth = self.health
        self.keys = 1

    def update_speed(self):
        keys = pygame.key.get_pressed()
        speed = self.baseSpeed
        if not (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT] or keys[K_LEFT]):
            self.vy = 0
            self.vx = 0
        else:
            if keys[K_UP]:
                self.vy = -speed
            if keys[K_DOWN]:
                self.vy = speed
            if keys[K_LEFT]:
                self.vx = -speed
            if keys[K_RIGHT]:
                self.vx = speed
            if keys[K_UP] == keys[K_DOWN]:
                self.vy = 0
            if keys[K_RIGHT] == keys[K_LEFT]:
                self.vx = 0
            if self.vx and self.vy:
                self.vx /= 1.4
                self.vy /= 1.4
        self.set_sprite_direction()

    def update_player(self, rect, direction):
        self.collision_rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.collision_rect.x
        self.realY = self.collision_rect.y
        self.startPoint = [self.collision_rect.x, self.collision_rect.y]
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.image = pygame.Surface((0, 0))
        self.direction = direction
        self.last_direction = None
        self.directionLock = False
        self.set_sprite_direction()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)
        self.collision_rect.w = 20
        self.walking_phase = 1
        self.moving = False
        self.stunned = False
        self.next_location = self.collision_rect
        self.red_blink = False
        self.displayHealth = self.health


class NPC(Character):
    def __init__(self, rect, charset, sprite_size_rect):
        super(NPC, self).__init__(rect, charset, sprite_size_rect)
        self.path = list()
        self.pathBricks = list()
        self.pathfinder = AStar()

    def update_path(self, grid, position, destination):
        # NPC Pathfinding
        p = self.pathfinder.find_path(grid, position, destination, 12)
        path = list()
        if p is not None:
            self.path = p.nodes
            for n in p.nodes:
                path.append(Brick(n.value[0] * drawSize, n.value[1] * drawSize, drawSize))
            self.pathBricks = path


class Stalker(NPC):
    def __init__(self, rect, charset, sprite_size_rect, player):
        super(Stalker, self).__init__(rect, charset, sprite_size_rect)
        self.baseSpeed = 0.04
        self.followPlayer = True
        self.player = player

    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            return
        speed = self.baseSpeed
        rect = self.collision_rect
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
        self.set_sprite_direction()

        if self.vx == self.vy == 0:
            self.path.pop(0)

    def update_position(self, time, collidables):
        if self.stunned:
            return
        super(Stalker, self).update_position(time, collidables)
        if self.next_location.colliderect(self.player.collision_rect):
            if not self.player.stunned:
                self.player.hit()

class Bowman(NPC):

    # Will attempt to get a straight line shot at the player, and back up if the player is too close.
    def __init__(self, rect, charset, sprite_size_rect, player):
        super(Bowman, self).__init__(rect, charset, sprite_size_rect)
        self.baseSpeed = 0.04
        self.player = player
    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            return
        speed = self.baseSpeed
        rect = self.collision_rect
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
        self.set_sprite_direction()

        if self.vx == self.vy == 0:
            self.path.pop(0)

    def update_position(self, time, collidables):
        if self.stunned:
            return
        super(Bowman, self).update_position(time, collidables)
