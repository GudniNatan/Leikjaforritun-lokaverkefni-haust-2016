import pygame
from pygame.locals import *
import threading
import sys
import os
from Scenes import *


def main():
    # Pygame stuff
    pygame.init()
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE|pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    pygame.display.set_caption('FOR3G3U')

    # Setup
    charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
    gridImage = pygame.image.load(os.path.join('images', 'grid 16x16 transculent.png')).convert_alpha()
    gridImage = pygame.transform.scale(gridImage, (gridImage.get_rect().w * 24 / 16, gridImage.get_rect().h * 24 / 16))
    manager = SceneMananger()
    pygame.mixer.init()
    pygame.time.set_timer(pathfindingEvent, 500)
    pygame.time.set_timer(animationEvent, 1000 / 24)
    running = True

    # Game loop
    while running:
        if pygame.event.get(QUIT):
            running = False
            return
        manager.scene.render(screen)
        pygame.display.update()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update(clock.get_time())
        clock.tick(120)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
