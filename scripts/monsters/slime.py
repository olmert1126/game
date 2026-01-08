import arcade


class Slime:
    def __init__(self, x, y, colision_sprites, gravity=7):
        self.loading_texture()
        self.slime_sprites_list = arcade.SpriteList()

        self.speed = 3

        self.gravity = gravity

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0

        self.slime_sprite = arcade.Sprite()
        self.slime_sprite.texture = self.main_form
        self.slime_sprite.center_x = self.center_x
        self.slime_sprite.center_y = self.center_y
        self.slime_sprite.scale = 0.1

        self.slime_sprites_list.append(self.slime_sprite)

        self.physicks_engine = arcade.PhysicsEnginePlatformer(
            self.slime_sprite,
            colision_sprites,
            gravity_constant=self.gravity,
        )

    def on_update(self, delta_time):
        self.physicks_engine.update()

        self.slime_sprite.change_x = self.change_x

    def update_animation(self, delta_time: float = 1 / 60, jump=False):
        pass


    def loading_texture(self):
        self.main_form = arcade.load_texture("models/monsters/slime/slime_main_form.png")

    def draw(self):
        self.slime_sprites_list.draw()
