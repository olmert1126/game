import arcade
import hero_death_knight

SCREEN_WIDTH = arcade.get_display_size()[0]
SCREEN_HEIGHT = arcade.get_display_size()[1]
PLAYER_SIZE = 0.1
PLAYER_SPEED = 200

class Map(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, fullscreen=False)
        pass

    def setup(self):
        self.player1 = hero_death_knight.DeathKnight(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, PLAYER_SPEED, PLAYER_SIZE, 1)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.player1.draw()

    def on_update(self, delta_time):
        self.player1.update(delta_time)

    def on_key_press(self, key, modifiers):
        self.player1.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.player1.on_key_release(key, modifiers)

def setup_game(width=800, height=600, title="Тест карта"):
    game = Map(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


if __name__ == "__main__":
    main()
