from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button


class AlgorithmChoice(StackLayout):
    def __init__(self, my_options, **kw):
        super(AlgorithmChoice, self).__init__(**kw)
        self.my_options = my_options
        self.size_hint = (1.0, 1.0)
        self.pos_hint = {"top": 1.0}
        self._create_buttons()

    def _create_buttons(self):
        alg1_button = Button(text="Naive",
                             size_hint=(1.0, 0.2),
                             pos_hint={"top": 0.8},
                             on_press=self._change_mode)
        self.add_widget(alg1_button)

        alg2_button = Button(text="Backtracking",
                             size_hint=(1.0, 0.2),
                             pos_hint={"top": 0.6},
                             on_press=self._change_mode)
        self.add_widget(alg2_button)

    def _change_mode(self, instance):
        if instance.text == "Naive":
            print("Algorithm: Naive")
            self.my_options.set_algorithm_mode("naive")
        elif instance.text == "Backtracking":
            print("Algorithm: Backtracking")
            self.my_options.set_algorithm_mode("backtracking")
