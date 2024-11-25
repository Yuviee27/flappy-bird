import pygame as pg
import sys
import time
from Bird import Bird
from pipe import Pipe

pg.init()


class Game:
    def __init__(self):
        # Setting window configuration
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.move_speed = 250
        self.flap_sound = pg.mixer.Sound("assets/flap.wav")  # Load the flap sound
        self.bird = Bird(self.scale_factor, self.flap_sound)
        self.collision_sound = pg.mixer.Sound("assets/dead.wav")
        self.score_sound = pg.mixer.Sound("assets/score.wav")

        # Game states
        self.is_enter_pressed = False
        self.game_over = False
        self.pipes = []
        self.pipe_generate_counter = 71
        self.score = 0
        self.high_score = self.load_high_score()  # Load high score from file

        # Fonts
        self.font = pg.font.Font(None, 50)
        self.large_font = pg.font.Font(None, 100)

        self.setUpBgAndGround()
        self.start_screen()

    def start_screen(self):
        # Display the start screen
        while not self.is_enter_pressed:
            self.win.fill((0, 0, 255))
            self.draw_text("Flappy Bird", self.large_font, (255, 255, 255), self.width // 2, self.height // 3)
            self.draw_text("Press ENTER to Start", self.font, (255, 255, 255), self.width // 2, self.height // 2)
            self.draw_text(f"High Score: {self.high_score}", self.font, (255, 255, 0), self.width // 2, self.height // 2 + 50)
            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.is_enter_pressed = True
                    self.bird.update_on = True

        self.gameLoop()

    def gameLoop(self):
        last_time = time.time()
        while True:
            # Calculating delta time
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN and self.game_over:  # Restart game
                        self.reset_game()
                    elif event.key == pg.K_SPACE and not self.game_over:  # Flap
                        self.bird.flap(dt)

            if not self.game_over:
                self.updateEverything(dt)
                self.checkCollisions()

            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def checkCollisions(self):
        # Collision with ground or pipes
        if self.bird.rect.bottom > 568 or any(
            self.bird.rect.colliderect(pipe.rect_up) or self.bird.rect.colliderect(pipe.rect_down)
            for pipe in self.pipes
        ):
            self.bird.update_on = False
            self.game_over = True
            self.collision_sound.play()  # Play collision sound when collision occurs
            self.update_high_score()

    def update_high_score(self):
        # Update and save high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def load_high_score(self):
        # Load high score from file
        try:
            with open("high_score.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        # Save high score to file
        with open("high_score.txt", "w") as file:
            file.write(str(self.high_score))

    def updateEverything(self, dt):
        if self.is_enter_pressed and not self.game_over:
            # Moving the ground
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            # Generating pipes
            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0

            self.pipe_generate_counter += 1

            # Moving the pipes
            for pipe in self.pipes:
                pipe.update(dt)

            # Removing pipes and updating score
            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)
                    self.score += 1
                    self.score_sound.play()  # Play score sound when a point is earned

            # Moving the bird
            self.bird.update(dt)

    def drawEverything(self):
        self.win.blit(self.bg_img, (0, -300))
        for pipe in self.pipes:
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        # Draw the score and high score
        self.draw_text(f"Score: {self.score}", self.font, (255, 255, 255), self.width // 8, 30)
        self.draw_text(f"High Score: {self.high_score}", self.font, (0, 255, 255), self.width // 5, 70)

        if self.game_over:
            self.draw_text("Game Over", self.large_font, (255, 0, 0), self.width // 2, self.height // 3)
            self.draw_text("Press ENTER to Restart", self.font, (255, 165, 0), self.width // 2, self.height // 2)

    def setUpBgAndGround(self):
        # Loading images for bg and ground
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

    def reset_game(self):
        # Reset game state
        self.bird.rect.center = (100, 100)  # Reset bird position
        self.bird.y_velocity = 0  # Reset vertical velocity
        self.bird.update_on = True

        self.pipes = []  # Clear pipes
        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.pipe_generate_counter = 71
        self.score = 0  # Reset score
        self.game_over = False

    def draw_text(self, text, font, color, x, y):
        # Draw text centered at (x, y)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.win.blit(text_surface, text_rect)


# Run the game
game = Game()
