import cv2
import os


def extract_info_to_imgs(img_path, output_path):
    original_image = cv2.imread(img_path)
    coords = [(380, 240, 390, 52), (280, 325, 450, 50), (570, 370, 200, 42),
              (470, 400, 90, 45), (810, 400, 150, 45), (280, 477, 600, 42)]
    os.makedirs(output_path, exist_ok=True)

    for i in range(0, len(coords)):
        x = coords[i][0]
        y = coords[i][1]
        width = coords[i][2]
        height = coords[i][3]

        # Create a unique output path for each ROI
        if i == 0:
            output_roi_path = f'{output_path}/1.id.png'
        elif i == 1:
            output_roi_path = f'{output_path}/2.name.png'
        elif i == 2:
            output_roi_path = f'{output_path}/3.dob.png'
        elif i == 3:
            output_roi_path = f'{output_path}/4.gender.png'
        elif i == 4:
            output_roi_path = f'{output_path}/5.nation.png'
        elif i == 5:
            output_roi_path = f'{output_path}/6.origin.png'

        # Extract and save the ROI
        roi = original_image[y:y + height, x:x + width]
        cv2.imwrite(output_roi_path, roi)
