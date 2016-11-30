import pygame
from pygame.locals import *
import os
from Constants import *
from Characters_sprites import *
from Objects import *
import random
import codecs


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
        walls = pygame.image.load(os.path.join('images', 'veggur test.png')).convert_alpha()
        self.paused = False
        self.entities = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.Group()
        self.animations = list()
        self.collidables = list()
        character_sprite_size = (16, 18, 24)
        self.player = Player(pygame.Rect(30, 30, drawSize-1, drawSize / 2), charset.subsurface(pygame.Rect(0, 72, 47, 72)), character_sprite_size)

        self.block_group = pygame.sprite.Group()
        self.grid = Grid(GRID_SIZE)
        self.grand_clock = pygame.time.Clock()

        f = open(os.path.join('rooms', 'room' + str(level)) + ".txt", 'r')
        lines = f.readlines()
        for i in xrange(len(lines)):
            for j in xrange(len(lines[i])):
                if lines[i][j] == "W":
                    rect = pygame.Rect(j * drawSize, i * drawSize, drawSize, drawSize)
                    self.block_group.add(SimpleRectSprite(rect, walls.subsurface(0, 0, drawSize, drawSize)))
                if lines[i][j] == "S":
                    stalker = Stalker(pygame.Rect(j * drawSize, i * drawSize, 15, drawSize / 2), charset.subsurface(pygame.Rect(48, 72, 47, 72)), character_sprite_size, self.player)
                    self.npcs.add(stalker)
                if lines[i][j] == "P":
                    self.player.realX = j * drawSize
                    self.player.realY = i * drawSize
                    self.player.collision_rect.topleft = (j * drawSize, i * drawSize)
                    print("p")

        '''for i in range(GRID_SIZE[0] * 2):
                block1 = (Block(pygame.Rect(i * drawSize, 0, drawSize, drawSize), BLACK))
                block2 = (Block(pygame.Rect(i * drawSize, (GRID_SIZE[1] * 2 - 1) * drawSize, drawSize, drawSize), BLACK))
                self.block_group.add(block1, block2)
        for i in range(GRID_SIZE[1] * 2):
                block1 = (Block(pygame.Rect(0, i * drawSize, drawSize, drawSize), BLACK))
                block2 = (Block(pygame.Rect((GRID_SIZE[0] * 2 - 1) * drawSize, i * drawSize, drawSize, drawSize), BLACK))
                self.block_group.add(block1, block2)'''
        self.collidables.extend(self.block_group)

        self.entities.add(self.player, self.npcs)
        self.character_collision_boxes = [char.get_collision_box() for char in self.entities]
        self.grid.update_grid(self.collidables + self.character_collision_boxes)
        if self.character_collision_boxes:
            self.shadow = pygame.transform.scale(shadow, self.character_collision_boxes[0].rect.size)

    def render(self, screen):
        screen.fill(WHITE)
        for box in self.character_collision_boxes:
            screen.blit(self.shadow, box.rect.midleft)

        self.block_group.draw(screen)
        self.entities.draw(screen)
        if self.paused:
            line_rect1 = pygame.Rect(screen.get_rect().w / 32 * 31, screen.get_rect().h / 16, screen.get_rect().w / 64, screen.get_rect().w / 64 * 3)
            line_rect2 = pygame.Rect(screen.get_rect().w / 32 * 30, screen.get_rect().h / 16, screen.get_rect().w / 64, screen.get_rect().w / 64 * 3)
            pygame.draw.rect(screen, RED, line_rect1)
            pygame.draw.rect(screen, RED, line_rect2)

    def update(self, time):
        if self.paused:
            return
        for sprite in self.entities.sprites():
            self.entities.change_layer(sprite, sprite.rect.centery)
        self.character_collision_boxes = [entity.get_collision_box() for entity in self.entities]
        for entity in self.entities:
            if type(entity) is not Player:
                entity.update_speed()
            entity.update_position(time, self.collidables + self.character_collision_boxes)
        if self.player.health <= 0:
            self.manager.go_to(GameOverScene())

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
                pygame.event.post(pygame.event.Event(swordSwingEvent))
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
                    '''if s.name == "sword":
                        if sword.rotation < s.end and s.direction == self.player.direction:
                            sword.display = True
                            sword.rot_center(50)
                        else:
                            sword.display = False
                            sword.rotation = 0
                            animations.remove(s)'''
                    #Animations needed:
                        #Sword swing
                        #Death
                        #Door opening
                        #Chest opening
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
                    if sprite.health <= 0:
                        self.entities.remove(sprite)
                        #Set death animation here

                '''if Animation("sword") not in animations:
                    sword.rotation = thePlayer.direction - 25
                    params = {'direction': thePlayer.direction, 'end': thePlayer.direction + 100}
                    animations.append(Animation("sword", params))'''
            if event.type == unstunEvent:
                for entity in self.entities:
                    if entity.stunned:
                        entity.stunned = False


class TitleScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.mixer = pygame.mixer.Channel(0)
        self.mixer.set_volume(0.8)
        self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
        self.mixer.play(self.music)
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]

    def render(self, screen):
        screen.fill(BLACK)
        text1 = self.font.render('Lokaverkefni', True, tuple(self.color))
        text2 = self.sfont.render('> press space to start <', True, WHITE)
        screen.blit(text1, (450, 50))
        screen.blit(text2, (420, 350))

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
            if event.type == KEYDOWN and event.key == K_SPACE or event.key == K_ESCAPE:
                self.manager.go_to(TitleScene())

