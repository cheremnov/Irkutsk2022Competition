""" An easy-to-use, simple GUI for labeling data.

The tool can be used to label images for machine learning. 
The labels are automatically saved in a CSV file.

The labeler is a simple GUI, consisting of a window with a large image, a list of labels, and a
button for each label. Clicking on a label will set the label for the
current image. The images are loaded in a random order.

Images are prepared for the labeler by running the prepare_image() function,
which will resize the image to a fixed size and crop the location of interest.

The user can navigate through the images using the arrow keys.

Usage:
    label_data.py <path_to_images> <path_to_csv>

Example:
    label_data.py /home/user/images /home/user/labels.csv

"""
from importlib.resources import path
import os
import sys
import csv
import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk

# The size of the image to be displayed
IMAGE_CROP_AREA = (1020, 510, 1300, 1350)

def prepare_image(image):
    """ Prepare the image for the labeler.
    Crop the location of interest.
    Args:
        image (PIL.Image): The image to be prepared.
    Returns:
        PIL.Image: The prepared image.
    """
    image = image.crop(IMAGE_CROP_AREA)
    return image

class Labeler:
    def __init__(self, path_to_images, path_to_csv, labels=[], door_id=1):
        self.door_id = door_id
        self.path_to_images = path_to_images
        self.path_to_csv = path_to_csv
        self.image_files = []
        self.labels = labels
        self.current_image = None
        self.current_image_index = 0
        self.current_label = None
        self.current_label_index = 0
        self.root = tk.Tk()
        self.root.title('Labeler')
        self.root.geometry('800x600')
        key_bindings = {
            '<Left>': self.previous_image,
            '<Right>': self.next_image,
            '<Up>': self.previous_label,
            '<Down>': self.next_label,
            'q': self.quit,
            'n': self.next_image
        }
        # Also bind capital letters
        for key in list(key_bindings.keys()):
            if 'a' <= key[0] and key[0] <= 'z':
                key_bindings[key.upper()] = key_bindings[key]
        # Bind all key bindings
        for key, callback in key_bindings.items():
            self.root.bind(key, callback)
        self.load_image_files()
        self.load_csv()
        self.create_gui()
        self.load_labels()
        self.load_image()
        self.root.mainloop()

    def load_image_files(self):
        self.image_files = []
        for file in os.listdir(self.path_to_images):
            if file.endswith('.jpg') or file.endswith('.png'):
                self.image_files.append(file)
        random.shuffle(self.image_files)
    
    def load_csv(self):
        # Load dataframe with columns 'image', 'label', 'door_id'
        if os.path.exists(self.path_to_csv):
            self.doors_df = pd.read_csv(self.path_to_csv)
        else:
            self.doors_df = pd.DataFrame(columns=['image', 'label', 'door_id'])

    def load_image(self):
        # Close previous image if opened
        if self.current_image is not None:
            self.image_canvas.delete(self.current_image)

        self.current_image = self.image_files[self.current_image_index]
        self.image = Image.open(os.path.join(self.path_to_images, self.current_image))
        self.image = prepare_image(self.image)
        self.image = ImageTk.PhotoImage(self.image)
        self.image_canvas.create_image(0, 0, image=self.image, anchor=tk.NW)
        # Contract the canvas to the image size
        self.image_canvas.config(width=self.image.width(), height=self.image.height())
        # Remove the empty space between the image and the labels sidebar
        self.root.geometry('{}x{}'.format(self.image.width() + 200, self.image.height()))
    
    def save(self, event=None):
        if self.current_label is None:
            return
        # Check if the image is already in the dataframe
        if self.current_image in self.doors_df['image'].values:
            # Update the label
            self.doors_df.loc[self.doors_df['image'] == self.current_image, 'label'] = self.current_label
        else:
            # Add a new row
            self.doors_df = self.doors_df.append({'image': self.current_image, 'label': self.current_label, 'door_id': self.door_id}, ignore_index=True)
        
        self.doors_df.to_csv(self.path_to_csv, index=False)
    
    def previous_image(self, event=None):
        self.save()
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.image_files) - 1
        self.load_image()

    def next_image(self, event=None, no_save=False):
        if no_save is False:
            self.save()
        self.current_image_index += 1
        if self.current_image_index >= len(self.image_files):
            self.current_image_index = 0
        self.load_image()
    
    def skip_image(self, event=None):
        self.next_image(no_save=True)
        
    def previous_label(self, event=None):
        self.current_label_index -= 1
        if self.current_label_index < 0:
            self.current_label_index = len(self.labels) - 1
        self.label_list.selection_clear(0, tk.END)
        self.label_list.selection_set(self.current_label_index)
        self.label_list.activate(self.current_label_index)
        self.current_label = self.labels[self.current_label_index]

    def next_label(self, event=None):
        self.current_label_index += 1
        if self.current_label_index >= len(self.labels):
            self.current_label_index = 0
        self.label_list.selection_clear(0, tk.END)
        self.label_list.selection_set(self.current_label_index)
        self.label_list.activate(self.current_label_index)
        self.current_label = self.labels[self.current_label_index]

    def create_gui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Image canvas
        self.image_canvas = tk.Canvas(self.frame, height=IMAGE_CROP_AREA[2] - IMAGE_CROP_AREA[0],
                                      width=IMAGE_CROP_AREA[3] - IMAGE_CROP_AREA[1])
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Slim vertical sidebar, ultra-modern minimalistic design
        self.label_frame = tk.Frame(self.frame)
        self.label_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Label list
        self.label_list = tk.Listbox(self.label_frame, selectmode=tk.SINGLE)
        self.label_list.pack(fill=tk.BOTH, expand=True)
        self.label_list.bind('<<ListboxSelect>>', self.select_label)

        # Add buttons: previous, next, skip, quit
        self.button_frame = tk.Frame(self.label_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.previous_button = tk.Button(self.button_frame, text='Previous', command=self.previous_image)
        self.previous_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.next_button = tk.Button(self.button_frame, text='Next', command=self.next_image)
        self.next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.skip_button = tk.Button(self.button_frame, text='Skip', command=self.skip_image)
        self.skip_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.quit_button = tk.Button(self.button_frame, text='Quit', command=self.quit)
        self.quit_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def load_labels(self):
        self.label_list.delete(0, tk.END)
        for label in self.labels:
            self.label_list.insert(tk.END, label)

    def select_label(self, event):
        self.current_label_index = self.label_list.curselection()[0]
        self.current_label = self.labels[self.current_label_index]
    
    def quit(self, event=None):
        self.root.quit()
    
    # Destructor
    def __del__(self):
        self.quit()

DOOR_LABELS = ["open", "closed"]

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Read "path_to_images" and "path_to_csv" from command line arguments or use default values
    if len(sys.argv) > 2:
        path_to_images = sys.argv[1]
        path_to_csv = sys.argv[2]
    else:
        path_to_images = 'actions'
        path_to_csv = 'doors/doors.csv'
    
    # Create the GUI
    gui = Labeler(path_to_images, path_to_csv, DOOR_LABELS)

