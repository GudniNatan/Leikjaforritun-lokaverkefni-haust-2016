from Scenes import SceneManager
from Scenes import Scene
import pygame
from pygame.locals import *
import Objects
from Constants import *

class MenuScene(Scene):
    def __init__(self, manager):
        super(MenuScene, self).__init__()
        self.manager = manager
        self.font = pygame.font.SysFont('Consolas', 56)
        self.sfont = pygame.font.SysFont('Consolas', 32)
        loadRoomText = self.font.render('Load Room from file', True, WHITE)
        loadRoomImage = pygame.Surface(loadRoomText.get_size())
        loadRoomImage.fill(BLUE, loadRoomText.get_rect())
        loadRoomImage.blit(loadRoomText, (0, 0))
        self.load_room_button = Objects.SimpleRectSprite(loadRoomImage.get_rect(), loadRoomImage)
        newRoomText = self.font.render('Create new room', True, WHITE)
        newRoomImage = pygame.Surface(newRoomText.get_size())
        newRoomImage.fill(BLUE, newRoomText.get_rect())
        newRoomImage.blit(newRoomText, (0, 0))
        self.new_room_button = Objects.SimpleRectSprite(newRoomImage.get_rect(), newRoomImage)
        screenrect = self.manager.screen.get_rect()
        self.load_room_button.rect.center = screenrect.center
        self.new_room_button.rect.center = screenrect.center
        self.load_room_button.rect.centery -= window_height / 20
        self.new_room_button.rect.centery += window_height / 20
        self.buttons = pygame.sprite.RenderUpdates(self.load_room_button, self.new_room_button)
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        pass

    def render(self, screen):
        screen.fill(BLACK)
        self.buttons.draw(screen)
        for button in self.buttons:
            print button.rect
        pass

    def update(self, time):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.event.post(pygame.event.Event(QUIT))
        pass