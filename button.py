import pygame 
from enum import Enum


class MouseClick(Enum):
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3


class Button():
    DEFAULT = 0
    HOVERING = 1
    CLICKED = 2

    def __init__(self, x, y, image_list, scale):
        self.image_list = image_list
        self.btn_state = self.DEFAULT
        self.scale = scale
        self.__update_image__()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def __update_image__(self):
        if self.btn_state >= len(self.image_list):
            self.btn_state = self.DEFAULT

        img = self.image_list[self.btn_state]
        self.image = pygame.transform.scale(img, (int(img.get_width() * self.scale), 
            int(img.get_height() * self.scale)))

    def update(self):
        self.btn_state = self.DEFAULT

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            self.btn_state = self.HOVERING
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.btn_state = self.CLICKED

        if pygame.mouse.get_pressed()[0] == 0 and self.clicked:
            action = True
            self.clicked = False
            self.btn_state = self.HOVERING

    def check_button_click(self):
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                self.btn_state = self.CLICKED
                return MouseClick.LEFT
            elif pygame.mouse.get_pressed()[2] == 1:
                return MouseClick.RIGHT

        return None

    def check_button_up(self):
        # get mouse position
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 0:
            self.btn_state = self.HOVERING
        else:
            self.btn_state = self.DEFAULT

    def draw(self, surface):
        # update button image
        self.__update_image__()

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

