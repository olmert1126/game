import arcade
from scripts.weapon.projectile import Projectile

class StaffWeapon:
    def __init__(self, name="staff", damage=40, attack_duration_frames=3,
                 projectile_speed=8, projectile_scale=0.3):
        self.name = name
        self.damage = damage
        self.attack_duration_frames = attack_duration_frames
        self.is_ranged = True
        self.projectile_speed = projectile_speed
        self.projectile_scale = projectile_scale

        self.attack_frames_right = []
        self.attack_frames_left = []

    def load_attack_animations(self, base_path, frame_count):
        for i in range(1, frame_count + 1):
            path = f"{base_path}/staff_attack{i}.png"
            tex_left = arcade.load_texture(path)
            tex_right = tex_left.flip_left_right()
            self.attack_frames_right.append(tex_right)
            self.attack_frames_left.append(tex_left)

    def create_projectile(self, x, y, direction, walls=None):  # ← ДОБАВИЛИ walls!
        return Projectile(
            x=x,
            y=y,
            direction=direction,
            speed=self.projectile_speed,
            damage=self.damage,
            scale=self.projectile_scale,
            walls=walls
        )

    @classmethod
    def create_staff(cls):
        return cls()

