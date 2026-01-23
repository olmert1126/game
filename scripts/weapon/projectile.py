import arcade

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction, speed=8, damage=40, scale=0.5, walls=None, max_distance=900):
        # super().__init__("models/items/ball.png", scale=scale)  # ← ЗАКОММЕНТИРУЙТЕ ЭТО
        super().__init__()  # ← Создаём пустой спрайт
        self.texture = arcade.make_soft_circle_texture(20, arcade.color.BLUE)  # ← Цветной круг
        self.scale = scale  # ← Масштаб

        self.center_x = x
        self.center_y = y
        self.start_x = x
        self.damage = damage
        self.speed = speed
        self.direction = direction
        self.max_distance = max_distance

        # Создаём SpriteList из walls
        self.walls = arcade.SpriteList()
        if isinstance(walls, list):
            for wall in walls:
                if isinstance(wall, arcade.Sprite):
                    self.walls.append(wall)
        elif isinstance(walls, arcade.SpriteList):
            self.walls.extend(walls)

    def update(self, delta_time):
        move = self.speed * delta_time
        if self.direction == "right":
            self.center_x += move
        else:
            self.center_x -= move

        if abs(self.center_x - self.start_x) > self.max_distance:
            self.remove_from_sprite_lists()
            return

        if arcade.check_for_collision_with_list(self, self.walls):
            self.remove_from_sprite_lists()
