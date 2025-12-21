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

        self.anim_run = []
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.1

        self.run = False

        self.loading_texture()
        self.anim_run.append(self.one_shot_run)
        self.anim_run.append(self.two_shot_run)
        self.anim_run.append(self.three_shot_run)
        self.anim_run.append(self.four_shot_run)

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

        if self.change_x > 0 and self.run == False:
            self.player_sprite.texture = self.tex_right
            self.facing = "right"
        elif self.change_x < 0 and self.run == False:
            self.player_sprite.texture = self.tex_left
            self.facing = "left"
        elif self.change_x == 0 and self.run == False:
            self.player_sprite.texture = self.tex_default
            self.facing = "default"

        if self.run:
            self.update_animation(delta_time)

    def update_animation(self, delta_time: float = 1 / 60):
        if self.run:
            self.texture_change_time_run += delta_time
            if self.texture_change_time_run >= self.texture_change_delay_run:
                self.texture_change_time_run = 0
                self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run)

                texture = self.anim_run[self.current_texture_run]

                if self.facing == "left":
                    pass

                self.player_sprite.texture = texture

    def loading_texture(self):
        self.tex_default = arcade.load_texture("models/hero/death_knight/main_form.png")
        self.tex_right = arcade.load_texture("models/hero/death_knight/main_form_right.png")
        self.tex_left = self.tex_right.flip_left_right()

        self.one_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/1_faze_run.png")
        self.two_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/2_faze_run.png")
        self.three_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/3_faze_run.png")
        self.four_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/4_faze_run.png")

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
                self.run = True
            elif key == arcade.key.D:
                self.run = True
                self.change_x = self.speed
        elif self.number_player == 2:
            if key == arcade.key.UP:
                self.change_y = self.speed
            elif key == arcade.key.DOWN:
                self.change_y = -self.speed
            elif key == arcade.key.LEFT:
                self.change_x = -self.speed
                self.run = True
            elif key == arcade.key.RIGHT:
                self.change_x = self.speed
                self.run = True

    def on_key_release(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.W or key == arcade.key.S:
                self.change_y = 0
            elif key == arcade.key.A or key == arcade.key.D:
                self.change_x = 0
                self.run = False
                self.current_texture_run = 0
        elif self.number_player == 2:
            if key == arcade.key.UP or key == arcade.key.DOWN:
                self.change_y = 0
            elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.change_x = 0
                self.run = False
                self.current_texture_run = 0
