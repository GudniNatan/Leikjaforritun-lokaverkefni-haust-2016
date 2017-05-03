import pygame
from Constants import *
import Methods
from Objects import SimpleRectSprite
from Characters_sprites import Character

class Arrow(SimpleRectSprite):
    def __init__(self, rect, surface, sender, speed=1, scale=True):
        super(Arrow, self).__init__(rect, surface, scale)
        self.direction = sender.direction
        self.rotate_90_degrees_N_times(self.direction / 90)
        self.sender = sender
        self.baseSpeed = speed
        self.vx = 0
        self.vy = 0

        #Spawn and travel in direction the shooter is facing

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
                objectCollideRect = object.rect.colliderect
                #check against all characters, if it's a character that the arrow hit it will disappear and the character will be hit
                if isinstance(object, Character):
                    self.kill()
                    object.hit()

                # Flats, reverse velocity based on side hit of collidable
                if self.vx > 0 and objectCollideRect(
                        pygame.Rect(next_location.left + next_location.w, rect.top, 0, next_location.h)):  # Left
                    self.realX = object.rect.left - next_location.w
                    self.vx = -self.vx
                elif self.vx < 0 and objectCollideRect(
                        pygame.Rect(next_location.right - next_location.w, rect.top, 0, next_location.h)):  # right
                    self.realX = object.rect.right
                    self.vx = -self.vx
                if self.vy > 0 and objectCollideRect(
                        pygame.Rect(rect.left, next_location.top + next_location.h, next_location.w, 0)):  # top
                    self.realY = object.rect.top - next_location.h
                    self.vy = -self.vy
                elif self.vy < 0 and objectCollideRect(
                        pygame.Rect(rect.left, next_location.bottom - next_location.h, next_location.w, 0)):  # bottom
                    self.realY = object.rect.bottom
                    self.vy = -self.vy

                if object.rect.collidepoint(rect.center):   # Moves you out if fully inside a collidable object
                    (self.realX, self.realY) = self.startPoint
        rect.x = self.realX
        rect.y = self.realY
        self.gridPos = [self.collision_rect.centerx / drawSize, self.collision_rect.centery / drawSize]
        self.rect.midbottom = (rect.centerx, rect.bottom - 1)
