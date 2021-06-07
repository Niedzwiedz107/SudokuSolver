from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from App.Sudoku import SudokuAlgorithms

import numpy as np
import cv2


class SudokuCreator(StackLayout):
    def __init__(self, my_options, **kw):
        super(SudokuCreator, self).__init__(**kw)
        self.my_options = my_options
        self.size_hint = (1.0, 0.8)
        self.pos_hint = {"top": 1.0}
        self._arrange_grid()

    def _arrange_grid(self):
        for i in range(81):
            single_field = Button(text=str(0), size_hint=(0.11, 0.11))
            single_field.bind(on_press=self._change_field_value)

            self.add_widget(single_field)

        save_button = Button(text="Save",
                             size_hint=(0.3, 0.15),
                             pos_hint={"top": 0.82},
                             on_press=self._save)

        self.add_widget(save_button)

    def _change_field_value(self, instance):
        instance.text = str((int(instance.text) + 1) % 10)

    def _save(self, instance):
        sudoku_matrix = np.zeros((9, 9), dtype=int)
        for i in range(9):
            for j in range(9):
                sudoku_matrix[i, j] = int(self.children[-((i * 9) + j + 1)].text)

        # Check correctness of sudoku
        if SudokuAlgorithms.check_correctness(sudoku_matrix):
            self._create_sudoku_img(sudoku_matrix)
        else:
            print("Invalid sudoku!")

    def _create_sudoku_img(self, matrix):
        img = np.zeros((408, 408), dtype=np.uint8)  # black img
        img = cv2.bitwise_not(img)
        x_dt = 408 // 9
        y_dt = 408 // 9

        # Create single box
        box = np.zeros((136, 136), dtype=np.uint8)
        box = cv2.bitwise_not(box)
        box[0:4, :] = 0
        box[132:, :] = 0
        box[:, 0:4] = 0
        box[:, 132:] = 0
        for i in range(44, 89, 44):
            box[i:i + 4, :] = 0
            box[:, i:i + 4] = 0

        # Copy box to img
        for i in range(3):
            for j in range(3):
                img[i * 136:i * 136 + 136, j * 136:j * 136 + 136] = box.copy()

        # Write sudoku digits
        for i in range(9):
            for j in range(9):
                if matrix[i, j] != 0:
                    cv2.putText(img, text="{}".format(matrix[i][j]),
                                org=(20 + j * x_dt, 35 + i * y_dt),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1.0,
                                thickness=3,
                                color=(0, 0, 0))

        cv2.imwrite("App/Pictures/sudoku_created.jpg", img)
        print("Sudoku created succesfuly!")
