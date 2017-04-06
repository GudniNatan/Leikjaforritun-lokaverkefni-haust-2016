import threading
import pygame
from pygame import *
from pygame.locals import *

# By Gudni Natan Gunnarsson, 2017

class _Timer(object):
    def __init__(self, event, rate):
        self.running = False
        self.event = event
        self.rate = rate
        self.t = threading.Thread(target=self.eventPoster, args=(event, rate))
        self.t.daemon = True
        self.ok = threading.Event()

    def go(self):
        self.ok.set()

    def eventPoster(self, event, rate):
        e = pygame.event
        go = self.go

        def wait(rate):
            self.ok.clear()
            goThread = threading.Timer(float(rate) / 1000.0, go)
            goThread.daemon = True
            goThread.start()
            self.ok.wait()
            if goThread.is_alive() and self.running:
                goThread.join()

        wait(rate)
        while self.running:
            if type(event) is e.EventType:
                e.post(event)
            else:
                e.post(e.Event(event))
            wait(self.rate)

    def start_timer(self):
        self.running = True
        self.t.start()

    def stop_timer(self):
        if self.running:
            self.running = False
            self.ok.set()
            self.t.join()

    def change_rate(self, rate):
        self.rate = rate

class _BetterTimers(object):
    def __init__(self):
        self.timers = list()

    def set_timer(self, event, rate):
        t = _Timer(event, rate)
        for e in self.timers:
            if e.event == event:
                if rate > 0:
                    e.change_rate(rate)
                else:
                    e.stop_timer()
                    self.timers.remove(e)
                return
        if rate > 0:
            t.start_timer()
            self.timers.append(t)

    def end_all_timers(self):
        for t in self.timers:
            t.stop_timer()

        self.timers = list()


_time = _BetterTimers()

class Rect(pygame.Rect):
    def reverse_clamp(self, other):
        if not self.contains(other):
            new_rect = Rect(self)
            if other.left <= self.left:
                new_rect.left = other.left
            elif other.right >= self.right:
                new_rect.right = other.right
            if other.top <= self.top:
                new_rect.top = other.top
            elif other.bottom >= self.bottom:
                new_rect.bottom = other.bottom
            return new_rect
        return self

    def reverse_clamp_ip(self, other):
        if not self.contains(other):
            if other.left <= self.left:
                self.left = other.left
            elif other.right >= self.right:
                self.right = other.right
            if other.top <= self.top:
                self.top = other.top
            elif other.bottom >= self.bottom:
                self.bottom = other.bottom

    #Other possible methods include declamp, declamp_ip and reverse_declamp, reverse_declamp_ip

class Surface(pygame.Surface):
    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.get_rect()
        rot_image = pygame.transform.rotate(self, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def aspect_scale(self, widthHeightTuple):
        bx, by = widthHeightTuple
        scale_rect = pygame.Rect(0, 0, bx, by)
        image_rect = self.get_rect()
        pygame.transform.scale(self, image_rect.fit(scale_rect).size)

def init():
    pygame.init()
    time.set_timer = _time.set_timer
    time.end_all_timers = _time.end_all_timers


def quit():
    _time.end_all_timers()
    pygame.quit()
