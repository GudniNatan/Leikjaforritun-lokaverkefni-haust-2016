import pygame
from pygame.locals import *
import threading
import sys
import os
from Constants import *
from Characters_sprites import *
from Objects import *
from Scenes import *

# Pygame stuff
pygame.init()
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
clock = pygame.time.Clock()
processing_clock = pygame.time.Clock()
pygame.display.set_caption('FOR3G3U')


running = True
charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
'''character_sprite_size = (16, 18, 24)
thePlayer = Player(pygame.Rect(30, 30, 15, drawSize / 2), charset.subsurface(pygame.Rect(0, 72, 47, 72)), character_sprite_size)
theStalker = Stalker(pygame.Rect(100, 300, 15, drawSize / 2), charset.subsurface(pygame.Rect(48, 72, 47, 72)), character_sprite_size)
theStalker2 = Stalker(pygame.Rect(200, 300, 15, drawSize / 2), charset.subsurface(pygame.Rect(48, 72, 47, 72)), character_sprite_size)
npcs = list()
npcs.extend([theStalker, theStalker2])'''
stalkerTimer = pygame.time.set_timer(stalkerEvent, 500)
animationTimer = pygame.time.set_timer(animationEvent, 1000 / 24)
gridImage = pygame.image.load(os.path.join('images', 'grid 16x16 transculent.png')).convert_alpha()
gridImage = pygame.transform.scale(gridImage, (gridImage.get_rect().w * 24 / 16, gridImage.get_rect().h * 24 / 16))
'''grid = []
swordi = pygame.image.load(os.path.join('images', 'sword.png')).convert_alpha()
sword = Sword(thePlayer.rect.x, thePlayer.rect.y, 50, 50, swordi)
shadow = pygame.image.load(os.path.join('images', 'shadow.png')).convert_alpha()
shadow = pygame.transform.scale(shadow, thePlayer.collision_rect.size)
events = list()
walls = list()
collidables = list()'''
animations = list()
'''block_group = pygame.sprite.Group()
character_group = pygame.sprite.LayeredUpdates()
character_group.add(thePlayer, theStalker, theStalker2)
character_collision_boxes = [char.get_collision_box() for char in character_group]'''

'''theGrid = Grid(GRID_SIZE)
for i in range(GRID_SIZE[0] * 2):
        block1 = (Block(pygame.Rect(i * drawSize, 0, drawSize, drawSize), BLACK))
        block2 = (Block(pygame.Rect(i * drawSize, (GRID_SIZE[1] * 2 - 1) * drawSize, drawSize, drawSize), BLACK))
        block_group.add(block1, block2)
for i in range(GRID_SIZE[1] * 2):
        block1 = (Block(pygame.Rect(0, i * drawSize, drawSize, drawSize), BLACK))
        block2 = (Block(pygame.Rect((GRID_SIZE[0] * 2 - 1) * drawSize, i * drawSize, drawSize, drawSize), BLACK))
        block_group.add(block1, block2)
collidables.extend(block_group)
theGrid.update_grid(collidables, 4)'''


def main():
    manager = SceneMananger()
    global running
    while running:  # Game loop
        """# Events
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
                pygame.event.post(pygame.event.Event(swordSwingEvent))
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                thePlayer.update_speed()
            if event.type == stalkerEvent:
                for char in npcs:
                    if type(char) is Stalker:
                        char.update_path(theGrid.grid, char.gridPos, thePlayer.gridPos)
            if event.type == updateGridEvent:
                theGrid.update_grid(collidables + character_collision_boxes)
            if event.type == animationEvent:
                # Update all active animations
                for s in animations:
                    if s.name == "sword":
                        if sword.rotation < s.end and s.direction == thePlayer.direction:
                            sword.display = True
                            sword.rot_center(50)
                        else:
                            sword.display = False
                            sword.rotation = 0
                            animations.remove(s)
                for char in character_group:
                    if char.moving:
                        char.walking_phase = (char.walking_phase + 0.5) % 3
                        char.update_sprite()
            if event.type == swordSwingEvent:
                if Animation("sword") not in animations:
                    sword.rotation = thePlayer.direction - 25
                    params = {'direction': thePlayer.direction, 'end': thePlayer.direction + 100}
                    animations.append(Animation("sword", params))
        #Processing
        character_collision_boxes = [char.get_collision_box() for char in character_group]
        for char in character_group:
            if type(char) is not Player:
                char.update_speed()
            char.update_position(clock.get_time(), collidables + character_collision_boxes)

        '''thePlayer.update_position(clock.get_time(), collidables + [theStalker.get_collision_box(), theStalker2.get_collision_box()])
        theStalker.update_speed()
        theStalker.update_position(clock.get_time(), collidables + [thePlayer.get_collision_box(), theStalker2.get_collision_box()])'''
        sword.update_pos(thePlayer.collision_rect.center)


        # Graphics
        screen.fill(WHITE)
        #screen.fill(BLUE, sword.originalRect)
        #screen.fill(GREEN, sword.rect)
        if sword.display:
            screen.blit(sword.surface, sword.rect.topleft)

        #for node in theStalker.pathBricks: # Use this to see stalker pathfinding
        #    screen.fill(GREEN, node)
        for box in character_collision_boxes:
            screen.blit(shadow, box.rect.midleft)

        block_group.draw(screen)
        for sprite in character_group.sprites():
            character_group.change_layer(sprite, sprite.gridPos[1])
        character_group.draw(screen)

        #screen.blit(thePlayer.sprite, thePlayer.sprite_rect)
        #screen.blit(theStalker.sprite, theStalker.sprite_rect)


        #screen.blit(gridImage, (0, 0))

        clock.tick()
        pygame.display.update()"""
        if pygame.event.get(QUIT):
            running = False
            return
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update(clock.get_time())
        manager.scene.render(screen)
        pygame.display.flip()
        clock.tick()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
