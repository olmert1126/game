import arcade
from scripts.modes.game_view import GameView
from arcade.gui import UIFlatButton, UIManager

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.manager.enable()

        self.flat_button = UIFlatButton(
            text="Запуск игры",
            width=200,
            height=50,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2 - 100  # чуть ниже текста
        )

        # Привязываем обработчик клика
        @self.flat_button.event("on_click")
        def on_click_button(event):
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        self.manager.add(self.flat_button)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Главное меню",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center"
        )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        pass

    def on_hide_view(self):
        # Отключаем UI, когда вид скрывается (хорошая практика)
        self.manager.disable()