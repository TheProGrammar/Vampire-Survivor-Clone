import pygame

from player import Player
from enemy_manager import EnemyManager
from scoreboard import Scoreboard
from health_bar import HealthBar
from settings import *
from pause_menu import PauseMenu
from enemy_drop import EnemyDrop
from xp_bar import XPBar
from camera import Camera

class Level:
    def __init__(self, display, game_state_manager, clock):
        self.display = display
        self.game_state_manager = game_state_manager
        self.player = Player(self.display)
        self.camera = Camera(self.player, display.get_size())
        self.enemy_manager = EnemyManager(self.display, 20, 20)
        self.scoreboard = Scoreboard(self.display, clock)
        self.health_bar = HealthBar(self.display, self.player)
        self.pause_menu = PauseMenu(self.display, game_state_manager)
        self.drops = pygame.sprite.Group()
        self.xp_bar = XPBar(self.display, self.player)
        self.clock = clock


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu.is_paused = not self.pause_menu.is_paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button down events
                pass

    def check_collisions(self):
        """Handle player/enemy collisions and manage enemy attacks based on cooldown."""
        current_time = pygame.time.get_ticks()  # Get the current game time
        hits = pygame.sprite.spritecollide(self.player, self.enemy_manager.enemy_list, False, collided=pygame.sprite.collide_rect_ratio(0.6))
        for enemy in hits:
            enemy.attack(self.player, current_time)

    def check_slash_collisions(self):
        if self.player.slash_attack.active:
            enemies_hit = pygame.sprite.spritecollide(self.player.slash_attack, self.enemy_manager.enemy_list, dokill=True)
            for enemy in enemies_hit:
                self.scoreboard.current_score += 10  # Example of incrementing the score
                drop_type = EnemyDrop.determine_drop_type()
                drop = EnemyDrop(self.display, enemy.rect.center, drop_type, 2)
                self.drops.add(drop)

    def check_drop_collisions(self):
        drops_hit = pygame.sprite.spritecollide(self.player, self.drops, dokill=True, collided=pygame.sprite.collide_rect_ratio(0.5))
        for drop in drops_hit:
            if drop.drop_type == 'health':
                self.player.increase_health(10)
            elif drop.drop_type == 'exp':
                self.player.increase_xp(15)
            # Handle other drop types as needed

    def reset(self):
        self.player.reset()
        self.enemy_manager.reset()
        self.scoreboard.reset()

    def run(self, events):
        self.handle_events(events)
        current_time = pygame.time.get_ticks()

        if not self.pause_menu.is_paused:
            self.display.fill('black')
            self.camera.update()
            self.player.update()

            offset = (self.camera.offset_x, self.camera.offset_y)

            self.display.blit(self.player.image, self.player.rect.topleft - pygame.math.Vector2(offset))
            self.enemy_manager.update(self.player.rect.center, (self.camera.offset_x, self.camera.offset_y), current_time)

            for drop in self.drops:
                drop.draw(self.display, offset)

            if self.player.slash_attack.active:
                self.player.slash_attack.update()
                self.player.slash_attack.draw(self.display, offset)

            self.check_collisions()
            self.check_slash_collisions()
            self.check_drop_collisions()
            self.scoreboard.update()
            self.health_bar.update(offset)
            self.xp_bar.update(self.player.current_xp, self.player.xp_to_next_level)

        else:
            self.pause_menu.update(events)
            self.pause_menu.draw()