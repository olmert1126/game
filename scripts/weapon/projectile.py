import arcade

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction, speed=8, damage=40, scale=0.5, walls=None, max_distance=900):
        texture = arcade.make_soft_circle_texture(50, arcade.color.BLUE)
        super().__init__(texture, scale=scale)

        self.center_x = x
        self.center_y = y
        self.start_x = x
        self.damage = damage
        self.speed = speed
        self.direction = direction

    def update(self, delta_time):
        move = self.speed * delta_time
        if self.direction == "right":
            self.center_x += move
        else:
            self.center_x -= move

