

# ENG 
# Graphical Interface for Image Annotation 
Project completed in 2 months as an end-of-degree internship 
## IMPORTANT TO READ

Before you start using this graphical interface, there are several important points to note:

1. **Saving Annotations:** It is recommended to wait for some time after completing the annotations before closing the graphical interface. This allows for all modifications to be correctly saved.
2. **Loading Images:** The images to load must have the same prefix (EX:image1) and have suffixes sonar, bathy, and tri.
3. **Annotation Format:** The annotations are saved in two different formats. The first one is the `.npy` format, which is a NumPy array format. The second is the `.json` format, which is a data format easily readable by machines and humans. The `.json` format is used to facilitate the loading of annotations into the graphical interface.

## Project Presentation

This project involves creating a Graphical User Interface (GUI) using PyQt5 to display and manipulate images. The aim of the application is to enable users to open, interact with, and annotate images using a user-friendly interface.

- json
- PyQt5.QtWidgets (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QSizePolicy, QDialog, QFileDialog, QColorDialog, QInputDialog, QSlider, QCheckBox)
- PyQt5.QtGui (QPixmap, QImage, QPen, QPainter, QColor, QPainterPath)
- PyQt5.QtCore (Qt, QFileInfo, QPoint, QRect, QSize)
- matplotlib.cm
- skimage.draw (line)

## Key Features

- **Folder Selection:** The application's main interface starts with an interface to select the input folder containing images and the output folder that will contain the annotations once completed.
- **Image Display:** Images are displayed using an instance of the ImageWidget class, which inherits from QWidget. Images can be loaded from .npy files (NumPy array files).
- **Image Modification:** Users can draw on the images using a "pencil function". When the pencil function is enabled, mouse events are intercepted and used to draw lines on the image.
- **Control Buttons:** There are several buttons to control the behavior of the application. These buttons include options to hide images, enable or disable the pencil function, and move to a new image.
- **Tabs:** Images can be hidden in new tabs. The user can switch between images and select 2 or 3 images from a total of 3.
- **Synchronization of Drawings:** The drawing is synchronized across all images to ensure annotation consistency.
- **Customization Options:** The user can customize the interface, including the color and thickness of the pencil, and the shape of the "Painter".
- **Modification of the canvas area:** The canvas area is fixed at a size of 100x100 pixels and is centered on the image.
- **Normalization of images:** The user has the option to normalize the images using different buttons.
- **Opacity slider:** An opacity slider is available for each image, which allows adjusting the transparency of the drawing on the image.
- **Folder and file management:** The interface handles loading of images and saving of annotations. If an image has already been annotated, the interface can load these annotations.


# FR 
# Interface Graphique pour l'Annotation d'Images
Projet réalisé en 2 mois comme stage de fin de licence
## IMPORTANT À LIRE

Avant de commencer à utiliser cette interface graphique, il y a plusieurs points importants à noter :

1. **Sauvegarde des Annotations :** Il est recommandé d'attendre un certain temps après avoir terminé les annotations avant de fermer l'interface graphique. Cela permet d'assurer que toutes les modifications sont correctement sauvegardées.
2. **Chargement d'Images :** Les images a charger doivent avoir le meme prefix (EX:image1) et avoir comm sufix sonar, bathy et tri.
3. **Format des Annotations :** Les annotations sont sauvegardées sous deux formats différents. Le premier est le format `.npy`, qui est un format de tableau NumPy. Le second est le format `.json`, qui est un format de données facilement lisible par les machines et les humains. Le format `.json` est utilisé pour faciliter le chargement des annotations dans l'interface graphique.

## Présentation du Projet

Ce projet implique la création d'une interface utilisateur graphique (GUI) utilisant PyQt5 pour afficher et manipuler des images. L'objectif de l'application est de permettre aux utilisateurs d'ouvrir, d'interagir et d'annoter des images à l'aide d'une interface conviviale.



- json
- PyQt5.QtWidgets (QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QSizePolicy, QDialog, QFileDialog, QColorDialog, QInputDialog, QSlider, QCheckBox)
- PyQt5.QtGui (QPixmap, QImage, QPen, QPainter, QColor, QPainterPath)
- PyQt5.QtCore (Qt, QFileInfo, QPoint, QRect, QSize)
- matplotlib.cm
- skimage.draw (line)

## Fonctionnalités Principales

- **Sélection de dossier :** L'interface principale de l'application démarre avec une interface pour sélectionner le dossier d'entrée contenant les images et le dossier de sortie qui contiendra les annotations une fois réalisées.

- **Affichage d'images :** Les images sont affichées à l'aide d'une instance de la classe ImageWidget, qui hérite de QWidget. Les images peuvent être chargées à partir de fichiers .npy (fichiers de tableau NumPy).

- **Modification d'images :** Les utilisateurs peuvent dessiner sur les images à l'aide d'une "fonction crayon". Lorsque la fonction crayon est activée, les événements de la souris sont interceptés et utilisés pour dessiner des lignes sur l'image.

- **Boutons de contrôle :** Il existe plusieurs boutons pour contrôler le comportement de l'application. Ces boutons incluent des options pour cacher des images, activer ou désactiver la fonction crayon, et passer à une nouvelle image.

- **Onglets :** Les images peuvent être cachées dans de nouveaux onglets. L'utilisateur peut basculer entre les images et sélectionner 2 ou 3 images à partir d'un total de 3.

- **Synchronisation des dessins :** Le dessin est synchronisé entre toutes les images pour assurer la cohérence de l'annotation.

- **Options de personnalisation :** L'utilisateur peut personnaliser l'interface, y compris la couleur et l'épaisseur du crayon, et la forme du "Painter".

- **Modification de la zone du canvas :** La zone du canvas est fixée à une taille de 100x100 pixels et est centrée sur l'image.

- **Normalisation des images :** L'utilisateur a la possibilité de normaliser les images à l'aide de différents boutons.

- **Curseur d'opacité :** Un curseur d'opacité est disponible pour chaque image, ce qui permet de régler la transparence du dessin sur l'image.

- **Gestion des dossiers et des fichiers :** L'interface gère le chargement des images et la sauvegarde des annotations. Si une image a déjà été annotée, l'interface peut charger ces annotations.
