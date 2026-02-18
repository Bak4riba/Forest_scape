import random
import math
from pygame import Rect

WIDTH = 800
HEIGHT = 800

GRAVITY = 0.5
GROUND_Y = 500


class Button:
    def __init__(self, text, center):
        self.text = text
        self.rect = Rect((0, 0), (200, 50))
        self.rect.center = center
        self.game_over_timer = 0
        self.time_survived = 0
        self.frame_counter = 0

    def draw(self):
        screen.draw.filled_rect(self.rect, "darkblue")
        screen.draw.rect(self.rect, "white")
        screen.draw.text(
            self.text,
            center=self.rect.center,
            fontsize=30,
            color="white"
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Character:
    def __init__(self, pos, idle_frames, run_frames):
        self.x, self.y = pos
        self.vx = 0
        self.vy = 0
        self.idle_frames = idle_frames
        self.run_frames = run_frames
        self.current_frames = idle_frames
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.current_frames[0]

    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.frame_index]
            self.animation_timer = 0

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Hero(Character):
    def update(self):
        keys = keyboard

        self.vx = 0

        if keys.left:
            self.vx = -4
            self.current_frames = self.run_frames
        elif keys.right:
            self.vx = 4
            self.current_frames = self.run_frames
        else:
            self.current_frames = self.idle_frames

        if keys.space and self.y >= GROUND_Y:
            self.vy = -10
            sounds.jump.play()

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if self.y > GROUND_Y:
            self.y = GROUND_Y
            self.vy = 0

        self.update_animation()


class Enemy(Character):
    def __init__(self, pos, idle_frames, run_frames, patrol_range):
        super().__init__(pos, idle_frames, run_frames)
        self.start_x = pos[0]
        self.patrol_range = patrol_range
        self.vx = 2

    def update(self):
        self.x += self.vx

        if abs(self.x - self.start_x) > self.patrol_range:
            self.vx *= -1

        self.current_frames = self.run_frames
        self.update_animation()


class Game:
    def __init__(self):
        self.state = "menu"
        self.music_on = True
        self.game_over_timer = 0
        self.time_survived = 0
        self.frame_counter = 0
        self.start_button = Button("Start Game", (WIDTH // 2, 250))
        self.sound_button = Button("Music On/Off", (WIDTH // 2, 320))
        self.exit_button = Button("Exit", (WIDTH // 2, 390))

        self.hero = Hero(
            (100, GROUND_Y),
            ["hero_idle_1", "hero_idle_2"],
            ["hero_run_1", "hero_run_2"]
        )

        self.enemies = [
            Enemy((300, GROUND_Y),
                  ["enemy_idle_1", "enemy_idle_2"],
                  ["enemy_run_1", "enemy_run_2"],
                  100),
            Enemy((450, GROUND_Y),
                  ["enemy_idle_1", "enemy_idle_2"],
                  ["enemy_run_1", "enemy_run_2"],
                  80),
            Enemy((500, GROUND_Y),
                  ["enemy_idle_1", "enemy_idle_2"],
                  ["enemy_run_1", "enemy_run_2"],
                  120),
        ]

    def draw(self):
        if self.state == "menu":
            screen.fill("black")
            self.start_button.draw()
            self.sound_button.draw()
            self.exit_button.draw()

        elif self.state == "game":
            screen.blit("background", (0, 0))
            self.hero.draw()
            self.frame_counter += 1

            # 60 frames ≈ 1 segundo
            if self.frame_counter >= 60:
                self.time_survived += 1
                self.frame_counter = 0
            for enemy in self.enemies:
                enemy.draw()
            screen.draw.text(
            f"Time: {self.time_survived}s",
            (20, 20),
            fontsize=30,
            color="white"
        )
        elif self.state == "game_over":
            screen.fill("black")
            screen.draw.text(
                "GAME OVER",
                center=(WIDTH // 2, HEIGHT // 2 - 40),
                fontsize=60,
                color="red"
            )
            screen.draw.text(
                "Click to return to menu",
                center=(WIDTH // 2, HEIGHT // 2 + 30),
                fontsize=30,
                color="white"
            )
            screen.draw.text(
                f"You survived: {self.time_survived} seconds",
                center=(WIDTH // 2, HEIGHT // 2 + 80),
                fontsize=30,
                color="white"
            )

            
            self.state = "menu"
            self.reset_game()

    def update(self):
        if self.state == "game":
            self.hero.update()

            for enemy in self.enemies:
                enemy.update()
                if self.check_collision(self.hero, enemy):
                    sounds.hit.play()
                    music.stop()
                    self.state = "game_over"

    def check_collision(self, hero, enemy):
        hero_rect = Rect(
            (hero.x + 10, hero.y + 10),
            (44, 54)
        )

        enemy_rect = Rect(
            (enemy.x + 20, enemy.y + 20),
            (34, 40)
        )

        return hero_rect.colliderect(enemy_rect)
    def reset_game(self):
        self.hero.x = 100
        self.hero.y = GROUND_Y
        self.hero.vx = 0
        self.hero.vy = 0

        for enemy in self.enemies:
            enemy.x = enemy.start_x


    def on_mouse_down(self, pos):
        if self.state == "menu":
            if self.start_button.is_clicked(pos):
                sounds.click.play()
                self.state = "game"
                if self.music_on:
                    music.play("theme")

            elif self.sound_button.is_clicked(pos):
                sounds.click.play()
                self.music_on = not self.music_on
                if self.music_on:
                    music.play("theme")
                else:
                    music.stop()

            elif self.state == "game_over":
                self.reset_game()
                self.state = "menu"
            elif self.exit_button.is_clicked(pos):
                exit()
        


game = Game()


def draw():
    screen.clear()
    game.draw()


def update():
    game.update()


def on_mouse_down(pos):
    game.on_mouse_down(pos)
