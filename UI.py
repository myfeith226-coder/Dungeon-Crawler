from tkinter import font

import pygame
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT
class MainMenu:
    def __init__(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.background = pygame.image.load(
            os.path.join(current_dir,
                         "assets",
                         "UI",
                         "main_menu.png")
        ).convert()

        self.buttons = pygame.image.load(
            os.path.join(current_dir,
                         "assets",
                         "UI",
                         "main_menu_button1.png")
        ).convert_alpha()

        self.background = pygame.transform.scale(
            self.background,
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        self.buttons = pygame.transform.scale_by(
            self.buttons,
            6
        )

        self.play_rect = pygame.Rect(0, 0, 280, 120)
        self.exit_rect = pygame.Rect(0, 0, 280, 120)
        # self.exit_rect = pygame.Rect(0, 0, 280, 120)

    def draw(self, screen):

        screen.blit(self.background, (0, 0))

        x = screen.get_width() // 2 - self.buttons.get_width() // 2 + 150

        y = screen.get_height() // 2 + 180

        screen.blit(self.buttons, (x, y))

        self.play_rect.topleft = (
            x + 10,
            y + 10
        )

        self.exit_rect.topleft = (
            x + 310,
            y + 10
        )

        # self.exit_rect.topleft = (
        #     x + 620,
        #     y + 10
        # )
        
        # pygame.draw.rect(screen, (255,0,0), self.play_rect, 2)
        # # pygame.draw.rect(screen, (0,255,0), self.options_rect, 2)
        # pygame.draw.rect(screen, (0,0,255), self.exit_rect, 2)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.play_rect.collidepoint(event.pos):
                    return "play"

                # if self.options_rect.collidepoint(event.pos):
                #     return "options"

                if self.exit_rect.collidepoint(event.pos):
                    return "exit"

        return None

class HUD:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.potion_img = pygame.image.load(
            os.path.join(current_dir, "assets", "Knight", "potion_bottle.png")
        ).convert_alpha()

        self.hp_background = pygame.image.load(
            os.path.join(current_dir, "assets", "UI", "Health_Background.png")
        ).convert_alpha()

        self.hp_empty = pygame.image.load(
            os.path.join(current_dir, "assets", "UI", "Health_Empty.png")
        ).convert_alpha()

        self.hp_full = pygame.image.load(
            os.path.join(current_dir, "assets", "UI", "Health_Full.png")
        ).convert_alpha()

        self.hp_background = pygame.transform.scale_by(
            self.hp_background, 6
        )

        self.hp_empty = pygame.transform.scale_by(
            self.hp_empty, 6
        )

        self.hp_full = pygame.transform.scale_by(
            self.hp_full, 6
        )

        self.potion_img = pygame.transform.scale_by(
            self.potion_img, 0.5
        )

    def draw(self, screen, player):

        x = 20
        y = 20

        hp_percent = max(0, player.hp) / 100

        full_width = self.hp_full.get_width()

        current_width = int(full_width * hp_percent)

        # 1. Background (darah hilang)
        screen.blit(self.hp_background, (x, y))

        # 2. Darah aktif
        if current_width > 0:

            hp_crop = self.hp_full.subsurface(
                (0, 0, current_width, self.hp_full.get_height())
            )

            screen.blit(hp_crop, (x, y))

        # 3. Frame
        screen.blit(self.hp_empty, (x, y))

        potion_x = x + self.hp_background.get_width() + 20
        potion_y = y

        screen.blit(self.potion_img, (potion_x, potion_y))

        font = pygame.font.SysFont(None, 36)

        jumlah_potion = len(player.inventory)

        text = font.render(
            f"x{jumlah_potion}",
            True,
            (255,255,255)
        )

        screen.blit(
            text,
            (
            potion_x + self.potion_img.get_width() + 3,
            potion_y + 15
            )
)


class PauseMenu:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        self.image = pygame.image.load(
    os.path.join(
        current_dir,
        "assets",
        "UI",
        "escape_menu1.png"
    )
    ).convert_alpha()

        self.image = pygame.transform.scale_by(
        self.image,
        4
        )

        self.rect = self.image.get_rect()
        self.play_rect = pygame.Rect(0, 0, 165, 70)
        self.exit_rect = pygame.Rect(0, 0, 165, 70)
        # self.exit_rect = pygame.Rect(0, 0, 165, 70)

        self.active = False

    def toggle(self):
        self.active = not self.active

    def draw(self, screen):
        if not self.active:
            return

        self.rect.center = (
            screen.get_width() // 2,
            screen.get_height() // 2
        )

        # posisi relatif terhadap panel

        self.play_rect.center = (
            self.rect.centerx,
            self.rect.top + 80
        )

        self.exit_rect.center = (
            self.rect.centerx,
            self.rect.top + 173
        )

        # self.exit_rect.center = (
        #     self.rect.centerx,
        #     self.rect.top + 265
        # )

        screen.blit(self.image, self.rect)

        # pygame.draw.rect(screen, (255,0,0), self.play_rect, 2)
        # pygame.draw.rect(screen, (0,255,0), self.options_rect, 2)
        # pygame.draw.rect(screen, (0,0,255), self.exit_rect, 2)

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
           if event.button == 1:

               if self.play_rect.collidepoint(event.pos):
                return "play"

            #    if self.options_rect.collidepoint(event.pos):
            #       return "options"

               if self.exit_rect.collidepoint(event.pos):
                   return "exit"

        return None

   