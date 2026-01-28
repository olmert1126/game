import arcade
from scripts.modes.game_view import GameView
from scripts.modes.statistic_view import StatisticsView
from arcade.gui import UIFlatButton, UIManager


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.manager.enable()

        # Кнопка "Запуск игры"
        self.start_button = UIFlatButton(
            text="Запуск игры",
            width=200,
            height=50,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2 - 60
        )

        @self.start_button.event("on_click")
        def on_click_start(event):
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        # Кнопка "Статистика"
        self.stats_button = UIFlatButton(
            text="Статистика",
            width=200,
            height=50,
            center_x=self.window.width / 2,
            center_y=self.window.height / 2 - 130  # ниже первой кнопки
        )

        @self.stats_button.event("on_click")
        def on_click_stats(event):
            stats_view = StatisticsView()
            self.window.show_view(stats_view)

        self.manager.add(self.start_button)
        self.manager.add(self.stats_button)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        # Центрируем кнопки при показе (на случай изменения размера окна)
        self.start_button.center_x = self.window.width / 2
        self.start_button.center_y = self.window.height / 2 - 60
        self.stats_button.center_x = self.window.width / 2
        self.stats_button.center_y = self.window.height / 2 - 130

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Главное меню",
            self.window.width / 2,
            self.window.height / 2 + 40,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center"
        )
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()
