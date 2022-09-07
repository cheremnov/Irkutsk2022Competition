# Human action recognition, YOLOv5

This is a solution for the Employee action recognition competition. The solution is based on YOLOv5, which is a state-of-the-art object detection model. We use the bounding boxes of the detected objects to extract the human body. Then, we use the coords and several other features to train a simple classifier (Random Forest).

We also train a classifier on the images of the doors, to use the state of the door ("open" or "closed") as a feature.

## Directory structure

- `action` - extracted frames from the videos
- `doors`
-- `doors.csv` - the doors dataset
- `door_classifier.pkl` - the trained door classifier
- `models`
-- `resnet_employee_classifier_5_epochs.pt` - the trained classifier
- `ocr_error` - frames with OCR errors
- `augmented_train.csv` - the augmented train dataset (with bounding boxes coords, etc.)
- `augmented_test.csv` - the augmented test dataset (with bounding boxes coords, etc.)
- `label_data.py` - simple GUI tool to label doors
- `yolo_baseline.ipynb` - the solution notebook