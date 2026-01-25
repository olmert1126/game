import arcade

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction, speed=50, damage=40, scale=0.5, walls=None, max_distance=900):
        super().__init__("models/items/ball.png", scale=scale)
        self.center_x = x
        self.center_y = y
        self.start_x = x
        self.damage = damage
        self.change_x = speed if direction == "right" else -speed
        self.direction = direction
        self.walls = walls or arcade.SpriteList()
        self.max_distance = max_distance

    def update(self, delta_time):
        self.center_x += self.change_x

        # Удаление по дистанции
        if abs(self.center_x - self.start_x) > self.max_distance:
            self.remove_from_sprite_lists()
            return

        # Удаление при столкновении со стенами
        if arcade.check_for_collision_with_list(self, self.walls):
            self.remove_from_sprite_lists()
