import arcade
import sqlite3

class StatisticsView(arcade.View):
    def __init__(self):
        super().__init__()
        self.monster_stats = []  # Список кортежей (имя, убийства)
        self.load_statistics()

    def load_statistics(self):
        """Загружает статистику из базы данных."""
        try:
            conn = sqlite3.connect('scripts/statistic.db')
            cursor = conn.cursor()
            cursor.execute("SELECT monsters, kills FROM statistic ORDER BY kills DESC")
            self.monster_stats = cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при загрузке статистики: {e}")
            self.monster_stats = [("Ошибка", 0)]
        finally:
            if 'conn' in locals():
                conn.close()

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Статистика убийств монстров",
            self.window.width // 2,
            self.window.height - 60,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center"
        )

        start_y = self.window.height - 120
        line_height = 40
        for i, (name, kills) in enumerate(self.monster_stats):
            text = f"{name}: {kills}"
            arcade.draw_text(
                text,
                self.window.width // 2,
                start_y - i * line_height,
                arcade.color.LIGHT_GREEN,
                font_size=24,
                anchor_x="center"
            )

        arcade.draw_text(
            "Нажмите ESC или ENTER, чтобы вернуться",
            self.window.width // 2,
            40,
            arcade.color.GRAY,
            font_size=18,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE or key == arcade.key.ENTER:
            from scripts.modes.start_view import StartView
            main_menu = StartView()
            self.window.show_view(main_menu)
