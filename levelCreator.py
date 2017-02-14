import pygame
from pygame.locals import *
import threading
import sys
import os
from LevelCreatorScenes import *


def main():
    from pygame import USEREVENT

    WHITE = (242, 242, 242)
    BLACK = (25, 25, 25)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 102, 255)
    ORANGE = (255, 153, 0)

    drawSize = 40
    halfDrawSize = drawSize / 2
    window_size = window_width, window_height = 1280, 720

    # Pygame stuff
    pygame.init()
    screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    pygame.display.set_caption('FOR3L3DU')

    # Setup
    try:
        pygame.mixer.init()
    except pygame.error as err:
        print("Error: " + str(err) + "; attempting to run anyway.")
        print("Please note that you may run into glitches and crashes while in this mode.")

    manager = SceneManager(screen)
    manager.go_to(MenuScene(manager))
    running = True
    fpsAverage = list()
    sfont = pygame.font.SysFont('Consolas', 12)


    # Game loop
    while running:
        if pygame.event.get(QUIT):
            running = False
            return
        manager.scene.render(screen)
        text1 = sfont.render("fps:" + str(clock.get_fps()), False, WHITE)
        screen.blit(text1, (0, 0))
        """fpsAverage.append(clock.get_fps())
        if len(fpsAverage) > 200:
            fpsAverage.pop(0)
        text2 = sfont.render("avg:" + str(reduce(lambda x, y: x + y, fpsAverage) / len(fpsAverage)), False, WHITE)
        screen.blit(text2, (0, 13))"""
        pygame.display.update()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update(clock.get_time())
        clock.tick()
        #print(clock.get_fps())
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
