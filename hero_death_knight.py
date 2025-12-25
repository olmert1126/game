import arcade


class DeathKnight:
    def __init__(self, x, y, speed=100, scale=50, number_player=1, colision_sprites=None, jump_speed=40, gravity=7, coyote_time=None):
        self.speed = speed
        self.hp = 3
        self.scale = scale

        self.number_player = number_player
        self.jump_speed = jump_speed
        self.gravity = gravity

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.up = False

        self.anim_run_right = []
        self.anim_run_left = []
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2

        self.run = False

        self.loading_texture()
        self.anim_run_right.append(self.one_shot_run)
        self.anim_run_right.append(self.two_shot_run)
        self.anim_run_right.append(self.three_shot_run)
        self.anim_run_right.append(self.four_shot_run)
        self.anim_run_left.append(self.one_shot_run_left)
        self.anim_run_left.append(self.two_shot_run_left)
        self.anim_run_left.append(self.three_shot_run_left)
        self.anim_run_left.append(self.four_shot_run_left)

        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.tex_default
        self.player_sprite.center_x = self.center_x
        self.player_sprite.center_y = self.center_y
        self.player_sprite.scale = self.scale

        self.facing = "default"

        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.physicks_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, colision_sprites)

    def on_update(self, delta_time):
        self.player_sprite.change_x = self.change_x * delta_time

        if self.change_x > 0:
            self.facing = "right"
        elif self.change_x < 0:
            self.facing = "left"
        elif self.change_x == 0:
            self.facing = "default"

        if self.run:
            self.update_animation(delta_time)
        else:
            if self.facing == "right":
                self.player_sprite.texture = self.tex_right
            elif self.facing == "left":
                self.player_sprite.texture = self.tex_left
            else:
                self.player_sprite.texture = self.tex_default

        if self.run:
            self.update_animation(delta_time)

        if self.up:
            self.physicks_engine.jump(self.jump_speed)

    def update_animation(self, delta_time: float = 1 / 60):
        if self.run:
            if self.facing == "right":
                self.texture_change_time_run += delta_time
                if self.texture_change_time_run >= self.texture_change_delay_run:
                    self.texture_change_time_run = 0
                    self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)
                    texture = self.anim_run_right[self.current_texture_run]
                    self.player_sprite.texture = texture
            elif self.facing == "left":
                self.texture_change_time_run += delta_time
                if self.texture_change_time_run >= self.texture_change_delay_run:
                    self.texture_change_time_run = 0
                    self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_left)
                    texture = self.anim_run_left[self.current_texture_run]
                    self.player_sprite.texture = texture


    def loading_texture(self):
        self.tex_default = arcade.load_texture("models/hero/death_knight/main_form.png")
        self.tex_right = arcade.load_texture("models/hero/death_knight/main_form_right.png")
        self.tex_left = self.tex_right.flip_left_right()

        self.one_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/1_faze_run.png")
        self.two_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/2_faze_run.png")
        self.three_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/3_faze_run.png")
        self.four_shot_run = arcade.load_texture("models/hero/death_knight/animations/run/4_faze_run.png")
        self.one_shot_run_left  = self.one_shot_run.flip_left_right()
        self.two_shot_run_left = self.two_shot_run.flip_left_right()
        self.three_shot_run_left = self.three_shot_run.flip_left_right()
        self.four_shot_run_left = self.four_shot_run.flip_left_right()

    def draw(self):
        self.player_sprite_list.draw()

    def on_key_press(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.W:
                if self.physicks_engine.can_jump():
                    self.physicks_engine.jump(self.jump_speed)
            elif key == arcade.key.A:
                self.change_x = -self.speed
                self.run = True
            elif key == arcade.key.D:
                self.run = True
                self.change_x = self.speed
        elif self.number_player == 2:
            if key == arcade.key.UP:
                if self.physicks_engine.can_jump():
                    self.physicks_engine.jump(self.jump_speed)
            elif key == arcade.key.LEFT:
                self.change_x = -self.speed
                self.run = True
            elif key == arcade.key.RIGHT:
                self.change_x = self.speed
                self.run = True

    def on_key_release(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.A or key == arcade.key.D:
                self.change_x = 0
                self.run = False
                self.current_texture_run = 0
        elif self.number_player == 2:
            if key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.change_x = 0
                self.run = False
                self.current_texture_run = 0
