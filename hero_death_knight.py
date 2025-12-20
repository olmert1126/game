import arcade

class DeathKnight:
    def __init__(self, x, y, speed=100, scale=50, number_player=1):
        self.speed = speed
        self.hp = 3
        self.scale = scale

        self.number_player = number_player

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0

        self.tex_default = arcade.load_texture("models/hero/death_knight/main_form.png")
        self.tex_right = arcade.load_texture("models/hero/death_knight/main_form_right.png")
        self.tex_left = arcade.load_texture("models/hero/death_knight/main_form_left.png")

        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.tex_default
        self.player_sprite.center_x = self.center_x
        self.player_sprite.center_y = self.center_y
        self.player_sprite.scale = self.scale

        self.facing = "default"

        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        self.player_sprite.center_x = self.center_x
        self.player_sprite.center_y = self.center_y

        if self.change_x > 0:
            self.player_sprite.texture = self.tex_right
            self.facing = "right"
        elif self.change_x < 0:
            self.player_sprite.texture = self.tex_left
            self.facing = "left"
        else:
            self.player_sprite.texture = self.tex_default
            self.facing = "default"

    def draw(self):
        self.player_sprite_list.draw()

    def on_key_press(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.W:
                self.change_y = self.speed
            elif key == arcade.key.S:
                self.change_y = -self.speed
            elif key == arcade.key.A:
                self.change_x = -self.speed
            elif key == arcade.key.D:
                self.change_x = self.speed
        elif self.number_player == 2:
            if key == arcade.key.UP:
                self.change_y = self.speed
            elif key == arcade.key.DOWN:
                self.change_y = -self.speed
            elif key == arcade.key.LEFT:
                self.change_x = -self.speed
            elif key == arcade.key.RIGHT:
                self.change_x = self.speed

    def on_key_release(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.W or key == arcade.key.S:
                self.change_y = 0
            elif key == arcade.key.A or key == arcade.key.D:
                self.change_x = 0
        elif self.number_player == 2:
            if key == arcade.key.UP or key == arcade.key.DOWN:
                self.change_y = 0
            elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.change_x = 0
