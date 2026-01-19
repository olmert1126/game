import arcade

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction, speed=300, damage=40, scale=0.5):
        # Загружаем реальную текстуру
        super().__init__("models/wizard/1.png", scale=scale)
        self.center_x = x
        self.center_y = y
        self.damage = damage
        self.change_x = speed if direction == "right" else -speed
        self.direction = direction

    def update(self):
        self.center_x += self.change_x