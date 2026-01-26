import arcade

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction, speed=50, damage=40, scale=0.5, max_distance=2000):
        super().__init__("models/items/ball.png", scale=scale)
        self.center_x = x
        self.center_y = y
        self.start_x = x
        self.damage = damage
        self.change_x = speed if direction == "right" else -speed
        self.direction = direction
        self.max_distance = max_distance

    def update(self, delta_time):
        self.center_x += self.change_x

        # Удаляем только если превышена максимальная дистанция
        if abs(self.center_x - self.start_x) > self.max_distance:
            self.remove_from_sprite_lists()