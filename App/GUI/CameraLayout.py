from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.texture import Texture
from kivy.utils import platform
from kivy.clock import Clock
import cv2
import numpy as np
import time

from kivy_garden.xcamera import XCamera
from App.Sudoku import SudokuFinder, SudokuAlgorithms


class CameraLayout(FloatLayout):
    def __init__(self, my_options, **kwargs):
        super(CameraLayout, self).__init__(**kwargs)
        self.my_options = my_options
        self.size_hint = (1.0, 0.9)
        self.cam = CameraCV(my_options)
        self.add_widget(self.cam)


class CameraCV(XCamera):
    def __init__(self, my_options, **kwargs):
        super(CameraCV, self).__init__(**kwargs)
        self.my_options = my_options
        self.allow_stretch = True
        self.keep_ratio = False
        self.size_hint = (1.0, 1.0)
        self.photo_idx = 0
        self.frame = None
        self.frame_oryginal = None
        self.frame_online = None
        self.SudokuFinder = SudokuFinder.SudokuFinder(self.my_options)
        Clock.schedule_interval(self.on_tex, 1.0 / 60.0)

    def on_tex(self, *l):
        # Get run mode option
        run_mode = self.my_options.get_capture_mode()

        if run_mode == "online" and self.frame_online is not None:
            time.sleep(4)

        # Get frame from texture
        if platform == "win":
            if self._camera.texture is None:
                return
            frame = np.frombuffer(self._camera.texture.pixels, dtype=np.uint8)
            frame = np.reshape(frame, (self.texture_size[1], self.texture_size[0], 4))
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif platform == "linux":
            if self._camera._texture is None:
                return
            frame = np.frombuffer(self._camera._texture.pixels, dtype=np.uint8)
            frame = np.reshape(frame, (self.texture_size[1], self.texture_size[0], 4))
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif platform == "android":
            if self._camera._buffer is None:
                return
            w, h = self.resolution
            frame = np.frombuffer(self._camera._buffer.tostring(), dtype=np.uint8).reshape((h + h // 2, w))
            frame = cv2.cvtColor(frame, 93)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.frame_oryginal = self.frame.copy()

        # Find sudoku contour
        sudoku_contour = self.SudokuFinder.find_sudoku_contour(self.frame)
        if sudoku_contour is not None:
            # Draw sudoku contours
            cv2.drawContours(self.frame, [sudoku_contour], 0, (0, 255, 0), 3)

        # Convert frame to texture
        if platform == "android":
            changed_texture_size = [self.texture_size[1], self.texture_size[0]]
            buf = self.frame.tostring()
            image_texture = Texture.create(size=changed_texture_size, colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        else:
            if run_mode == "online":
                self.frame_online = self._get_result_img()
                if self.frame_online is not None:
                    self.frame = self.frame_online

            self.frame = cv2.rotate(self.frame, rotateCode=1)
            self.frame = cv2.flip(self.frame, 1)
            buf = self.frame.tostring()
            image_texture = Texture.create(size=self.texture_size, colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.texture = image_texture

    def _get_result_img(self):
        # Get sudoku matrix
        sudoku_arr = self.SudokuFinder.sudoku_to_array(self.frame_oryginal)

        if sudoku_arr is None:
            return None

        # Solve sudoku
        result_arr = None
        algorithm_mode = self.my_options.get_algorithm_mode()

        if algorithm_mode == "naive":
            result_arr = SudokuAlgorithms.solve_naive(sudoku_arr.copy())
        elif algorithm_mode == "backtracking":
            result_arr = SudokuAlgorithms.solve_backtracking(sudoku_arr.copy())

        # Create result img
        result_img = None
        if result_arr is not None:
            result_img = self.SudokuFinder.print_result(self.frame_oryginal, sudoku_arr, result_arr)

        if result_img is not None:
            return result_img
        else:
            return None

    def shoot(self):
        # Get result img
        result_img = self._get_result_img()
        # Save
        if result_img is not None:
            cv2.imwrite(f'App/Pictures/IMG_{self.photo_idx}.jpg', result_img)
            print("Succesfuly saved solved sudoku!")
            self.photo_idx += 1
