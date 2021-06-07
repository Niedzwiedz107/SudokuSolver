from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform

from App.GUI import MenuLayout
from App.GUI import CameraLayout
from App.Utils import Options


class MyGrid(FloatLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.size = (400, 800)

        self.title = Label(
            font_size=40,
            text="Sudoku",
            size_hint=(0.1, 0.1),
            pos_hint={"center_x": 0.5, "top": 1.0},
            color=(0.0, 0.0, 1.0))

        # App options
        self.options = Options.MyOptions()

        # Adding components
        self.add_widget(self.title)
        self.add_widget(MenuLayout.MenuButton(self.options))
        self.add_widget(CameraLayout.CameraLayout(self.options))


class MyApp(App):
    def build(self):
        self.title = "Sudoku Solver"
        return MyGrid()


if __name__ == '__main__':
    if platform == "android":
        from android.permissions import Permission, request_permissions


        def callback(permission, results):
            if all([res for res in results]):
                print("Got all permissions!")
            else:
                print("Did not get all permissions!")


        request_permissions([
            Permission.CAMERA,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE], callback)

    MyApp().run()
