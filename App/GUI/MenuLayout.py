from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from App.GUI import AlgorithmChoice, SudokuCreator, RunModeChoice


class MenuWindow(RelativeLayout):
    def __init__(self, my_options, **kw):
        super(MenuWindow, self).__init__(**kw)
        self.my_options = my_options

        self.info_button = Button(
            text="Info",
            size_hint=(1.0, 0.2),
            pos_hint={"top": 1.0},
            on_press=self.show_info)

        self.mode_button = Button(
            text="Algorithm",
            size_hint=(1.0, 0.2),
            pos_hint={"top": 0.8},
            on_press=self.show_algorithms)

        self.run_mode_button = Button(
            text="Run modes",
            size_hint=(1.0, 0.2),
            pos_hint={"top": 0.6},
            on_press=self.show_run_modes)

        self.sudoku_creator_button = Button(
            text="Create Sudoku",
            size_hint=(1.0, 0.2),
            pos_hint={"top": 0.4},
            on_press=self.show_sudoku_creator)

        # Adding menu buttons
        self.add_widget(self.info_button)
        self.add_widget(self.mode_button)
        self.add_widget(self.run_mode_button)
        self.add_widget(self.sudoku_creator_button)

    def show_info(self, instance):
        info_label = Popup(
            title="About",
            size_hint=(0.8, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            content=InfoLabel(self))
        info_label.open()

    def show_algorithms(self, instance):
        algorithms_label = Popup(
            title="Algorithms to choose",
            size_hint=(0.5, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            content=AlgorithmChoice.AlgorithmChoice(self.my_options))
        algorithms_label.open()

    def show_run_modes(self, instance):
        run_mode_label = Popup(
            title="Run modes to choose",
            size_hint=(0.5, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            content=RunModeChoice.RunModeChoice(self.my_options))
        run_mode_label.open()

    def show_sudoku_creator(self, instance):
        sudoku_creation_label = Popup(
            title="Sudoku builder",
            size_hint=(0.8, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            content=SudokuCreator.SudokuCreator(self.my_options))
        sudoku_creation_label.open()


class MenuButton(Button):
    def __init__(self, my_options, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.font_size = 20
        self.text = "Menu"
        self.size_hint = (0.15, 0.1)
        self.pos_hint = {"right": 1.0, "top": 1.0}
        self.background_color = (0.0, 1.0, 0.0)
        self.menu_window = Popup(
            title="Menu",
            size_hint=(0.4, 0.8),
            pos_hint={"center_x": 0.78, "center_y": 0.5},
            content=MenuWindow(my_options))

    def on_press(self):
        print("Menu button clicked!")
        self.menu_window.open()


class InfoLabel(Label):
    def __init__(self, parent, **kwargs):
        super(InfoLabel, self).__init__(**kwargs)
        self.size = self.texture_size
        self.pos_hint = {"top": 1.0}
        self.text_size = parent.width, None
        self.text = "Sudoku solver app \n" \
                    "Click photo button to take a picture \n" \
                    "Your pictures will be saved in pictures folder"
