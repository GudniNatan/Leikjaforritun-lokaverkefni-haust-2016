import pygame
from pygame.locals import *
from pathfinderAStar import AStar
from Constants import *
from Objects import *
from Methods import *

class Character(pygame.sprite.DirtySprite):
    def __init__(self, rect, charset, sprite_size_rect):
        super(Character, self).__init__()
        self.collision_rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.collision_rect.x
        self.realY = self.collision_rect.y
        self.startPoint = [self.collision_rect.x, self.collision_rect.y]
        self.gridPos = [self.collision_rect.centerx / drawSize, self.collision_rect.centery / drawSize]
        self.baseSpeed = 0.003 * drawSize
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
        self.rect.bottom = rect.bottom - 1
        self.collision_rect.w = self.sprite_size_rect[0]
        if self.collision_rect.w < drawSize / 2 or self.collision_rect.w > drawSize:
            self.collision_rect.w = drawSize - 1
        self.walking_phase = 1
        self.moving = False
        self.stunned = False
        self.next_location = self.collision_rect
        self.red_blink = False

    def set_sprite_direction(self, lock_on_to=None):
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
        if lock_on_to is None:
            direction = 180
            direction += vec2d_jdm.Vec2D(vy, -vx).get_angle() # Please note the += 180, get angle will return negatives
        else:
            try:
                direction = 90 + CreateVectorFromCoordinates(self.collision_rect.center, lock_on_to.collision_rect.center).get_angle()
            except Exception:
                direction = 180
                direction += vec2d_jdm.Vec2D(vy, -vx).get_angle()  # Please note the += 180, get angle will return negatives
        #direction = round(15 * round(float(direction)/15), 2)

        """if vx and vy:
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
            elif vx < 0:
                direction = 270
            if vy > 0:
                direction = 180
            elif vy < 0:
                direction = 0"""
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
        try:
            """if self.going_to.topleft != (0, 0) and abs(vec2d_jdm.Vec2D(self.vx * time, self.vy * time).length()) > 1:
                if abs(CreateVectorFromCoordinates(self.collision_rect.center, self.next_location.center).length()) > abs(CreateVectorFromCoordinates(self.collision_rect.center, self.going_to.center).length()):
                    self.next_location.center = self.going_to.center
                    (self.realX, self.realY) = self.next_location.topleft
                    print "Corrected next location"""
            self.going_to
            if self.going_to.topleft != (0 ,0):
                box = pygame.Rect(self.next_location)
                box.center = self.going_to.center
                if (self.realX > box.x and self.vx > 0) or (self.realX < box.x and self.vx < 0):
                    next_location.x = box.x
                    self.realX = next_location.x
                    pass
                if (self.realY > box.y and self.vy > 0) or (self.realY < box.y and self.vy < 0):
                    next_location.y = box.y
                    self.realY = next_location.y
                    pass
        except AttributeError:
            pass

        for object in collidables:
            if object.rect.colliderect(next_location):
                if object == self.collision_rect:
                    continue
                # Flats
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
                # Corners, might not actually be needed
                """if object.rect.collidepoint(rect.topleft[0] + 0.1, rect.topleft[1] + 0.1):
                    [self.realX, self.realY] = [original_x + 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomleft[0] + 0.1, rect.bottomleft[1] - 0.1):
                    [self.realX, self.realY] = [original_x + 1.1, original_y - 0.1]
                if object.rect.collidepoint(rect.topright[0] - 0.1, rect.topright[1] + 0.1):
                    [self.realX, self.realY] = [original_x - 0.1, original_y + 1.1]
                if object.rect.collidepoint(rect.bottomright[0] - 0.1, rect.bottomright[1] - 0.1):
                    [self.realX, self.realY] = [original_x - 1.1, original_y - 0.1]"""

                if object.rect.collidepoint(rect.center):   # Moves you out if fully inside a collidable object
                    (self.realX, self.realY) = self.startPoint
        rect.x = self.realX
        rect.y = self.realY
        self.gridPos = [self.collision_rect.centerx / drawSize, self.collision_rect.centery / drawSize]
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)

    def get_collision_box(self):
        return Box(self.collision_rect)

    def set_position(self, topleft):
        self.collision_rect.topleft = topleft
        (self.realX, self.realY) = topleft
        self.gridPos = [self.collision_rect.center[0] / drawSize, self.collision_rect.center[1] / drawSize]
        self.rect.midbottom = (self.collision_rect.centerx, self.collision_rect.bottom - 1)

    def hit(self, damage=1):
        if self.stunned:
            return
        try:
            if self.godMode:
                return
        except AttributeError:
            pass
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
        self.keys = 3
        self.godMode = False

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
        self.set_sprite_direction()

    def update_player(self, rect, direction):
        self.collision_rect = rect
        self.vx = 0
        self.vy = 0
        self.realX = self.collision_rect.x
        self.realY = self.collision_rect.y
        self.startPoint = [self.collision_rect.x, self.collision_rect.y]
        self.gridPos = [self.collision_rect.centerx / drawSize, self.collision_rect.centery / drawSize]
        self.image = pygame.Surface((0, 0))
        self.direction = direction
        self.last_direction = None
        self.directionLock = False
        self.set_sprite_direction()
        self.rect = self.image.get_rect()
        self.collision_rect.w = self.sprite_size_rect[0]
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)
        self.walking_phase = 1
        self.moving = False
        self.stunned = False
        self.next_location = self.collision_rect
        self.red_blink = False
        self.displayHealth = self.health

    def update_position(self, time, collidables):
        if self.health == 0:
            self.stunned = True
            self.directionLock = True
            return
        super(Player, self).update_position(time, collidables)


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
        self.baseSpeed = self.baseSpeed * 0.6
        self.followPlayer = True
        self.player = player
        self.going_to = pygame.Rect(0, 0, 0, 0)

    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            self.going_to = pygame.Rect(0, 0, 0, 0)
            return
        speed = self.baseSpeed
        rect = self.collision_rect
        next_square = path[0].value
        """if next_square[0] < rect.right / drawSize:
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
            self.vy = 0"""
        next_square_rect = pygame.Rect(next_square[0] * drawSize, next_square[1] * drawSize, drawSize, drawSize)
        self.going_to = next_square_rect
        vector = CreateVectorFromCoordinates(self.collision_rect.center, next_square_rect.center)
        normalVector = vector.normal()
        #print abs(vec2d_jdm.Vec2D(self.vx, self.vy).get_angle_between(vector))
        if abs(vec2d_jdm.Vec2D(self.vx, self.vy).get_angle_between(vector)) > 5 :
            (self.vx, self.vy) = (normalVector.x * speed, normalVector.y * speed)
        if self.vx == self.vy == 0 or vector.length() < 10 or next_square_rect.contains(self.collision_rect):
            self.path.pop(0)
            (self.vx, self.vy) = (normalVector.x * speed, normalVector.y * speed)
        self.set_sprite_direction()

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
        self.baseSpeed *= 0.6
        self.player = player
        self.readyToShoot = False
        self.going_to = pygame.Rect(0, 0, 0, 0)
    def update_speed(self):
        # Follows path
        path = self.path
        if path is None or not path:
            self.vx = 0
            self.vy = 0
            self.going_to = pygame.Rect(0, 0, 0, 0)
            return
        speed = self.baseSpeed
        next_square = path[0].value
        next_square_rect = pygame.Rect(next_square[0] * drawSize, next_square[1] * drawSize, drawSize, drawSize)
        self.going_to = next_square_rect
        vector = CreateVectorFromCoordinates(self.collision_rect.center, next_square_rect.center)
        if abs(vec2d_jdm.Vec2D(self.vx, self.vy).get_angle_between(vector)) > 5 :
            normalVector = vector.normal()
            (self.vx, self.vy) = (normalVector.x * speed, normalVector.y * speed)
        if self.vx == self.vy == 0 or vector.length() < 10 or next_square_rect.contains(self.collision_rect):
            self.path.pop(0)
            normalVector = vector.normal()
            (self.vx, self.vy) = (normalVector.x * speed, normalVector.y * speed)
        self.set_sprite_direction(self.player)

    def update_position(self, time, collidables):
        if self.stunned:
            return
        super(Bowman, self).update_position(time, collidables)

    def findShootingSpot(self, grid, range=5):  #Bowman will try to shoot from the given range. If the player closes in on him, he will try to run away.
        if max(self.gridPos[0], self.player.gridPos[0]) - min(self.gridPos[0], self.player.gridPos[0]) >= max(self.gridPos[1], self.player.gridPos[1]) - min(self.gridPos[1], self.player.gridPos[1]):
            if self.player.gridPos[0] < self.gridPos[0]:
                self.update_path(grid, self.gridPos, [self.player.gridPos[0] + range, self.player.gridPos[1]])
            else:
                self.update_path(grid, self.gridPos, [self.player.gridPos[0] - range, self.player.gridPos[1]])
            #self.update_path(grid, self.gridPos, [self.gridPos[0], self.player.gridPos[1]])
        else:
            if self.player.gridPos[1] < self.gridPos[1]:
                self.update_path(grid, self.gridPos, [self.player.gridPos[0], self.player.gridPos[1] + range])
            else:
                self.update_path(grid, self.gridPos, [self.player.gridPos[0], self.player.gridPos[1] - range])
            #self.update_path(grid, self.gridPos, [self.player.gridPos[0], self.gridPos[1]])
        if self.path == []:
            if CreateVectorFromCoordinates(self.gridPos, self.player.gridPos).length() < range:
                self.update_path(grid, self.gridPos, [self.startPoint[0] / drawSize, self.startPoint[1] / drawSize])

    def shoot(self):
        pass
