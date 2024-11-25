import pygame as pg

class Bird(pg.sprite.Sprite):
    def __init__(self, scale_factor, flap_sound):
        super(Bird, self).__init__()
        self.scale_factor = scale_factor  # Store scale_factor as an instance variable
        self.flap_sound = flap_sound  # Store flap_sound as an instance variable
        
        self.img_list = [
            pg.transform.scale_by(pg.image.load("assets/birdup.png").convert_alpha(), scale_factor),
            pg.transform.scale_by(pg.image.load("assets/birddown.png").convert_alpha(), scale_factor)
        ]
        self.image_index = 0
        self.image = self.img_list[self.image_index]
        self.rect = self.image.get_rect(center=(100, 100))
        self.y_velocity = 0
        self.gravity = 10
        self.flap_speed = 100
        self.anim_counter = 0
        self.update_on = False

    def update(self, dt):
        if self.update_on:
            self.playAnimation()
            self.applyGravity(dt)

            if self.rect.y <= 0 and self.flap_speed == 300:
                self.rect.y = 0
                self.flap_speed = 0
                self.y_velocity = 0
            elif self.rect.y > 0 and self.flap_speed == 0:
                self.flap_speed = 300

    def applyGravity(self, dt):
        self.y_velocity += self.gravity * dt
        self.rect.y += self.y_velocity

    def flap(self, dt):
        self.y_velocity = -3 * self.scale_factor  # Flap strength based on scale_factor
        self.flap_sound.play()  # Play the flap sound
    
    def playAnimation(self):
        if self.anim_counter == 5:
            self.image = self.img_list[self.image_index]
            if self.image_index == 0:
                self.image_index = 1
            else:
                self.image_index = 0
            self.anim_counter = 0

        self.anim_counter += 1
     