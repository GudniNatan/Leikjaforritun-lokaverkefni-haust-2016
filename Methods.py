import pygame
import vec2d_jdm


def aspect_scale(image, (bx, by)):
    scale_rect = pygame.Rect(0, 0, bx, by)
    image_rect = image.get_rect()
    return pygame.transform.scale(image, image_rect.fit(scale_rect).size)


def CreateVectorFromCoordinates((x1, y1), (x2, y2)):
    x = x2 - x1
    y = y2 - y1
    return vec2d_jdm.Vec2D(x, y)


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def reverse_clamp(smaller_rect, larger_rect):
    if not larger_rect.contains(smaller_rect):
        new_rect = larger_rect.copy()
        if smaller_rect.left <= larger_rect.left:
            new_rect.left = smaller_rect.left
        elif smaller_rect.right >= larger_rect.right:
            new_rect.right = smaller_rect.right
        if smaller_rect.top <= larger_rect.top:
            new_rect.top = smaller_rect.top
        elif smaller_rect.bottom >= larger_rect.bottom:
            new_rect.bottom = smaller_rect.bottom
        return new_rect
    return larger_rect


def reverse_clamp_ip(smaller_rect, larger_rect):
    if not larger_rect.contains(smaller_rect):
        if smaller_rect.left <= larger_rect.left:
            larger_rect.left = smaller_rect.left
        elif smaller_rect.right >= larger_rect.right:
            larger_rect.right = smaller_rect.right
        if smaller_rect.top <= larger_rect.top:
            larger_rect.top = smaller_rect.top
        elif smaller_rect.bottom >= larger_rect.bottom:
            larger_rect.bottom = smaller_rect.bottom
