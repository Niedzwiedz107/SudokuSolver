from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button


class RunModeChoice(StackLayout):
    def __init__(self, my_options, **kw):
        super(RunModeChoice, self).__init__(**kw)
        self.my_options = my_options
        self.size_hint = (1.0, 1.0)
        self.pos_hint = {"top": 1.0}
        self._create_buttons()

    def _create_buttons(self):
        mode1_button = Button(text="Offline",
                              size_hint=(1.0, 0.2),
                              pos_hint={"top": 0.8},
                              on_press=self._change_mode)
        self.add_widget(mode1_button)

        mode2_button = Button(text="Online",
                              size_hint=(1.0, 0.2),
                              pos_hint={"top": 0.6},
                              on_press=self._change_mode)
        self.add_widget(mode2_button)

    def _change_mode(self, instance):
        if instance.text == "Offline":
            print("RunMode: Offline")
            self.my_options.set_capture_mode("offline")
        elif instance.text == "Online":
            print("RunMode: Online")
            self.my_options.set_capture_mode("online")
