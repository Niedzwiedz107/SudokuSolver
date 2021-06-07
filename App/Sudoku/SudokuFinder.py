import numpy as np
import cv2

from easyocr import Reader


class SudokuFinder:
    def __init__(self, my_options):
        try:
            self.reader = Reader(['en'], gpu=True)
        except FileNotFoundError:
            print("Downloading model failure, check your network connection!")

        self.my_options = my_options
        self.wait_key = 100
        self.sudoku_warped = None
        self.sudoku_contour = None
        self.M = None

    def find_sudoku_contour(self, frame, epsilon=0.1):
        # Preprocess frame
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_blur = cv2.GaussianBlur(frame_gray, (3, 3), 0)
        threshold = cv2.adaptiveThreshold(frame_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Get contours
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort contours
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        height, weight = frame.shape[:2]
        max_area = height * weight
        sudoku_contour = None
        # Find sudoku contour
        for contour in contours:
            if cv2.contourArea(contour) < 0.9 * max_area:
                approx_length = epsilon * cv2.arcLength(contour, True)
                approx_poly = cv2.approxPolyDP(contour, approx_length, True)
                if len(approx_poly) == 4:
                    sudoku_contour = approx_poly
                    break

        self.sudoku_contour = sudoku_contour
        if self.sudoku_contour is not None:
            return self.sudoku_contour
        else:
            return None

    def _prepare_digit_img(self, digit_img):
        img = cv2.resize(digit_img, (150, 150), interpolation=cv2.INTER_AREA)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=1)
        img = cv2.GaussianBlur(img, (3, 3,), 0)
        return img

    def _find_digit(self, text):
        for c in text:
            if c.isdigit():
                return c
        return 0

    def _order_points(self, corners):
        # Order points as top left, top right, bottom left, bottom right
        points = np.zeros((4, 2), dtype="float32")

        sum = corners.sum(axis=1)
        points[0] = np.ceil(corners[np.argmin(sum)])
        points[3] = np.ceil(corners[np.argmax(sum)])

        diff = np.diff(corners, axis=1)
        points[1] = np.ceil(corners[np.argmin(diff)])
        points[2] = np.ceil(corners[np.argmax(diff)])
        return points

    def sudoku_to_array(self, frame, epsilon=0.1):
        sudoku_contour = self.sudoku_contour

        if sudoku_contour is None:
            return None

        # Order points
        sudoku_contour = sudoku_contour.reshape(4, 2)
        corners = self._order_points(sudoku_contour)

        # Get width and height of contour
        w1 = np.sqrt(((corners[3][0] - corners[2][0]) ** 2) + ((corners[3][1] - corners[2][1]) ** 2))
        w2 = np.sqrt(((corners[1][0] - corners[0][0]) ** 2) + ((corners[1][1] - corners[0][1]) ** 2))
        width = max(int(w1), int(w2))

        h1 = np.sqrt(((corners[1][0] - corners[3][0]) ** 2) + ((corners[1][1] - corners[3][1]) ** 2))
        h2 = np.sqrt(((corners[0][0] - corners[2][0]) ** 2) + ((corners[0][1] - corners[2][1]) ** 2))
        height = max(int(h1), int(h2))

        size = max(width, height)
        run_mode = self.my_options.get_capture_mode()
        if run_mode == "offline":
            if not size // 9 > 10:
                return None
        elif run_mode == "online":
            if not size // 9 > 40:
                return None

        # Warp perspective on sudoku img
        dest = np.array([[0, 0], [size, 0], [0, size], [size, size]], dtype="float32")
        self.M = cv2.getPerspectiveTransform(corners, dest)
        self.sudoku_warped = cv2.warpPerspective(frame, self.M, (size, size))

        # Preprocess sudoku img
        sudoku_img = cv2.resize(self.sudoku_warped, (600, 600), interpolation=cv2.INTER_AREA)
        sudoku_img = cv2.cvtColor(sudoku_img, cv2.COLOR_BGR2GRAY)
        sudoku_img = cv2.GaussianBlur(sudoku_img, (11, 11), 0)
        sudoku_img = cv2.adaptiveThreshold(sudoku_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11,
                                           2)
        field_size = 600 // 9
        structure_arg_size = 600 // 18
        # Connect lines
        img_to_remove_lines = sudoku_img.copy()
        kernel_repair = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        img_to_remove_lines = cv2.morphologyEx(img_to_remove_lines, cv2.MORPH_CLOSE, kernel_repair, iterations=2)
        img_to_remove_lines = cv2.dilate(img_to_remove_lines, kernel_repair, iterations=2)
        # Remove horizontal lines
        kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (structure_arg_size, 1))
        horizontal_lines = cv2.morphologyEx(img_to_remove_lines, cv2.MORPH_OPEN, kernel_horizontal, iterations=2)
        sudoku_img = cv2.bitwise_and(sudoku_img, cv2.bitwise_not(horizontal_lines))
        # Remove vertical lines
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, structure_arg_size))
        vertical_lines = cv2.morphologyEx(img_to_remove_lines, cv2.MORPH_OPEN, kernel_vertical, iterations=2)
        sudoku_img = cv2.bitwise_and(sudoku_img, cv2.bitwise_not(vertical_lines))

        # Open and close morph operations
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        sudoku_img = cv2.morphologyEx(sudoku_img, cv2.MORPH_CLOSE, kernel_dilate, iterations=1)
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        sudoku_img = cv2.morphologyEx(sudoku_img, cv2.MORPH_OPEN, kernel_erode, iterations=1)

        sudoku_img = cv2.bitwise_not(sudoku_img)
        sudoku_img = cv2.GaussianBlur(sudoku_img, (5, 5), 0)

        # cv2.imshow("Sudoku", sudoku_img)
        # cv2.waitKey(5000)
        # cv2.destroyAllWindows()

        # Scan sudoku img to get sudoku matrix
        sudoku_arr = np.zeros((9, 9), dtype="int0")
        for i in range(9):
            for j in range(9):
                digit_img = sudoku_img[i * field_size:i * field_size + field_size,
                            j * field_size:j * field_size + field_size].copy()
                digit_img = self._prepare_digit_img(digit_img)
                digit_text = self.reader.readtext(digit_img, detail=0, allowlist='123456789')
                if digit_text:
                    digit = self._find_digit(digit_text[0])
                    sudoku_arr[i][j] = np.int0(digit)
        return sudoku_arr

    def print_result(self, frame, init_arr, res_arr):
        height, width = self.sudoku_warped.shape[:2]

        x_dt = width // 9
        y_dt = height // 9
        start_x = int(0.3 * x_dt)
        start_y = int(0.8 * y_dt)
        for i in range(9):
            for j in range(9):
                if init_arr[i, j] == 0:
                    cv2.putText(img=self.sudoku_warped, text="{}".format(res_arr[i, j]),
                                org=(start_x + j * x_dt, start_y + i * y_dt),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=0.6,
                                thickness=3,
                                color=(0, 0, 255))

        # Get back from warp perspective
        _, IM = cv2.invert(self.M)
        sudoku_returned = cv2.warpPerspective(self.sudoku_warped, IM, (frame.shape[1], frame.shape[0]))

        # Add result img to frame
        roi = frame[0:frame.shape[0], 0:frame.shape[1]]
        mask = cv2.cvtColor(sudoku_returned, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        sudoku_returned = cv2.bitwise_and(sudoku_returned, sudoku_returned, mask=mask)
        roi = cv2.bitwise_and(roi, roi, mask=mask_inv)

        res_img = cv2.add(roi, sudoku_returned)

        return res_img
