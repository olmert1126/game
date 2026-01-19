import arcade


class Wizard:
    def __init__(self, x, y, speed=100, scale=50, number_player=1, colision_sprites=None,
                 jump_speed=40, gravity=7, hp=250):
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.scale = scale
        self.is_alive = True

        self.number_player = number_player
        self.jump_speed = jump_speed
        self.gravity = gravity

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.up = False
        self.run = False

        # Анимации
        self.anim_run_right = []
        self.anim_run_left = []
        self.current_texture_run = 0
        self.texture_change_time_run = 0
        self.texture_change_delay_run = 0.2

        self.anim_jump = []
        self.current_texture_jump = 0
        self.texture_change_time_jump = 0
        self.texture_change_delay_jump = 0.2

        elf.weapon = None
        self.is_attacking = False
        self.has_dealt_damage_this_attack = False
        self.texture_change_time_attack = 0
        self.texture_change_delay_attack = 0.2
        self.current_texture_attack = 0

        self.loading_texture()

        # Спрайт — начинаем с нейтральной позы
        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.tex_default
        self.player_sprite.center_x = self.center_x
        self.player_sprite.center_y = self.center_y
        self.player_sprite.scale = self.scale

        self.facing = "default"  # может быть: "left", "right", "default"

        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            colision_sprites,
            gravity_constant=self.gravity,
        )

    def loading_texture(self):
        # Нейтральная стойка (по центру)
        self.tex_default = arcade.load_texture("models/hero/wizard/wizard.png")
        self.tex_right = arcade.load_texture("models/hero/wizard/wizard_right.png")
        self.tex_left = self.tex_right.flip_left_right()

        # Бег
        run_paths = [
            "models/hero/wizard/animations/run/1_faze_run.png",
            "models/hero/wizard/animations/run/2_faze_run.png",
            "models/hero/wizard/animations/run/3_faze_run.png",
            "models/hero/wizard/animations/run/4_faze_run.png"
        ]
        self.anim_run_right = [arcade.load_texture(path) for path in run_paths]
        self.anim_run_left = [tex.flip_left_right() for tex in self.anim_run_right]

        # Прыжок
        jump_paths = [
            "models/hero/wizard/animations/jump/jump1.png",
            "models/hero/wizard/animations/jump/jump2.png",
            "models/hero/wizard/animations/jump/jump3.png",
            "models/hero/wizard/animations/jump/jump4.png"
        ]
        self.anim_jump = [arcade.load_texture(path) for path in jump_paths]

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player_sprite.change_x = self.change_x

        if self.change_x > 0:
            self.facing = "right"
        elif self.change_x < 0:
            self.facing = "left"
        else:
            self.facing = "default"

        if self.physics_engine.can_jump():
            self.up = False

        # Анимация атаки
        if self.is_attacking and self.weapon:
            self.update_animation(delta_time, is_attacking=True)
        elif self.up:
            self.update_animation(delta_time, jump=True)
        elif self.run:
            self.update_animation(delta_time, run=True)
        else:
            if self.facing == "right":
                self.player_sprite.texture = self.tex_right
            elif self.facing == "left":
                self.player_sprite.texture = self.tex_left
            else:
                self.player_sprite.texture = self.tex_default

    def update_animation(self, delta_time, jump=False, run=False):
        if is_attacking and self.weapon:
            self.texture_change_time_attack += delta_time
            frames = self.weapon.attack_frames_right if self.facing == "right" else self.weapon.attack_frames_left

            if frames and self.texture_change_time_attack >= self.texture_change_delay_attack:
                self.texture_change_time_attack = 0
                self.current_texture_attack += 1

                if self.current_texture_attack < len(frames):
                    self.player_sprite.texture = frames[self.current_texture_attack]
                else:
                    # Анимация завершена
                    self.is_attacking = False
                    self.current_texture_attack = 0
                    # Вернуться в idle
                    if self.facing == "right":
                        self.player_sprite.texture = self.tex_right
                    elif self.facing == "left":
                        self.player_sprite.texture = self.tex_left
                    else:
                        self.player_sprite.texture = self.tex_default
            return

        if jump:
            self.texture_change_time_jump += delta_time
            if self.texture_change_time_jump >= self.texture_change_delay_jump:
                self.texture_change_time_jump = 0
                self.current_texture_jump = (self.current_texture_jump + 1) % len(self.anim_jump)
                self.player_sprite.texture = self.anim_jump[self.current_texture_jump]

        elif run:
            self.texture_change_time_run += delta_time
            if self.texture_change_time_run >= self.texture_change_delay_run:
                self.texture_change_time_run = 0
                if self.facing == "right":
                    self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_right)
                    self.player_sprite.texture = self.anim_run_right[self.current_texture_run]
                elif self.facing == "left":
                    self.current_texture_run = (self.current_texture_run + 1) % len(self.anim_run_left)
                    self.player_sprite.texture = self.anim_run_left[self.current_texture_run]

    def on_key_press(self, key, modifiers):
        if self.number_player == 1:
            if key == arcade.key.W and self.physics_engine.can_jump():
                self.physics_engine.jump(self.jump_speed)
                self.up = True
                self.run = False
            elif key == arcade.key.A:
                self.change_x = -self.speed
                self.run = True
            elif key == arcade.key.D:
                self.change_x = self.speed
                self.run = True
            elif key == arcade.key.E:
                return self.start_attack()
        elif self.number_player == 2:
            if key == arcade.key.UP and self.physics_engine.can_jump():
                self.physics_engine.jump(self.jump_speed)
                self.up = True
                self.run = False
            elif key == arcade.key.LEFT:
                self.change_x = -self.speed
                self.run = True
            elif key == arcade.key.RIGHT:
                self.change_x = self.speed
                self.run = True
            elif key == arcade.key.NUM0:
                return self.start_attack()
    def on_key_release(self, key, modifiers):
        if self.number_player == 1:
            if key in (arcade.key.A, arcade.key.D):
                self.change_x = 0
                self.run = False
        elif self.number_player == 2:
            if key in (arcade.key.LEFT, arcade.key.RIGHT):
                self.change_x = 0
                self.run = False

    def draw(self):
        self.player_sprite_list.draw()

    def take_damage(self, damage):
        if not self.is_alive:
            return
        self.hp -= damage
        if self.hp <= 0:
            self.death()
        print(f"Нанесено урона {damage}, осталось ХП: {self.hp}")

    def death(self):
        self.is_alive = False
        print("Погиб")

    def equip_weapon(self, weapon):
        self.weapon = weapon
        print(f"Подобрано оружие: {weapon.name}")

    def start_attack(self):
        if not self.is_attacking and self.weapon:
            self.is_attacking = True
            self.has_dealt_damage_this_attack = False
            self.texture_change_time_attack = 0
            self.current_texture_attack = 0
            frames = self.weapon.attack_frames_right if self.facing == "right" else self.weapon.attack_frames_left
            if frames:
                self.player_sprite.texture = frames[0]

            if self.weapon.is_ranged:
                # Позиция выстрела: чуть впереди героя
                shoot_x = self.center_x + (20 if self.facing == "right" else -20)
                shoot_y = self.center_y
                projectile = self.weapon.create_projectile(shoot_x, shoot_y, self.facing)
                return projectile  # вернём, чтобы добавить в список снарядов
        return None