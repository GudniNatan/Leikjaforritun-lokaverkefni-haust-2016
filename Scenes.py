import pygame
from pygame.locals import *
import os
from Constants import *
from Characters_sprites import *
from Objects import *
import random
import codecs
from math import sin


class SceneMananger(object):
    def __init__(self):
        # self.go_to(TitleScene())

        self.go_to(TitleScene())

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self, time):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class GameScene(Scene):
    def __init__(self, level):
        super(GameScene, self).__init__()
        charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
        shadow = pygame.image.load(os.path.join('images', 'shadow.png')).convert_alpha()
        walls = pygame.image.load(os.path.join('images', 'veggur2.png')).convert_alpha()
        heart = pygame.image.load(os.path.join('images', 'hearts.png')).convert_alpha()
        floor_tile = pygame.image.load(os.path.join('images', 'floor.png')).convert_alpha()
        self.sword_texture = pygame.image.load(os.path.join('images', 'swords3.png')).convert_alpha()
        self.heartTexture = heart
        self.paused = False
        self.entities = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.Group()
        self.animations = list()
        self.collidables = list()
        character_sprite_size = (16, 18, 24)
        self.player = Player(pygame.Rect(30, 30, drawSize-1, drawSize / 5 * 3), charset.subsurface(pygame.Rect(0, 72, 47, 72)), character_sprite_size)

        self.block_group = pygame.sprite.Group()
        self.background_group = pygame.sprite.Group()
        self.grid = Grid(GRID_SIZE)
        self.grand_clock = pygame.time.Clock()

        f = open(os.path.join('rooms', 'room' + str(level)) + ".txt", 'r')
        lines = f.read().splitlines()
        self.levelrect = pygame.Rect(drawSize * 12, drawSize * 4, len(lines[0]) * drawSize, len(lines) * drawSize)
        for i in xrange(len(lines)):
            for j in xrange(len(lines[i])):
                rect = pygame.Rect(j * drawSize + self.levelrect.x, i * drawSize + self.levelrect.y, drawSize, drawSize)
                if lines[i][j] == "W":
                    sliced = [["W", "W", "W"], ["W", "W", "W"], ["W", "W", "W"]]
                    if 1 < i:
                        sliced[0][1] = lines[i-1][j]
                        if j > 1:
                            sliced[0][0] = lines[i-1][j-1]
                        if j < (len(lines[i]) - 1):
                            sliced[0][2] = lines[i-1][j+1]
                    if 1 < j:
                        sliced[1][0] = lines[i][j-1]
                    if j < (len(lines[i]) - 1):
                        sliced[1][2] = lines[i][j+1]
                    if i < (len(lines)-1):
                        sliced[2][1] = lines[i+1][j]
                        if 1 < j:
                            sliced[2][0] = lines[i+1][j-1]
                        if j < (len(lines[i]) - 1):
                            sliced[2][2] = lines[i+1][j+1]
                    sprite = self.make_wall_block(walls, sliced)
                    sprite = SimpleRectSprite(rect, sprite.image, True)
                    self.block_group.add(sprite)
                if lines[i][j] == "S":
                    stalker = Stalker(pygame.Rect(rect.x, rect.y, drawSize-1, drawSize / 5 * 3), charset.subsurface(pygame.Rect(48, 72, 47, 72)), character_sprite_size, self.player)
                    self.npcs.add(stalker)
                if lines[i][j] == "P":
                    self.player.realX = j * drawSize + self.levelrect.x
                    self.player.realY = i * drawSize + self.levelrect.y
                    self.player.collision_rect.topleft = (j * drawSize + self.levelrect.x, i * drawSize + self.levelrect.y)
                if lines[i][j] != "W":
                    sprite = SimpleRectSprite(rect, floor_tile, True)
                    sprite.image = pygame.transform.rotate(sprite.image, random.randrange(0, 360, 90))
                    self.background_group.add(sprite)

        self.collidables.extend(self.block_group)

        self.entities.add(self.player, self.npcs)
        self.character_collision_boxes = [char.get_collision_box() for char in self.entities]
        self.grid.update_grid(self.collidables + self.character_collision_boxes)
        if self.character_collision_boxes:
            self.shadow = pygame.transform.scale(shadow, self.character_collision_boxes[0].rect.size)
        self.heartList = list()
        for i in xrange(self.player.maxHealth):
            rect = pygame.Rect(self.levelrect.x + (40 * i), 20, 7 * 4, 7 * 4)
            if self.player.health > i:
                self.heartList.append(SimpleRectSprite(rect, heart.subsurface(pygame.Rect(0,0,8,8)), True))
            else:
                self.heartList.append(SimpleRectSprite(rect, heart.subsurface(pygame.Rect(8*12, 0, 8, 8)), True))
        self.hearts = pygame.sprite.Group(self.heartList)
        self.swordsprite = SimpleSprite(self.player.rect.midtop, pygame.Surface((0, 0)))

    def render(self, screen):
        screen.fill(BLACK)
        self.background_group.draw(screen)

        for box in self.character_collision_boxes:
            screen.blit(self.shadow, box.rect.midleft)
        self.block_group.draw(screen)
        if not 315 >= self.player.direction >= 180:
            screen.blit(self.swordsprite.image, self.swordsprite.rect)
            self.entities.draw(screen)
        else:
            self.entities.draw(screen)
            screen.blit(self.swordsprite.image, self.swordsprite.rect)
        self.hearts.draw(screen)
        if self.paused:
            line_rect1 = pygame.Rect(screen.get_rect().w / 32 * 31, screen.get_rect().h / 16, screen.get_rect().w / 64, screen.get_rect().w / 64 * 3)
            line_rect2 = pygame.Rect(screen.get_rect().w / 32 * 30, screen.get_rect().h / 16, screen.get_rect().w / 64, screen.get_rect().w / 64 * 3)
            pygame.draw.rect(screen, RED, line_rect1)
            pygame.draw.rect(screen, RED, line_rect2)
        pygame.draw.rect(screen, BLACK, self.levelrect, 6)
        screen.blit(self.swordsprite.image, (0,0))

    def update(self, time):
        if self.paused:
            return
        for sprite in self.entities.copy().sprites():
            self.entities.change_layer(sprite, sprite.rect.centery)
        self.character_collision_boxes = [entity.get_collision_box() for entity in self.entities]
        for entity in self.entities:
            if type(entity) is not Player:
                entity.update_speed()
            entity.update_position(time, self.collidables + self.character_collision_boxes)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
            if self.paused:
                continue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.manager.go_to(TitleScene())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                if Animation("sword") not in self.animations:
                    params = {'sprite': self.sword_texture, 'phase': 0}
                    self.animations.append(Animation("sword", params))
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.player.update_speed()
            if event.type == pathfindingEvent:
                for char in self.npcs:
                    if type(char) is Stalker:
                        char.update_path(self.grid.grid, char.gridPos, self.player.gridPos)
            if event.type == updateGridEvent:
                self.grid.update_grid(self.collidables + self.character_collision_boxes)
            if event.type == animationEvent:
                # Update all active animations
                for s in self.animations:
                    if s.name == "sword":
                        self.player.directionLock = True
                        if s.phase >= 12:
                            self.swordsprite.image = pygame.Surface((0, 0))
                            self.animations.remove(s)
                            self.player.directionLock = False
                            self.player.set_sprite_direction()
                            self.player.update_sprite()
                            continue
                        if s.phase < 7:
                            if s.phase == 3:
                                pygame.event.post(pygame.event.Event(swordSwingEvent))
                            if s.phase < 2:
                                self.swordsprite.image = s.sprite.subsurface(pygame.Rect(0, 0, 25, 28))
                            else:
                                self.swordsprite.image = s.sprite.subsurface(pygame.Rect(25 * (s.phase-2), 0, 25, 28))
                            self.swordsprite.image = pygame.transform.rotate(pygame.transform.flip(self.swordsprite.image, True, False), (360 - self.player.direction) % 360 )
                        self.swordsprite.rect.topleft = self.player.rect.midtop
                        if 45 > (self.player.direction % 360) or (self.player.direction % 360) >= 315:
                            self.swordsprite.rect.left -= 16
                        elif 45 <= (self.player.direction % 360) < 135:
                            self.swordsprite.rect.left -= 5
                            self.swordsprite.rect.top += 5
                        elif 135 <= (self.player.direction % 360) < 225:
                            self.swordsprite.rect.top += 12
                            self.swordsprite.rect.left -= 6
                        elif 225 <= (self.player.direction % 360) < 315:
                            self.swordsprite.rect.left -= 16
                            self.swordsprite.rect.top += 5
                            pass
                        s.phase += 1

                    #Animations needed:
                        #Sword swing x
                        #Death
                        #Door opening
                        #Chest opening
                    if s.name == "health":
                        if s.phase >= 13:
                            self.animations.remove(s)
                            continue
                        s.sprite.image = SimpleRectSprite(pygame.Rect(s.sprite.rect), self.heartTexture.subsurface(pygame.Rect((s.phase) * 8, 0, 8, 8)), True).image
                        s.phase += 1

                for char in self.entities:
                    if char.moving:
                        char.walking_phase = char.walking_phase + 0.5
                        char.update_sprite()
                    if char.stunned:
                        if not char.red_blink:
                            pixels = pygame.PixelArray(char.image)
                            pixels.replace(BLACK, RED, 0.9)
                            char.image = pixels.surface
                            char.red_blink = True
                        else:
                            char.red_blink = False
                            char.update_sprite()
                    elif char.red_blink:
                        char.red_blink = False
                        char.update_sprite()

            if event.type == swordSwingEvent:
                boxes = list()
                for i in xrange(0, 360, 45):
                    block = pygame.Rect(0, 0, self.player.collision_rect.w, self.player.collision_rect.w)
                    if i == 0 or i == 45 or i == 315:
                        block.bottom = self.player.collision_rect.top
                    elif i == 90 or i == 270:
                        block.top = self.player.collision_rect.top
                    elif 135 <= i <= 225:
                        block.top = self.player.collision_rect.bottom
                    if 225 <= i <= 360:
                        block.right = self.player.collision_rect.left
                    elif i == 0 or i == 180:
                        block.left = self.player.collision_rect.left
                    elif 45 <= i <= 135:
                        block.left = self.player.collision_rect.right
                    boxes.append(Block(block, BLACK))
                blocks = pygame.sprite.Group()
                blocks.add(boxes[self.player.direction/45])
                blocks.add(boxes[((self.player.direction/45) + 1) % 8])
                for sprite in pygame.sprite.groupcollide(self.npcs, blocks, False, True):
                    sprite.stun()
            if event.type == unstunEvent:
                for entity in self.entities:
                    if entity.stunned:
                        entity.stunned = False
                    if entity.health <= 0:
                        self.entities.remove(entity)
                        self.npcs.remove(entity)
                        entity = None
                        #Set death animation here

            if event.type == healthEvent:
                if self.player.health > self.player.maxHealth:
                    self.player.health = self.player.maxHealth - 1
                    self.player.displayHealth = self.player.maxHealth
                if self.player.health <= 0:
                    self.manager.go_to(GameOverScene())
                if self.player.displayHealth != self.player.health:
                    params = {'sprite': self.heartList[self.player.displayHealth-1],
                              'jumpdistance': 8, 'phase': 0, }
                    self.animations.append(Animation("health", params))
                    self.player.displayHealth = self.player.health

    def make_wall_block(self, wall_texture, array_slice):
        rect = pygame.Rect(0, 0, 24, 24)
        sprite = Block(rect, BLACK)
        rotated = list(array_slice)
        blocked = ["W", "D"]
        for i2 in xrange(4):
            innerRect = pygame.Rect(0, 0, 12, 12)
            if rotated[1][0] not in blocked:
                if rotated[0][1] not in blocked:
                    # open corner
                    innerRect.topleft = (12, 12)
                else:
                    # wall facing left
                    innerRect.topleft = (24, 0)
            elif rotated[0][1] not in blocked:
                innerRect.topleft = (12, 0)
                # wall facing up
            elif rotated[0][0] not in blocked:
                innerRect.topleft = (0, 12)
            if innerRect.topleft == (0, 0):
                sprite.image.blit(pygame.transform.rotate(wall_texture.subsurface(innerRect), random.randrange(0, 360, 90)), (0, 0))
            else:
                sprite.image.blit(wall_texture.subsurface(innerRect), (0, 0))
            rotated = zip(*rotated[::-1])
            sprite.image = pygame.transform.rotate(sprite.image, -90)
        return sprite




class TitleScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.background = pygame.image.load(os.path.join('images', 'background test.png')).convert_alpha()
        self.menu_background = pygame.image.load(os.path.join('images', 'background menu.png')).convert_alpha()
        self.logo = pygame.image.load(os.path.join('images', 'logo pixel.png')).convert_alpha()
        self.logo_sprite = SimpleRectSprite(pygame.Rect(425, 325, 400, 400), self.logo, True)
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.8)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
        self.mixer.play(self.music)
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]
        self.textCoord = 300
        self.textLevel = 0

    def render(self, screen):
        screen.blit(self.background, (0,0))
        screen.blit(self.menu_background, (0,0))
        text1 = self.font.render('Lokaverkefni', True, tuple(self.color))
        text2 = self.sfont.render('> press space to start <', True, WHITE)
        screen.blit(text1, (460, 100))
        screen.blit(text2, (425, self.textCoord))
        self.logo_sprite.rect.centerx = screen.get_rect().centerx
        screen.blit(self.logo_sprite.image, self.logo_sprite.rect)

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.event.post(pygame.event.Event(QUIT))
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.mixer.fadeout(500)
                self.manager.go_to(GameScene(0))
            if event.type == animationEvent:
                for i in range(3):
                    if self.colorLevel[i]:
                        self.color[i] += i+random.randint(-i, 2)
                        if self.color[i] >= 256:
                            self.color[i] = 255
                            self.colorLevel[i] = False
                    else:
                        self.color[i] -= i+random.randint(-i, 2)
                        if self.color[i] <= 0:
                            self.color[i] = 0
                            self.colorLevel[i] = True
                self.textCoord = round(300 + sin(self.textLevel) * 10)
                self.textLevel += 0.02
                temp_background = pygame.Surface(self.background.get_size(), 0, self.background)
                temp_background.blit(self.background, (1, 0))
                temp_background.blit(self.background.subsurface(pygame.Rect(self.background.get_width()-1, 0, 1, self.background.get_height())), (0, 0))
                self.background = temp_background


class TextScrollScene(Scene):

    def __init__(self, text):
        f = codecs.open(os.path.join('text', 'text' + str(text)) + ".txt", encoding='utf-8-sig')
        lines = f.readlines()
        self.text = ""
        for i in range(len(lines)):
            lines[i] = lines[i][:-1]
            self.text += lines[i] + "\n"
        self.livetext = ""
        self.font = pygame.font.SysFont('Consolas', 20)
        self.blanks = 0
        self.text_number = text

    def render(self, screen):
        screen.fill(BLACK)
        lines = self.livetext.splitlines()
        for i in range(len(lines)):
            text1 = self.font.render(lines[i], True, WHITE)
            screen.blit(text1, (20, 50 + i*self.font.get_linesize()))

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if self.text_number == 1:
                    self.manager.go_to(TitleScene())
                else:
                    self.manager.go_to(TextScrollScene(self.text_number + 1))
            if event.type == animationEvent:
                if len(self.livetext) + self.blanks != len(self.text):
                    if self.text[len(self.livetext)+self.blanks] == "|":
                        self.blanks += 1
                    else:
                        self.livetext += self.text[len(self.livetext)+self.blanks]


class GameOverScene(Scene):
    def __init__(self):
        font = pygame.font.SysFont('Consolas', 56)
        small_font = pygame.font.SysFont('Consolas', 32)
        self.text = font.render('Game Over', True, WHITE)
        self.text2 = small_font.render('Press space to try again.', True, WHITE)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.5)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'tengsli 1.1 loop.ogg'))
        self.mixer.play(self.music, -1,)

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.text, (500, 50))
        screen.blit(self.text2, (440, 120))

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_ESCAPE):
                self.mixer.fadeout(500)
                self.manager.go_to(TitleScene())

