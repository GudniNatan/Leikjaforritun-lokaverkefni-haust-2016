import pygame
from pygame.locals import *
import os
from Constants import *
from Characters_sprites import *
from Methods import *
from Objects import *
from Other_sprites import *
import random
import codecs
import threading
import copy
from math import sin
from rooms import get_room

class SceneManager(object):
    def __init__(self, screen):
        self.screen = screen
        self.go_to(TitleScene())
        self.room = list()

    def go_to(self, scene):
        if type(scene) is GameScene:  # If the scene already exists
            try:
                self.scene = self.room[scene.roomNumber]
                print("Found room")
            except IndexError:
                self.scene = scene
                print("Creating scene")
            self.scene.manager = self
            self.scene.load_level()
        else:
            self.scene = scene
            self.scene.manager = self

    def generate_rooms(self):  # Idea is to process everything at once so we can switch between rooms with ease.
        self.room = list()
        i = 0
        while True:  # Generate all possible rooms. if there is a gap anywhere, the generator will stop there.
            try:
                get_room(i)
                self.room.append(GameScene(i))
            except KeyError:
                break
            i += 1
        print("Generated " + str(i) + " rooms.")

class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self, time):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError

    def load_level(self):
        pass


class GameScene(Scene):
    def __init__(self, room=0):
        super(GameScene, self).__init__()
        lines = get_room(room)
        self.lines = lines
        self.nextScene = None
        self.nextSceneThread = None
        self.roomNumber = room
        lineLength = len(max(lines, key=len))
        charset = pygame.image.load(os.path.join('images', 'charset3.png')).convert_alpha()
        shadow = pygame.image.load(os.path.join('images', 'shadow.png')).convert_alpha()
        walls = pygame.image.load(os.path.join('images', 'veggur2.png')).convert_alpha()
        heart = pygame.image.load(os.path.join('images', 'hearts.png')).convert_alpha()
        floor_tile = pygame.image.load(os.path.join('images', 'floor.png')).convert_alpha()
        door = pygame.image.load(os.path.join('images', 'hurd2.png')).convert_alpha()
        self.arrowSprite = pygame.image.load(os.path.join('images', 'arrow.png')).convert_alpha()
        self.sword_texture = aspect_scale(pygame.image.load(os.path.join('images', 'swords3.png')).convert_alpha(), (100000, drawSize))
        self.sword_icon = pygame.image.load(os.path.join('images', 'sword icon.png')).convert_alpha()
        self.keyTexture = pygame.image.load(os.path.join('images', 'Small_Key_MC.gif')).convert_alpha()
        self.heartTexture = heart
        self.paused = False
        self.entities = pygame.sprite.LayeredUpdates()
        self.npcs = pygame.sprite.Group()
        self.animations = list()
        self.collidables = list()
        charset = aspect_scale(charset, (drawSize * 16, 100000)) # Even though it shouldn't, this does affect character width and therefore AI
        character_sprite_size = (charset.get_width() / 18, charset.get_height() / 8, drawSize * 0.9)
        charsetRect = charset.get_rect()
        self.player = Player(pygame.Rect(30, 30, drawSize-1, drawSize / 5 * 3), charset.subsurface(pygame.Rect(0, charsetRect.bottom - (charsetRect.height / 8 * 4), charset.get_width() / 18 * 3, charsetRect.height / 8 * 4)), character_sprite_size)
        self.block_group = pygame.sprite.OrderedUpdates()
        self.action_group = pygame.sprite.RenderUpdates()
        self.background_group = pygame.sprite.Group()
        self.grand_clock = pygame.time.Clock()
        self.levelrect = pygame.Rect(0, 0, lineLength * drawSize, len(lines) * drawSize)
        self.gameSurface = pygame.Surface(self.levelrect.size)
        self.camera = pygame.Rect(0, 0, min(window_width, self.gameSurface.get_width()), min(window_height, self.gameSurface.get_height()))


        #Custom event timers
        self.timers = list()

        #Grid
        self.grid = Grid([lineLength, len(lines)])
        screenrect = pygame.Rect(0, 0, window_width, window_height)
        self.cameraLeeway = pygame.Rect(0, 0, window_width / (drawSize / 8), window_height / (drawSize / 8))
        self.cameraLeeway.center = screenrect.center
        self.levelrect.center = screenrect.center
        self.doors = list()
        """ Guide to room element codes:
        Stone floor  = 0
        Stone wall = 1
        Wood door = 2, add a "L" to make it locked
        Player = "Player"
        Melee enemy = "Stalker"
        Bow enemy = "Bowman"
        Chest = "Chest", contents can be found at [0][0]
        """
        for i in xrange(len(lines)):
            for j in xrange(len(lines[i])):
                rect = pygame.Rect(j * drawSize, i * drawSize, drawSize, drawSize)
                if 1 in lines[i][j]:
                    sliced = self.make_array_slice(lines, i, j, [1])  # array, i, j, filler
                    sprite = self.make_wall_block(walls, sliced)
                    sprite = SimpleRectSprite(rect, sprite.image, True)
                    self.block_group.add(sprite)
                if "Stalker" in lines[i][j]:
                    stalker = Stalker(pygame.Rect(rect.x, rect.y, drawSize-1, drawSize / 5 * 3), charset.subsurface(pygame.Rect(charset.get_width() / 18 * 3, charsetRect.bottom - (charsetRect.height / 8 * 4), charset.get_width() / 18 * 3, charsetRect.height / 8 * 4)), character_sprite_size, self.player)
                    self.npcs.add(stalker)
                if "Bowman" in lines[i][j]:
                    bowman = Bowman(pygame.Rect(rect.x, rect.y, drawSize-1, drawSize / 5 * 3), charset.subsurface(pygame.Rect(charset.get_width() / 18 * 6, charsetRect.bottom - (charsetRect.height / 8 * 4), charset.get_width() / 18 * 3, charsetRect.height / 8 * 4)), character_sprite_size, self.player)
                    self.npcs.add(bowman)
                    #pygame.time.set_timer(bowmanShootEvent, 5000)
                if "Player" in lines[i][j]:
                    self.player.update_player(pygame.Rect(rect.x, rect.y, drawSize - 1, drawSize / 5 * 3), 180)
                if 2 in lines[i][j]:
                    # Check if vertical door or horizontal door
                    # If door has already been made, skip this
                    # Assuming that this is the top-left corner of the door
                    array_slice = self.make_array_slice(lines, i, j, [0])
                    temp_rect = pygame.Rect(rect)
                    if not (2 in array_slice[0][1] or 2 in array_slice[1][0]):
                        rotation = 0
                        if len(lines) - 1 >= (i + 1) and len(lines[i]) - 1 >= (j + 2) and 2 in lines[i+1][j+2]:
                            if i > len(lines) / 2:
                                rotation = 180
                            else:
                                rotation = 0
                            temp_rect.w = drawSize * 3
                            temp_rect.h = drawSize * 2
                        elif len(lines) - 1 >= (i + 2) and len(lines[i]) - 1 >= (j + 1) and 2 in lines[i+2][j+1]:
                            if j > len(lines[i]) / 2:
                                rotation = 270
                            else:
                                rotation = 90
                            temp_rect.w = drawSize * 2
                            temp_rect.h = drawSize * 3
                        else:
                            print("Level not set up properly.")
                            raise Exception
                        inner_rect = pygame.Rect(75, 0, 75, 50) if "L" in lines[i][j] else pygame.Rect(0, 0, 75, 50)
                        door_texture = door.copy().subsurface(inner_rect)
                        door_texture = pygame.transform.scale(door_texture, (drawSize * 3, drawSize * 2))
                        door_texture = pygame.transform.rotate(door_texture, rotation)
                        temp_door = Door(temp_rect, door_texture, rotation, pygame.transform.scale(door, (drawSize * 6, drawSize * 2)), True if "L" in lines[i][j] else False)
                        self.doors.append(temp_door)
                        self.action_group.add(temp_door)
                        self.collidables.append(temp_door)
                if 0 in lines[i][j]:
                    sprite = SimpleRectSprite(rect, floor_tile, True)
                    sprite.image = pygame.transform.rotate(sprite.image, random.randrange(0, 360, 90))
                    self.background_group.add(sprite)
        self.triggers = list()
        for tag in lines[0][0]:
            if type(tag) is Trigger:
                self.triggers.append(tag)
                try:
                    tag.placeWhere
                except:
                    pass
                else:
                    tag.set_place(lines)

        # Merge individual blocks into lines
        self.block_lines = pygame.sprite.OrderedUpdates()
        lastBlock = None
        currentLineSpriteGroup = pygame.sprite.Group()
        for block in self.block_group:
            if lastBlock is None:
                lastBlock = block
                currentLineSpriteGroup.add(block)
                continue
            if (lastBlock.rect.y == block.rect.y and lastBlock.rect.height == block.rect.height and lastBlock.rect.right == block.rect.left):
                currentLineSpriteGroup.add(block)
            else:
                self.block_lines.add(ConjoinedSpriteGroup(currentLineSpriteGroup))
                currentLineSpriteGroup = pygame.sprite.Group(block)
            lastBlock = block
        self.block_lines.add(ConjoinedSpriteGroup(currentLineSpriteGroup))

        #Merge lines into large blocks
        """self.large_block_group = pygame.sprite.Group()
        tempasd = pygame.sprite.Group()
        for line in self.block_lines:
            for line2 in self.block_lines:
                if (lastBlock.rect.x == block.rect.x and lastBlock.rect.width == block.rect.width and (lastBlock.rect.top == block.rect.bottom)):
                    for large_block in self.large_block_group:
                        if large_block.rect.contains(line2):
                            break
                    else:
                        tempasd.add(line2)
        self.large_block_group.add(ConjoinedSpriteGroup(pygame.sprite.Group()))"""

        self.collidables.extend(self.block_lines)

        self.entities.add(self.player, self.npcs)
        self.character_collision_boxes = [char.get_collision_box() for char in self.entities]
        #self.grid.update_grid(self.collidables + self.character_collision_boxes)
        self.grid.update_grid(self.collidables)
        if self.character_collision_boxes:
            self.shadow = pygame.transform.scale(shadow, self.character_collision_boxes[0].rect.size)
        self.update_hearts(heart)
        self.update_keys(self.keyTexture)
        self.swordsprite = SimpleSprite(self.player.rect.midtop, pygame.Surface((0, 0)))
        """self.backgroundFill = pygame.Surface((window_size))
        self.backgroundFill.fill(BLACK)
        self.gameSurface.blit(self.backgroundFill, self.camera)"""
        backgroundSurface = self.gameSurface.copy()
        backgroundSurface.fill(BLACK)

        self.block_group.draw(backgroundSurface)
        self.background_group.draw(backgroundSurface)
        backgroundSprite = SimpleSprite((0, 0), backgroundSurface)
        self.background = pygame.sprite.RenderUpdates(backgroundSprite,)
        self.windowRect = pygame.Rect((0, 0), window_size)
        self.offset = pygame.Rect(0, 0, 0, 0)
        if self.levelrect.w < window_width:
            self.offset.x = (window_width - self.levelrect.w) / 2
        if self.levelrect.h < window_height:
            self.offset.y = (window_height - self.levelrect.h) / 2
        self.cameraLeeway.center = self.player.collision_rect.center
        self.arrows = pygame.sprite.RenderUpdates()
        self.timerThread = threading.Thread()

    def render(self, screen):
        blit_to_gamesurface = self.gameSurface.blit
        # Game surface
        screen.fill(BLACK)
        self.background.draw(self.gameSurface)
        """for npc in self.npcs:
            if type(npc) is Stalker or Bowman:
                for brick in npc.pathBricks:
                    self.gameSurface.fill(BLACK, brick.rect)
                    pass"""
        for box in self.character_collision_boxes:
            blit_to_gamesurface(self.shadow, box.rect.midleft)
        self.action_group.draw(self.gameSurface)
        if not 315 >= self.player.direction >= 180:
            blit_to_gamesurface(self.swordsprite.image, self.swordsprite.rect)
            self.entities.draw(self.gameSurface)
        else:
            self.entities.draw(self.gameSurface)
            blit_to_gamesurface(self.swordsprite.image, self.swordsprite.rect)
        pygame.draw.rect(self.gameSurface, BLACK, pygame.Rect((0, 0), self.levelrect.size), 6)
        #self.gameSurface.fill(BLACK, self.player.collision_rect)

        screen.blit(self.gameSurface, ( self.offset.x  + 0 - self.camera.left,  self.offset.y  + 0 - self.camera.top))
        #screen.blit(pygame.transform.scale(gameSurface, window_size), (0, 0))

        # UI
        self.hearts.draw(screen)
        self.keys.draw(screen)
        if self.paused:
            line_rect1 = pygame.Rect(screen.get_rect().w // 32 * 31, screen.get_rect().h // 16, screen.get_rect().w // 64, screen.get_rect().w // 64 * 3)
            line_rect2 = pygame.Rect(screen.get_rect().w // 32 * 30, screen.get_rect().h // 16, screen.get_rect().w // 64, screen.get_rect().w // 64 * 3)
            pygame.draw.rect(screen, WHITE, line_rect1)
            pygame.draw.rect(screen, WHITE, line_rect2)
        screen.blit(self.swordsprite.image, (0,0))
        screen.blit(self.sword_icon.subsurface(pygame.Rect(0, 0, 44, 44)), (1000, 20))
        self.grand_clock.tick()

    def update(self, time):
        #self.grid.update_grid(self.collidables + self.character_collision_boxes)
        if self.paused:  # Don't update anything when paused, could add in any special exceptions here
            return
        # Update character positions, speed and layers
        change_entity_layer = self.entities.change_layer
        for sprite in self.entities.sprites():
            change_entity_layer(sprite, sprite.rect.centery)
        self.character_collision_boxes = [entity.get_collision_box() for entity in self.entities]
        for entity in self.entities:
            if type(entity) is not Player:
                entity.update_speed()
            entity.update_position(time, self.collidables + self.character_collision_boxes)
        for x in xrange(len(self.collidables) - 1):
            if not self.collidables[x].alive():
                self.collidables.pop(x)
        # Update camera
        if self.player.moving:
            self.update_camera()

        # Handle location based triggers
        for trigger in self.triggers:
            if trigger.rect.colliderect(self.player.collision_rect):
                # Collision/movement based triggers
                if trigger.name == "GotoRoom":
                    self.player.godMode = True
                    params = {'room': self.sword_texture, 'phase': 0, "gotoWhere": trigger.gotoWhere, 'vx':self.player.vx, 'vy':self.player.vy, 'nextScene': trigger.leadsToRoom}
                    self.animations.append(Animation("leaveRoom", params))
                    self.nextSceneThread = threading.Thread(target=self.processNextRoom, args=(trigger.leadsToRoom,))
                    self.nextSceneThread.daemon = True
                    self.nextSceneThread.start()
                self.triggers.remove(trigger)
            #Trigger types needed:
                #Enemy death trigger
                #
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.timerRunning = False
                if self.timerThread.is_alive():
                    self.timerThread.join()
                pygame.event.post(pygame.event.Event(QUIT))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.timerRunning = False
                if self.timerThread.is_alive():
                    self.timerThread.join()
                self.manager.go_to(TitleScene())
            if self.paused:
                continue
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_z) or (event.type == JOYBUTTONDOWN and event.button == 0):
                if Animation("sword") not in self.animations:
                    params = {'sprite': self.sword_texture, 'phase': 0}
                    self.animations.append(Animation("sword", params))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_x:
                pygame.event.post(pygame.event.Event(genericEvent, code='actionEvent',))
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP or event.type == JOYAXISMOTION or event.type == JOYHATMOTION:
                self.player.update_speed()
            if event.type == pathfindingEvent:
                for char in self.npcs:
                    if type(char) is Stalker:
                        char.update_path(self.grid, char.gridPos, self.player.gridPos)
                    if type(char) is Bowman:
                        char.findShootingSpot(self.grid)
            if event.type == updateGridEvent:
                self.grid.update_grid(self.collidables)
            if event.type == bowmanShootEvent:
                print "BOWMAN SHOOT EVENT"
                for npc in self.npcs:
                    if type(npc) is Bowman:
                        pygame.event.post(pygame.event.Event(delayedGenericEvent, code='bowmanShoot', delay=random.randint(0, 3000), entity=npc, ))

            if event.type == animationEvent:
                # Update all active animations
                for s in self.animations:
                    if s.name == "sword":  #Sword animation
                        self.player.directionLock = True
                        if s.phase >= 12:
                            self.swordsprite.image = pygame.Surface((0, 0))
                            self.animations.remove(s)
                            self.player.directionLock = False
                            self.player.set_sprite_direction()
                            self.player.update_sprite()
                            self.sword_icon = pygame.transform.flip(self.sword_icon, True, False)
                            continue
                        if s.phase < 7:
                            if s.phase == 3:
                                pygame.event.post(pygame.event.Event(genericEvent, code='swordSwingEvent',))
                            if s.phase < 2:
                                self.swordsprite.image = s.sprite.subsurface(pygame.Rect(0, 0, self.sword_texture.get_width() / 5, self.sword_texture.get_height()))
                            else:
                                self.swordsprite.image = s.sprite.subsurface(pygame.Rect((self.sword_texture.get_width() / 5) * (s.phase-2), 0, self.sword_texture.get_width() / 5, self.sword_texture.get_height()))
                            self.swordsprite.image = pygame.transform.rotate(pygame.transform.flip(self.swordsprite.image, True, False), (360 - self.player.direction) % 360 )
                        self.swordsprite.rect.topleft = self.player.rect.midtop
                        if s.phase == 0:
                            self.sword_icon = pygame.transform.flip(self.sword_icon, True, False)
                        if 45 > (self.player.direction % 360) or (self.player.direction % 360) >= 315:
                            self.swordsprite.rect.left -= drawSize * 0.7
                        elif 45 <= (self.player.direction % 360) < 135:
                            self.swordsprite.rect.left -= drawSize * 0.2
                            self.swordsprite.rect.top += drawSize * 0.25
                        elif 135 <= (self.player.direction % 360) < 225:
                            self.swordsprite.rect.top += drawSize * 0.5
                            self   .swordsprite.rect.left -= drawSize * 0.25
                        elif 225 <= (self.player.direction % 360) < 315:
                            self.swordsprite.rect.left -= drawSize * 0.7
                            self.swordsprite.rect.top += drawSize * 0.25
                            pass
                        s.phase += 1
                    # Animations needed:
                        # Sword swing x
                        # Death
                        # Door opening x
                        # Chest opening
                    if s.name == "health":
                        if s.phase >= 13:
                            self.animations.remove(s)
                            pygame.event.post(pygame.event.Event(genericEvent, code='healthEvent',))
                            continue
                        s.sprite.image = SimpleRectSprite(pygame.Rect(s.sprite.rect), self.heartTexture.subsurface(pygame.Rect((s.phase) * 8, 0, 8, 8)), True).image
                        s.phase += 1
                    if s.name == "openDoor":
                        if s.door.is_open:
                            self.animations.remove(s)
                            continue
                        if s.phase >= 6:
                            s.door.is_open = True
                            self.animations.remove(s)
                            if s.door.rotation == 0:
                                s.door.move_to(s.startRect.topright)
                            elif s.door.rotation == 90:
                                s.door.move_to(s.startRect.bottomleft)
                            elif s.door.rotation == 180:
                                s.door.move_to((s.startRect.left - s.startRect.width, s.startRect.top))
                            elif s.door.rotation == 270:
                                s.door.move_to((s.startRect.left, s.startRect.top - s.startRect.height))
                            self.grid.update_grid(self.collidables)
                            self.player.update_speed()
                            continue
                        self.player.vx = 0
                        self.player.vy = 0
                        self.player.set_sprite_direction()
                        if s.door.rotation == 0:
                            s.door.move((drawSize / 2, 0))
                        elif s.door.rotation == 90:
                            s.door.move((0, drawSize / 2))
                        elif s.door.rotation == 180:
                            s.door.move((-(drawSize / 2), 0))
                        elif s.door.rotation == 270:
                            s.door.move((0, -(drawSize / 2)))
                        s.phase += 1
                    if s.name == "leaveRoom":
                        if s.phase == 20:
                            #self.manager.go_to(GameScene(s.nextScene, self.player, pygame.Rect((300, 100), self.player.collision_rect.size)))
                            if self.nextSceneThread.is_alive():
                                self.nextSceneThread.join()
                            self.timerRunning = False
                            if self.timerThread.is_alive():
                                self.timerThread.join()
                            self.manager.go_to(self.nextScene)
                            self.manager.scene.set_player(self.player, s.gotoWhere)
                            self.animations.remove(s)
                            for tag in self.lines[0][0]:
                                if type(tag) is Trigger:
                                    self.triggers.append(tag)
                                    try:
                                        tag.placeWhere
                                    except Exception:
                                        pass
                                    else:
                                        tag.set_place(self.lines)
                            continue
                        if s.phase == 0:
                            self.player.directionLock = True
                        if s.vx > 0:
                            self.player.vx = self.player.baseSpeed
                        if s.vx < 0:
                            self.player.vx = -self.player.baseSpeed
                        if s.vy > 0:
                            self.player.vy = self.player.baseSpeed
                        if s.vy < 0:
                            self.player.vy = -self.player.baseSpeed
                        self.player.set_sprite_direction()
                        s.phase += 1

                for char in self.entities:
                    if char.moving:
                        char.walking_phase += 0.5
                        char.update_sprite()
                    if char.stunned:
                        if not char.red_blink:
                            pixels = pygame.PixelArray(char.image)
                            pixels.replace(WHITE, RED, 0.9)
                            char.image = pixels.surface
                            char.red_blink = True
                        else:
                            char.red_blink = False
                            char.update_sprite()
                    elif char.red_blink:
                        char.red_blink = False
                        char.update_sprite()

            if event.type == genericEvent:
                if event.code == "swordSwingEvent":
                    boxes = self.make_surrounding_blocks(self.player.collision_rect)
                    blocks = pygame.sprite.Group()
                    blocks.add(boxes[int(self.player.direction//45) % 8])
                    # blocks.add(boxes[((self.player.direction/45) + 1) % 8])
                    for sprite in pygame.sprite.groupcollide(self.npcs, blocks, False, False):
                        sprite.hit()

                elif event.code == "healthEvent":
                    if self.player.health > self.player.maxHealth:
                        self.player.health = self.player.maxHealth - 1
                        self.player.displayHealth = self.player.maxHealth
                    if self.player.displayHealth != self.player.health and self.player.health >= 0:
                        params = {'sprite': self.heartList[self.player.displayHealth-1],
                                  'jumpdistance': 8, 'phase': 0, }
                        self.animations.append(Animation("health", params))
                        self.player.displayHealth -= 1
                    elif self.player.health <= 0:
                        gamesurface = pygame.Surface(self.manager.screen.get_size())
                        gamesurface.fill(BLACK)
                        gamesurface.blit(self.gameSurface.subsurface(self.camera), (self.offset.x, self.offset.y))
                        self.timerRunning = False
                        if self.timerThread.is_alive():
                            self.timerThread.join()
                        self.manager.go_to(GameOverScene(gamesurface))

                elif event.code == "keyEvent":
                    self.update_keys(self.keyTexture)

                elif event.code == "actionEvent":  # When the player presses the action key
                    surrounding_blocks = self.make_surrounding_blocks(self.player.collision_rect)
                    blocks = pygame.sprite.Group()
                    blocks.add(surrounding_blocks[int(self.player.direction//45) - 1], Block(self.player.collision_rect, BLACK))
                    for door in pygame.sprite.groupcollide(self.doors, blocks, False, False):
                        if not door.locked:
                            if not door.is_open:
                                params = {'door': door, 'phase': 0, 'startRect': copy.copy(door.rect)}
                                self.animations.append(Animation("openDoor", params))
                        elif self.player.keys > 0:
                            self.player.keys -= 1
                            door.unlock()
                            pygame.event.post(pygame.event.Event(genericEvent, code='keyEvent',))
                elif event.code == "unstunEvent":
                    if event.entity.stunned:
                        event.entity.stunned = False
                    if event.entity.health <= 0:
                        try:
                            event.entity.kill()
                        except ValueError:
                            event.entity = None

                elif event.code == "bowmanShoot":
                    print ("SHOOT", event.entity)
                    #arrow = Arrow()
            if event.type == delayedGenericEvent:
                self.timerThread = threading.Timer(float(event.delay) / 1000.0, self.delayedEventHandling, args=(event,))
                self.timerThread.start()

    def delayedEventHandling(self, event):  #Waits for the specified amount of time, then sends the event on it's way
        pygame.event.post(pygame.event.Event(genericEvent, code=event.code, entity=event.entity,))

    def make_wall_block(self, wall_texture, array_slice):
        rect = pygame.Rect(0, 0, 24, 24)
        sprite = Block(rect, BLACK)
        rotated = list(array_slice)
        blocked = {1, 2}
        for rotation in xrange(4):
            innerRect = pygame.Rect(0, 0, 12, 12)
            for i in rotated[1][0]:
                if i in blocked:
                    for j in rotated[0][1]:
                        if j in blocked:
                            for k in rotated[0][0]:
                                if k in blocked:
                                    break
                            else:
                                # closed corner
                                innerRect.topleft = (0, 12)
                            break
                    else:
                        # wall facing up
                        innerRect.topleft = (12, 0)
                    break
            else:
                for i in rotated[0][1]:
                    if i in blocked:
                        # wall facing left
                        innerRect.topleft = (24, 0)
                        break
                else:
                    # open corner
                    innerRect.topleft = (12, 12)

            if innerRect.topleft == (0, 0):
                sprite.image.blit(pygame.transform.rotate(wall_texture.subsurface(innerRect), random.randrange(0, 360, 90)), (0, 0))
            else:
                sprite.image.blit(wall_texture.subsurface(innerRect), (0, 0))
            rotated = zip(*rotated[::-1])
            sprite.image = pygame.transform.rotate(sprite.image, -90)
        return sprite

    def make_array_slice(self, array, i, j, filler):
        sliced = [[filler, filler, filler], [filler, filler, filler], [filler, filler, filler]]
        for x in range(-1, 2):
            for y in range(-1, 2):
                try:
                    if i-x >= 0 and j-y >= 0:
                        sliced[1-x][1-y] = array[i-x][j-y]
                except IndexError:
                    pass
        return sliced

    def make_surrounding_blocks(self, rect):
        boxes = list()
        for i in xrange(0, 360, 45):
            block = pygame.Rect(0, 0, min(rect.w, rect.h), min(rect.w, rect.h))
            if i == 0 or i == 45 or i == 315:
                block.bottom = rect.top
            elif i == 90 or i == 270:
                block.top = rect.top
            elif 135 <= i <= 225:
                block.top = rect.bottom
            if 225 <= i <= 360:
                block.right = rect.left
            elif i == 0 or i == 180:
                block.left = rect.left
            elif 45 <= i <= 135:
                block.left = rect.right
            boxes.append(Block(block, BLACK))
        return boxes

    def update_hearts(self, heartTexture):
        self.heartList = list()
        for i in xrange(self.player.maxHealth):
            rect = pygame.Rect((window_width / 6) + (40 * i), 20, 7 * 4, 7 * 4)  # Edit this to change heart locations
            if self.player.health > i:
                self.heartList.append(SimpleRectSprite(rect, heartTexture.subsurface(pygame.Rect(0, 0, 8, 8)), True))
            else:
                self.heartList.append(SimpleRectSprite(rect, heartTexture.subsurface(pygame.Rect(8*12, 0, 8, 8)), True))
        self.hearts = pygame.sprite.RenderUpdates(self.heartList)

    def update_keys(self, keyTexture):  # Edit this to change key icon locations
        self.keyList = list()
        for i in xrange(self.player.keys):
            rect = pygame.Rect((window_width / 2) + (40 * i), 20, 7 * 5, 7 * 5)
            self.keyList.append(SimpleRectSprite(rect, self.keyTexture, True))
        self.keys = pygame.sprite.RenderUpdates(self.keyList)


    def processNextRoom(self, scene):
        try:
            self.nextScene = self.manager.room[scene]
        except IndexError:
            self.nextScene = GameScene(scene)
        print("Room " + str(scene) + " loaded")

    def teleportPlayerToTag(self, playerLocation):
        found_tag = False
        l = self.lines
        for a in xrange(len(l)):
            for b in xrange(len(l[a])):
                if playerLocation in l[a][b]:
                    self.player.update_player(
                        pygame.Rect((b * drawSize, a * drawSize), self.player.collision_rect.size), 180)
                    self.cameraLeeway.center = self.player.collision_rect.center
                    found_tag = True
        return found_tag

    def set_player(self, player, playerLocationTag):
        self.player.__dict__ = player.__dict__.copy()
        self.player.update_player(player.collision_rect, player.direction)
        self.teleportPlayerToTag(playerLocationTag)
        self.character_collision_boxes = [char.get_collision_box() for char in self.entities]
        self.grid.update_grid(self.collidables)
        self.update_hearts(self.heartTexture)
        self.update_keys(self.keyTexture)
        # Manually unstun player and update speed in case player is already holding down movement keys
        self.player.stunned = False
        self.player.godMode = False
        self.player.directionLock = False
        self.player.update_speed()
        self.cameraLeeway.center = self.player.collision_rect.center
        self.update_camera()

    def load_level(self):  # Don't mess with the player here, use set_player or teleportPlayerToTag
        for npc in self.npcs:
            npc.set_position(npc.startPoint)
        # Manually unstun player and update speed in case player is already holding down movement keys
        self.player.stunned = False
        self.player.godMode = False
        self.player.directionLock = False
        self.player.update_speed()
        self.cameraLeeway.center = self.player.collision_rect.center
        self.update_camera()

    def update_camera(self):
        camera = self.camera
        cameraLeeway = self.cameraLeeway
        player = self.player
        self.cameraLeeway = reverse_clamp(player.collision_rect, cameraLeeway)
        self.camera.center = self.cameraLeeway.center  # Camera follows the camera leeway rect
        self.camera = camera.clamp(self.gameSurface.get_rect())  # Make sure camera does not leave the game area


class TitleScene(Scene):

    def __init__(self):
        super(TitleScene, self).__init__()
        background = pygame.image.load(os.path.join('images', 'background test.png')).convert_alpha()
        background = pygame.transform.scale(background, window_size)
        self.menu_background = SimpleSprite((0, 0), pygame.image.load(os.path.join('images', 'background menu.png')).convert_alpha())
        self.logo = pygame.image.load(os.path.join('images', 'logo pixel.png')).convert_alpha()
        self.logo_sprite = SimpleRectSprite(pygame.Rect(425, 325, 400, 400), self.logo, True)
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        self.animations = list()
        if pygame.mixer.get_init():
            self.mixer = pygame.mixer.Channel(0)
            self.mixer.set_volume(0.8)
            self.music = pygame.mixer.Sound(os.path.join('sounds', 'abba lite.ogg'))
            self.mixer.play(self.music)
        self.color = [50, 50, 50]
        self.colorLevel = [True, True, True]
        self.textCoord = 300
        self.textLevel = 0
        self.realbackground1x = 0
        self.realbackground2x = -window_width
        self.background1 = SimpleSprite((self.realbackground1x, 0), background)
        self.background2 = SimpleSprite((self.realbackground2x, 0), background)
        self.backgroundSprites = pygame.sprite.Group(self.background1, self.background2)
        self.whiteScreen = pygame.Surface(window_size)
        self.whiteScreen.fill(WHITE)
        self.whiteScreen.set_alpha(0)
        self.screenRect = pygame.Rect((0, 0), window_size)
        self.menu_background.rect.center = self.screenRect.center
        self.logo_sprite.rect.center = (self.screenRect.centerx, self.menu_background.rect.centery + 150)

    def render(self, screen):
        blitToScreen = screen.blit
        self.backgroundSprites.draw(screen)
        blitToScreen(self.menu_background.image, self.menu_background.rect)
        text1 = self.font.render('Lokaverkefni', True, tuple(self.color))
        text2 = self.sfont.render('> press space to start <', True, WHITE)
        blitToScreen(text1, (self.menu_background.rect.left + 460, self.menu_background.rect.top + 100))
        blitToScreen(text2, (self.menu_background.rect.left + 425, self.menu_background.rect.top + self.textCoord))
        blitToScreen(self.logo_sprite.image, self.logo_sprite.rect)
        blitToScreen(self.whiteScreen, (0, 0))

    def update(self, time):
        self.textCoord = 300 + (sin(self.textLevel) * 10)
        self.textLevel += (0.0005 * time) % 0.1
        self.textLevel %= 6.28
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.event.post(pygame.event.Event(QUIT))
            if (event.type == KEYDOWN and event.key == K_SPACE) or (event.type == JOYBUTTONDOWN and event.button == 0):
                params = {'phase': 0, 'opacity': 0}
                self.animations.append(Animation("StartGame", params))
            if event.type == animationEvent:
                for s in self.animations:
                    if s.name == "StartGame":
                        if s.phase == 0:
                            if pygame.mixer.get_init():
                                self.mixer.fadeout(1000)
                        if s.phase == 19:
                            self.whiteScreen.set_alpha(255)
                        if s.phase == 20:
                            self.manager.generate_rooms()
                            self.manager.go_to(GameScene(startLevel))
                        s.opacity += 12
                        self.whiteScreen.set_alpha(s.opacity)
                        s.phase += 1

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
                    self.realbackground1x += 0.5
                    self.realbackground2x += 0.5
                    self.background1.rect.left = self.realbackground1x
                    self.background2.rect.left = self.realbackground2x
                    if self.realbackground1x == 0:
                        self.realbackground2x = -window_width
                    elif self.realbackground2x == 0:
                        self.realbackground1x = -window_width

class TextScrollScene(Scene):

    def __init__(self, text):
        super(TextScrollScene, self).__init__()
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
    def __init__(self, game_scene_background):
        super(GameOverScene, self).__init__()
        if pygame.mixer.get_init():
            self.mixer = pygame.mixer.Channel(1)
            self.mixer.set_volume(0.3)
            self.music = pygame.mixer.Sound(os.path.join('sounds', 'tengsli 1.1 loop.ogg'))
            self.mixer.play(self.music, -1,)
        font = pygame.font.SysFont('Consolas', 56)
        small_font = pygame.font.SysFont('Consolas', 32)
        self.text = font.render('Game Over', True, WHITE)
        self.text2 = small_font.render('Press space to try again.', True, WHITE)
        self.text3 = font.render('Game Over', True, BLACK)
        self.text4 = small_font.render('Press space to try again.', True, BLACK)
        self.text3.set_alpha(120)
        self.text4.set_alpha(120)
        self.background = game_scene_background
        self.blackScreen = pygame.Surface(self.background.get_size())
        self.blackScreen.fill(BLACK)
        self.blackScreen.set_alpha(0)
        self.animations = list()
        self.animations.append(Animation("fadeOutOfGame", {'phase': 0}))
        self.textRect = pygame.Rect(0, 0, max(self.text.get_width(), self.text2.get_width()), 500)
        self.textRect.center = pygame.Rect((0, 0), window_size).center

    def render(self, screen):
        blit_to_screen = screen.blit
        text_rect = self.textRect
        blit_to_screen(self.background, (0 ,0))
        blit_to_screen(self.blackScreen, (0, 0))
        blit_to_screen(self.text3, (text_rect.left + 85, text_rect.top + 55))
        blit_to_screen(self.text4, (text_rect.left + 5, text_rect.top + 125))
        blit_to_screen(self.text, (text_rect.left + 80, text_rect.top + 50))
        blit_to_screen(self.text2, (text_rect.left, text_rect.top + 120))

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_ESCAPE):
                if pygame.mixer.get_init():
                    self.mixer.fadeout(500)
                self.manager.go_to(TitleScene())
            if event.type == animationEvent:
                for s in self.animations:
                    if s.name == "fadeOutOfGame":
                        if s.phase >= 40:
                            print "Done"
                            self.animations.remove(s)
                            continue
                        self.blackScreen.set_alpha(s.phase * 5)
                        s.phase += 1


