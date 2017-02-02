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
    charset = pygame.image.load(os.path.join('images', 'charset.png')).convert_alpha()
    gridImage = pygame.image.load(os.path.join('images', 'grid 16x16 transculent.png')).convert_alpha()
    gridImage = pygame.transform.scale(gridImage, (gridImage.get_rect().w * 24 / 16, gridImage.get_rect().h * 24 / 16))
    try:
        pygame.mixer.init()
    except pygame.error as err:
        print("Error: " + str(err) + "; attempting to run anyway.")
        print("Please note that you may run into glitches and crashes while in this mode.")
        
    manager = SceneManager()
    pygame.time.set_timer(pathfindingEvent, 500)
    pygame.time.set_timer(animationEvent, 42)  # approx 24 times per second
    running = True

    sfont = pygame.font.SysFont('Consolas', 12)

    # Game loop
    while running:
        if pygame.event.get(QUIT):
            running = False
            return
        manager.scene.render(screen)
        text1 = sfont.render("fps:" + str(clock.get_fps()), False, WHITE)
        screen.blit(text1, (0, 0))
        pygame.display.update()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update(clock.get_time())
        clock.tick()
        #print(clock.get_fps())

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
