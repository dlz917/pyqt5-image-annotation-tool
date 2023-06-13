import numpy as np
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget,QSizePolicy,QDialog,QFileDialog,QColorDialog,QInputDialog,QSlider,QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QFileInfo,QPoint,QRect,QSize
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPen, QPainter, QColor, QPainterPath
from matplotlib import cm
from skimage.draw import line    

class ImageWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.image_label = QLabel(self)
        self.opacity = 255
        
        if self.image_path.lower().endswith('.npy'):
            image_data = np.load(image_path)

            if len(image_data.shape) == 2:
                # Normalize the image to span the full colormap
                image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))
                image_data=add_border(image_data)
                # Get the colormap
                cmap = cm.get_cmap('gray')
                # Apply the colormap
                rgba_image = cmap(image_data)
                # Convert the data to 0-255 integers
                image_data = (rgba_image * 255).astype(np.uint8)

                height, width, _ = image_data.shape
                bytes_per_line = 4 * width  # for Format_RGBA8888, each pixel is 4 bytes
               
                qimage = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_RGBA8888)

            elif len(image_data.shape) == 3:
                if image_data.shape[2] == 3 or image_data.shape[2] == 4:
                    image_data = image_data[..., ::-1]  # reverse the color channels

                image_data = np.require(image_data, np.uint8, 'C')
                height, width, channels = image_data.shape
                bytes_per_line = channels * width
                qimage = QImage(image_data.data, width, height, bytes_per_line, QImage.Format_RGB888)

            else:
                raise ValueError(f"Unsupported number of dimensions: {len(image_data.shape)}")

            self.pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(self.pixmap)
        else:
            pixmap = QPixmap(image_path)

        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(512, 512, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

        self.canvas = CanvasWidget(self)
        self.canvas.hide()  # Hide initially

        self.button = QPushButton('Hide', self)
        self.button.clicked.connect(self.hide_and_open_tab)

        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.button)
        
        self.setLayout(self.layout)
        
        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 255)  # 0 = fully transparent, 255 = fully opaque
        self.opacity_slider.setValue(self.opacity)  # Start with fully opaque
        self.opacity_slider.valueChanged.connect(self.set_opacity)

        self.layout.addWidget(self.opacity_slider)

        # Add the quantile slider to the layout
        self.quantile_slider = QSlider(Qt.Horizontal, self)
        self.quantile_slider.setRange(0, 100)  # 0 = 0th percentile, 100 = 100th percentile
        self.quantile_slider.setValue(100)  # Start with the 100th percentile (full range)
        self.quantile_slider.valueChanged.connect(self.update_image_quantile)

        #Add the log transform checkbox to the layout
        self.log_checkbox = QCheckBox('Log Transform', self)
        self.log_checkbox.stateChanged.connect(self.toggle_log_transform)

        # Add the log transform checkbox to the layout
        self.layout.addWidget(self.log_checkbox)

        # Load the image data and store a copy for transformations
        self.original_image_data = np.load(self.image_path)
        self.transformed_image_data = np.copy(self.original_image_data)

                
    def set_opacity(self, value):
        self.opacity = value
        self.canvas.update()

    def showEvent(self, event):
        super().showEvent(event)
        # Adjust canvas size to image_label size
        self.canvas.setGeometry(self.image_label.geometry())
        self.canvas.update() 
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Scale pixmap to fit the label
        scaled_pixmap = self.pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        # Adjust canvas size to image_label size
        self.canvas.setGeometry(self.image_label.geometry())
        self.canvas.update() 

    def hide_and_open_tab(self):
        self.hide()
        self.canvas.hide()  # Also hide canvas
        image_name = QFileInfo(self.image_path).baseName()
        tab = QWidget()
        tab.setWindowTitle(image_name)
        main_window.addTab(tab, image_name)
        main_window.image_tabs[tab] = self
        main_window.update_hide_buttons()  # Update the visibility of hide buttons

    def show_image(self):
        self.show()
        
            
    def update_image_label_pixmap(self):
        scaled_pixmap = self.pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
   
    def update_image_quantile(self, value):
        # Convert the value from a 0-100 scale to a 0.0-1.0 scale
        quantile = value / 100.0
        if self.image_path.lower().endswith('.npy'):
            image_data = np.load(self.image_path)
            
            # Rescale the image data to the specified quantile
            min_value = np.percentile(image_data, 0)
            max_value = np.percentile(image_data, quantile*100)
            image_data = np.clip(image_data, min_value, max_value)
            
            # Normalize the image to span the full colormap
            image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))

            image_data=add_border(image_data)
            # Convert the image data to 8-bits and reshape it to 1D
            image_8bit = np.uint8(image_data * 255).reshape(-1)

            # Create QImage from the data
            height, width = image_data.shape
            qimage = QImage(image_8bit.data, width, height, QImage.Format_Grayscale8)

            # Set the new pixmap
            self.pixmap = QPixmap.fromImage(qimage)
            self.update_image_label_pixmap()

    def toggle_log_transform(self, state):
        if state == Qt.Checked:
            # Apply a log transform to the data, adding a small constant to avoid log(0)
            self.transformed_image_data = np.log(self.original_image_data + 1e-9)
        else:
            # If the checkbox is unchecked, use the original image data
            self.transformed_image_data = np.copy(self.original_image_data)

        self.update_image()

    def update_image(self):
        # Convert the value from a 0-100 scale to a 0.0-1.0 scale
        quantile = self.quantile_slider.value() / 100.0

        # Rescale the image data to the specified quantile
        image_data = self.transformed_image_data
        min_value = np.percentile(image_data, 0)
        max_value = np.percentile(image_data, quantile*100)
        image_data = np.clip(image_data, min_value, max_value)
        
        # Normalize the image to span the full colormap
        image_data = (image_data - np.min(image_data)) / (np.max(image_data) - np.min(image_data))
        image_data=add_border(image_data)
        # Convert the image data to a QImage
        image_data = np.uint8(image_data * 255)  # Convert to 8-bit unsigned integer
        qimage = QImage(image_data.data, image_data.shape[1], image_data.shape[0], image_data.strides[0], QImage.Format_Grayscale8)

        
        # Set the new pixmap
        self.pixmap = QPixmap.fromImage(qimage)
        self.update_image_label_pixmap()    
        
        
class MainWindow(QTabWidget):
    def __init__(self, sonar_image, bathy_image, tri_image, output_folder,file_prefix):        
        super().__init__()
        self.segments = []  # Store the segments in MainWindow so they can be saved later
        self.setWindowTitle('Image Display')

        self.image_widget1 = ImageWidget(sonar_image, self)
        self.image_widget2 = ImageWidget(bathy_image, self)
        self.image_widget3 = ImageWidget(tri_image, self)

        self.image_widget1.canvas.show()
        self.image_widget2.canvas.show()
        self.image_widget3.canvas.show()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(30)  # Add 30 px space between widgets
        self.layout.addWidget(self.image_widget1)
        self.layout.addWidget(self.image_widget2)
        self.layout.addWidget(self.image_widget3)

         # Set the size policy to Expanding so the images can take extra space
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_widget1.setSizePolicy(sizePolicy)
        self.image_widget2.setSizePolicy(sizePolicy)
        self.image_widget3.setSizePolicy(sizePolicy)

        # Set the stretch factor to a higher value so the images take more of the extra space
        self.layout.setStretchFactor(self.image_widget1, 1)
        self.layout.setStretchFactor(self.image_widget2, 1)
        self.layout.setStretchFactor(self.image_widget3, 1)

        self.container = QWidget()
        self.container.setLayout(self.layout)

        self.addTab(self.container, 'Images')
        self.image_tabs = {}
        self.currentChanged.connect(self.on_tab_click)
        
        self.pencil_button = QPushButton('Pencil', self.container)
        self.pencil_button.setCheckable(True)
        self.layout.addWidget(self.pencil_button, alignment=Qt.AlignTop | Qt.AlignLeft)

        self.pencil_color = '#000000'  # Default pencil color: black
        self.pencil_thickness = 1  # Default pencil thickness: 3 pixels

        self.pencil_button.toggled.connect(self.update_canvas_mouse_events)
        self.pencil_button.toggled.connect(self.update_canvas_visibility)

        self.save_button = QPushButton('Save', self.container)
        self.layout.addWidget(self.save_button, alignment=Qt.AlignTop | Qt.AlignRight)
        self.save_button.clicked.connect(self.save)

        self.output_folder = output_folder 
        self.file_prefix = file_prefix  
        self.load()  # Load existing annotations

        

    def update_canvas_visibility(self, checked):
        visible_widgets = [widget for widget in [self.image_widget1, self.image_widget2, self.image_widget3] if widget.isVisible()]
        for widget in visible_widgets:
            if checked:
                widget.canvas.show()
            else:
                widget.canvas.hide()

        if len(visible_widgets) == 1:  # if only one image is visible
            widget = visible_widgets[0]
            # make the widget to take up all available space
            widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            # center the widget
            self.layout.setAlignment(widget, Qt.AlignCenter)
            # set the stretch factor to a higher value so the images take more of the extra space
            self.layout.setStretchFactor(widget, 2)
        else:
            for widget in visible_widgets:
                # set the size policy to Expanding so the images can take extra space
                widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
                # set the stretch factor to a higher value so the images take more of the extra space
                self.layout.setStretchFactor(widget, 1)
                self.layout.setAlignment(Qt.AlignLeft)


    def on_tab_click(self, index):
        current_tab = self.widget(index)
        if current_tab in self.image_tabs:
            self.image_tabs[current_tab].show_image()
            self.setCurrentWidget(self.container)
            self.removeTab(index)
            self.update_hide_buttons()  # Update the visibility of hide buttons

    def update_hide_buttons(self):
        visible_widgets = [widget for widget in [self.image_widget1, self.image_widget2, self.image_widget3] if widget.isVisible()]
        if len(visible_widgets) > 2:
            for widget in visible_widgets:
                widget.button.show()
        else:
            for widget in visible_widgets:
                widget.button.hide()

    def update_canvas_mouse_events(self, checked):
        if checked:
            self.colormap={'Posidonie': QColor('#0b9224'), 'Enrochement': QColor('#969d97'), 'Matte': QColor('#d55e09'), 'Anthropique': QColor('#0c03d2'), 'Cymodecee': QColor('#20e4db'), 'Sediment' : QColor('#fef22f'), 'Roche' : QColor('#751f1c'), 'BlocGaletGravier' : QColor('#524e44'), 'SedimentRide' : QColor('#a28446')} 

            # Assuming colormap is a dictionary with keys as names and values as QColor objects
            color_name = QInputDialog.getItem(self, 'Select Pencil Color', 'Choose a color:', list(self.colormap.keys()))
            if color_name[1]:  # If user pressed OK
                self.pencil_color = self.colormap[color_name[0]].name()
        
        self.image_widget1.canvas.set_segments(self.segments.copy())  # update() will be called inside set_segments()
        self.image_widget2.canvas.set_segments(self.segments.copy())
        self.image_widget3.canvas.set_segments(self.segments.copy())

    def update(self):
        # Clear the image
        self.image.fill(Qt.white)
        painter = QPainter(self.image)
        
        # Redraw all segments
        for color, thickness, points in self.segments:
            painter.setPen(QPen(QColor(color), thickness))
            for i in range(1, len(points)):
                painter.drawLine(QPoint(*points[i - 1]), QPoint(*points[i]))

        # Force a repaint event
        self.repaint()

    def load(self):
        # Get the base name (file name with extension) from one of the selected image paths
        annot_file_path= os.path.join(self.output_folder, self.file_prefix + '_annot.json')        # Get the base name without extension
        print(annot_file_path)

        if os.path.exists(annot_file_path):
            with open(annot_file_path, 'r') as f:
                segments_data = json.load(f)
            
            segments = [
                (
                    data['color'], 
                    data['thickness'], 
                    [(float(x[0]), float(x[1])) for x in data['points']]  # Convert list back to tuple
                ) 
                for data in segments_data
            ]
            
            self.segments = segments
            
            # Apply the loaded annotations to all image widgets
            for image_widget in [self.image_widget1, self.image_widget2, self.image_widget3]:
                image_widget.segments = segments  # Update the segments for this image widget
                image_widget.update()  # Redraw the widget


    def save(self):
        color_map = {
            '#0b9224': 1, 
            '#969d97': 2, 
            '#d55e09': 3, 
            '#0c03d2': 4,
            '#20e4db': 5, 
            '#fef22f': 6, 
            '#751f1c': 7, 
            '#524e44': 8,
            '#a28446': 9
        }

        # Interesting rows and columns
        interesting_rows = np.array([ 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395,
        414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431,
        432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449,
        450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467,
        468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479])

        interesting_cols = np.array([ 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230,
        249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266,
        267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284,
        285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302,
        303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314])

        # Create an empty matrix
        image_matrix = np.zeros((self.image_widget1.pixmap.height(), self.image_widget1.pixmap.width()))

        # Convert segments to matrix
        for color, _, points in self.segments:
            # Convert color from #RRGGBB to QColor and then to integer value in color_map
            color_value = color_map[QColor(color).name()]
            for i in range(1, len(points)):
                point1 = points[i - 1]
                point2 = points[i]

                # Convert the points from relative to absolute coordinates
                x1_abs, y1_abs = self.image_widget1.canvas._image_relative_to_widget_absolute(point1)
                x2_abs, y2_abs = self.image_widget1.canvas._image_relative_to_widget_absolute(point2)

                # Add the segment to the image matrix
                x1, x2 = map(int, [x1_abs, x2_abs])
                y1, y2 = map(int, [y1_abs, y2_abs])
                rr, cc = line(y1, x1, y2, x2)  # Using Bresenham's line algorithm from skimage library

                # Check that the coordinates are within the valid range
                valid_indices = (0 <= rr) & (rr < image_matrix.shape[0]) & (0 <= cc) & (cc < image_matrix.shape[1])
                rr = rr[valid_indices]
                cc = cc[valid_indices]

                image_matrix[rr, cc] = color_value

        # Crop to interesting rows and columns
        image_matrix = image_matrix[np.min(interesting_rows):np.max(interesting_rows)+1, np.min(interesting_cols):np.max(interesting_cols)+1]

        output_path = os.path.join(self.output_folder, self.file_prefix + '_output.npy')
        np.save(output_path, image_matrix)
        

        file_path = os.path.join(self.output_folder, self.file_prefix  + '_annot.json')

        segments_data = [{
            'color': segment[0],
            'thickness': segment[1],
            'points': [[float(x) for x in point] for point in segment[2]]  
        } for segment in self.segments]

        with open(file_path, 'w') as f:
            json.dump(segments_data, f)

        
        print('Saved to', output_path)

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.points = []  # This will now store tuples of (relative x, relative y)
        self.segments = []  # List of segments, where each segment is a tuple: (color, thickness, list of points)
        self.drawing_area_fraction = 0.1943125  # The fraction of the image that will be used as the drawing area
        #Put a border around the canvas
        self.raise_()
        self.setStyleSheet("border: 10px solid white;")
        self.show()

    def set_points(self, points):
        self.points = points
        self.update()

    def set_segments(self, segments):
        self.segments = segments
        self.update()

    def mousePressEvent(self, event):
        if main_window.pencil_button.isChecked() and self._is_in_drawing_area(event.pos()):
            self.drawing = True
            x_rel, y_rel = self._event_pos_to_image_relative(event.pos())
            main_window.segments.append((main_window.pencil_color, main_window.pencil_thickness, [(x_rel, y_rel)]))
            # Also set segments for the other canvases
            for image_widget in [main_window.image_widget1, main_window.image_widget2, main_window.image_widget3]:
                if image_widget.canvas is not self:
                    image_widget.canvas.set_segments(main_window.segments.copy())  # copy() to prevent aliasing

    def mouseMoveEvent(self, event):
        if self.drawing and main_window.pencil_button.isChecked() and self._is_in_drawing_area(event.pos()):
            x_rel, y_rel = self._event_pos_to_image_relative(event.pos())
            main_window.segments[-1][2].append((x_rel, y_rel))
            # Also set segments for the other canvases
            for image_widget in [main_window.image_widget1, main_window.image_widget2, main_window.image_widget3]:
                if image_widget.canvas is not self:
                    image_widget.canvas.set_segments(main_window.segments.copy())  # copy() to prevent aliasing
            self.update()
            
    def _is_in_drawing_area(self, pos):
        pixmap = self.parent().pixmap
        image_label = self.parent().image_label

        # Calculate scale factor between pixmap and label
        scale_factor = min(image_label.width() / pixmap.width(), image_label.height() / pixmap.height())

        # Calculate the size and position of the drawing area
        drawing_area_size = scale_factor * pixmap.width() * self.drawing_area_fraction
        drawing_area_x = (image_label.width() - drawing_area_size) / 2
        drawing_area_y = (image_label.height() - drawing_area_size) / 2

        # Check if the position is within the drawing area
        return (drawing_area_x <= pos.x() <= drawing_area_x + drawing_area_size) and (drawing_area_y <= pos.y() <= drawing_area_y + drawing_area_size)
    
    def _event_pos_to_image_relative(self, pos):
        pixmap = self.parent().pixmap
        image_label = self.parent().image_label

        # Calculate scale factor between pixmap and label
        scale_factor = min(image_label.width() / pixmap.width(), image_label.height() / pixmap.height())

        # Calculate the empty space due to aspect ratio preservation
        empty_space_x = (image_label.width() - scale_factor * pixmap.width()) / 2
        empty_space_y = (image_label.height() - scale_factor * pixmap.height()) / 2

        # Adjust the position to take into account the empty space
        pos_adjusted_x = pos.x() - empty_space_x
        pos_adjusted_y = pos.y() - empty_space_y

        # Convert to relative position
        x_rel = pos_adjusted_x / (scale_factor * pixmap.width())
        y_rel = pos_adjusted_y / (scale_factor * pixmap.height())

        return x_rel, y_rel

    def paintEvent(self, event):
        painter = QPainter(self)
        for color, thickness, points in main_window.segments:  # Use the segments stored in MainWindow
            # Convert color from #RRGGBB format to QColor
            color = QColor(color)
            # Set opacity
            color.setAlpha(self.parent().opacity)  # Get opacity from parent widget
            # Set pen with modified color
            painter.setPen(QPen(color, thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            if points: # Check if the list is not empty
                path = QPainterPath()
                # Start the path at the first point
                x_abs_start, y_abs_start = self._image_relative_to_widget_absolute(points[0])
                path.moveTo(x_abs_start, y_abs_start)

                # Continue the path through the rest of the points
                for point_rel in points[1:]:
                    x_abs, y_abs = self._image_relative_to_widget_absolute(point_rel)
                    path.lineTo(x_abs, y_abs)

                # Draw the path
                painter.drawPath(path)

    def _image_relative_to_widget_absolute(self, point_rel):
        pixmap = self.parent().pixmap
        image_label = self.parent().image_label

        # Calculate scale factor between pixmap and label
        scale_factor = min(image_label.width() / pixmap.width(), image_label.height() / pixmap.height())

        # Calculate the empty space due to aspect ratio preservation
        empty_space_x = (image_label.width() - scale_factor * pixmap.width()) / 2
        empty_space_y = (image_label.height() - scale_factor * pixmap.height()) / 2

        # Convert to absolute position
        x_abs = point_rel[0] * scale_factor * pixmap.width() + empty_space_x
        y_abs = point_rel[1] * scale_factor * pixmap.height() + empty_space_y

        return x_abs, y_abs
    
class FolderSelectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Folders')
        self.folder1 = None
        self.folder2 = None
        self.resize(800, 600)  # Set initial size

        self.button1 = QPushButton('Select Files', self)
        self.button1.clicked.connect(self.select_folder1)

        self.button2 = QPushButton('Select Output Folder', self)
        self.button2.clicked.connect(self.select_folder2)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.button1)
        self.button_layout.addWidget(self.button2)

        self.proceed_button = QPushButton('Proceed', self)
        self.proceed_button.clicked.connect(self.proceed)
        self.proceed_button.setEnabled(False)

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.proceed_button, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def select_folder1(self):
        self.folder1 = QFileDialog.getOpenFileName(self, 'Select Files')
        self.check_folders_selected()

    def select_folder2(self):
        self.folder2 = QFileDialog.getExistingDirectory(self, 'Select Folder for the ouptut')
        self.check_folders_selected()

    def check_folders_selected(self):
        if self.folder1 and self.folder2:
            self.proceed_button.setEnabled(True)

    def proceed(self):

        def sort_files(file):
            if 'sonar' in file:
                return 0
            elif 'bathy' in file:
                return 1
            elif 'tri' in file:
                return 2
        
        # get the base name (file name with extension) from the selected file path
        selected_file_basename = os.path.basename(self.folder1[0]) 
        # get the base name without extension
        selected_file_base = os.path.splitext(selected_file_basename)[0]  
        # get the prefix of the selected file (before the last underscore)
        selected_file_prefix = "_".join(selected_file_base.split("_")[:-1])  

        # get the directory of the selected file
        selected_file_dir = os.path.dirname(self.folder1[0])  
        # get all files in the directory
        all_files = os.listdir(selected_file_dir)  

        # filter files with the same prefix and different suffix ('bathy', 'sonar', 'tri')
        corresponding_files = [f for f in all_files if f.startswith(selected_file_prefix) and f.endswith(('.tif', '.npy'))]

        # sort the files
        corresponding_files.sort(key=sort_files)

        # now corresponding_files[0] is 'bathy', corresponding_files[1] is 'sonar', and corresponding_files[2] is 'tri'

        self.sonar_image = os.path.join(selected_file_dir, corresponding_files[0])
        self.bathy_image = os.path.join(selected_file_dir, corresponding_files[1])
        self.tri_image = os.path.join(selected_file_dir, corresponding_files[2])
        

        self.close()
        global main_window
        main_window = MainWindow(self.sonar_image, self.bathy_image, self.tri_image, self.folder2,selected_file_prefix)
        main_window.show()
        main_window.load()  # Load existing annotations
    
def add_border(image, border_size=100):
    # Create a border mask of ones with the same size as the image
    border_mask = np.ones(image.shape, dtype=image.dtype)

    # Calculate the coordinates for the border
    start_y, start_x = (image.shape[0] - border_size) // 2, (image.shape[1] - border_size) // 2
    end_y, end_x = start_y + border_size, start_x + border_size

    # Set the border pixels in the mask to min or max depending on the mean
    if np.mean(image) < 0.5:
        border_mask[start_y:end_y, start_x] = 255  # Left border
        border_mask[start_y:end_y, end_x] = 255  # Right border
        border_mask[start_y, start_x:end_x] = 255  # Top border
        border_mask[end_y, start_x:end_x] = 255  # Bottom border
    else:
        border_mask[start_y:end_y, start_x] = 0  # Left border
        border_mask[start_y:end_y, end_x] = 0  # Right border
        border_mask[start_y, start_x:end_x] = 0  # Top border
        border_mask[end_y, start_x:end_x] = 0  # Bottom border

    # Multiply the image with the border mask to apply the border
    bordered_image = image * border_mask

    return bordered_image
    
def main():
    global main_window
    app = QApplication(sys.argv)

    folder_selection_window = FolderSelectionWindow()
    folder_selection_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()