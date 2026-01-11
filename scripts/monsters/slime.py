import arcade

class Slime:
    def __init__(self, x, y, collision_sprites, gravity=0.5):
        self.loading_texture()
        self.slime_sprites_list = arcade.SpriteList()

        self.speed = 3
        self.facing = "right"

        self.gravity = gravity

        self.center_x = x
        self.center_y = y
        self.change_x = self.speed
        self.change_y = 0
        self.on_ground = False

        self.anim_run_right = []
        self.anim_run_left = []
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2
        self.run = True

        self.slime_sprite = arcade.Sprite()
        self.slime_sprite.texture = self.main_form
        self.slime_sprite.center_x = self.center_x
        self.slime_sprite.center_y = self.center_y
        self.slime_sprite.scale = 0.12

        self.slime_sprites_list.append(self.slime_sprite)

        self.collision_sprites = collision_sprites

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.slime_sprite,
            collision_sprites,
            gravity_constant=self.gravity,
        )

        # Анимации
        self.anim_run_right = [
            self.one_shot_run,
            self.two_shot_run,
            self.three_shot_run,
            self.four_shot_run
        ]
        self.anim_run_left = [
            self.one_shot_run_left,
            self.two_shot_run_left,
            self.three_shot_run_left,
            self.four_shot_run_left
        ]

    def loading_texture(self):
        self.main_form = arcade.load_texture("models/monsters/slime/slime_main_form.png")
        self.main_form_left = self.main_form.flip_left_right()

        self.one_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run1.png")
        self.two_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run2.png")
        self.three_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run3.png")
        self.four_shot_run = arcade.load_texture("models/monsters/slime/animations/run/run4.png")
        self.one_shot_run_left = self.one_shot_run.flip_left_right()
        self.two_shot_run_left = self.two_shot_run.flip_left_right()
        self.three_shot_run_left = self.three_shot_run.flip_left_right()
        self.four_shot_run_left = self.four_shot_run.flip_left_right()

    def on_update(self, delta_time):
        # Обновляем физику
        self.physics_engine.update()
        direction = 1 if self.facing == "right" else -1
        next_x = self.slime_sprite.center_x + self.speed * direction

        # Создаём тестовые спрайты для проверки
        test_front = arcade.Sprite(center_x=next_x, center_y=self.slime_sprite.center_y)
        test_front.texture = self.main_form
        test_front.scale = self.slime_sprite.scale
        front_collisions = arcade.check_for_collision_with_list(test_front, self.collision_sprites)

        if front_collisions:
            self._reverse_direction()
        else:
            self.slime_sprite.center_x = next_x

        self.update_animation(delta_time)

    def _reverse_direction(self):
        self.facing = "left" if self.facing == "right" else "right"
        self.current_texture_run = 0

    def update_animation(self, delta_time: float = 1 / 60):
        self.texture_change_time_run += delta_time
        if self.texture_change_time_run >= self.texture_change_delay_run:
            self.texture_change_time_run = 0
            self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)

            if self.facing == "right":
                self.slime_sprite.texture = self.anim_run_right[self.current_texture_run]
            else:
                self.slime_sprite.texture = self.anim_run_left[self.current_texture_run]

    def draw(self):
        self.slime_sprites_list.draw()
