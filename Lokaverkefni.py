import pygame
from pygame.locals import *
import threading
import sys
import os
from Scenes import *


def main():
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
    pygame.time.set_timer(pathfindingEvent, 150)
    pygame.time.set_timer(animationEvent, 42)  # approx 24 times per second
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
