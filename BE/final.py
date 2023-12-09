import os
import shutil
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from removebg import RemoveBg
from change_img_perspective import wrap_perspective
from extract_info import extract_info_to_imgs
import unicodedata
import csv
from rembg import remove

def load_image(input_path, scale_factor=6):
    image = Image.open(input_path).convert('L')

    scale_factor = 6

    image = image.resize((image.width * scale_factor, image.height * scale_factor), Image.LANCZOS)

    return image


def preprocess_image(image, threshold=128):
    image_array = list(image.getdata())

    image_array = [image_array[offset:offset + image.width] for offset in
                   range(0, image.width * image.height, image.width)]

    binary_image = [[0 if pixel < threshold else 255 for pixel in row] for row in image_array]

    return binary_image


def merge_overlapping_boxes(boxes):
    sorted_boxes = sorted(boxes, key=lambda x: x[0])

    merged_boxes = []

    current_box = sorted_boxes[0]

    for box in sorted_boxes[1:]:
        # Check if box is completely inside current_box
        if (current_box[0] <= box[0]
                and current_box[1] <= box[1]
                and current_box[2] >= box[2]
                and current_box[3] >= box[3]):

            # Box is completely inside, update the current_box to encompass both
            current_box = (
                min(current_box[0], box[0]),
                min(current_box[1], box[1]),
                max(current_box[2], box[2]),
                max(current_box[3], box[3])
            )
        else:
            # No complete containment, add the current merged box to the result
            merged_boxes.append(current_box)
            current_box = box

    # Add the last merged box
    merged_boxes.append(current_box)

    return merged_boxes


# def remove_background_for_folder(folder_path):
#     # Initialize RemoveBg with your API key
#     rmbg = RemoveBg("he1V59AqpPt6ypJXqSW1FXRi", "error.log")
#
#     files = os.listdir(folder_path)
#
#     for file in files:
#         if file.lower().endswith('.png'):
#             img_file_path = os.path.join(folder_path, file)
#             # rmbg.remove_background_from_img_file(img_file_path=img_file_path, bg_color="black")
#             rmbg.remove_background_from_img_file(img_file_path=img_file_path)
#     move_no_bg(folder_path)
#
#
# def move_no_bg(folder_path):
#     files = os.listdir(folder_path)
#     os.makedirs(f'{folder_path}/no_bg', exist_ok=True)
#     for file in files:
#         if file.endswith("_no_bg.png"):
#             shutil.move(f"{folder_path}/{file}", f"{folder_path}/no_bg/{file}")
def remove_background_for_folder(folder_path):
    os.makedirs(f'{folder_path}/no_bg', exist_ok=True)
    files = os.listdir(folder_path)
    for file in files:
        if file.lower().endswith('.png'):
            img_file_path = os.path.join(folder_path, file)
            output_file_path = os.path.join(f"{folder_path}/no_bg", f"{os.path.basename(img_file_path)}_no_bg.png")
            img = Image.open(img_file_path)
            img_no_bg = remove(img)
            img_no_bg.save(output_file_path)

def preprocess_cards(input_path):
    no_bg_path = os.path.join(input_path, 'no_bg')
    wrapped_path = os.path.join(input_path, 'warped')

    os.makedirs(wrapped_path, exist_ok=True)

    for file in os.listdir(no_bg_path):
        img_file_path = os.path.join(no_bg_path, file)
        wrap_perspective(img_file_path, wrapped_path)




def find_character_boxes(image_array, width, height):
    contours = []
    for y in range(height):
        for x in range(width):
            if image_array[y][x] == 0:  # Black pixel
                x0, x1, y0, y1 = x, x, y, y
                stack = [(x, y)]

                while stack:
                    px, py = stack.pop()
                    if px >= 0 and px < width and py >= 0 and py < height and image_array[py][px] == 0:
                        image_array[py][px] = 255
                        x0, x1 = min(x0, px), max(x1, px)
                        y0, y1 = min(y0, py), max(y1, py)
                        stack.extend(((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)))

                if x1 - x0 > 10 and y1 - y0 > 10:  # Eliminate small area
                    contours.append((x0, 0, x1, height))
    res = merge_overlapping_boxes(contours)
    return res


def find_spaces(binary_image, new_width, new_height):
    character_spaces = []
    boxes = []
    for x in range(new_width):
        is_space = True
        for y in range(new_height):
            if binary_image[y][x] == 0:  # Black pixel
                is_space = False
                break
        if is_space:
            character_spaces.append(x)
        else:
            if character_spaces:
                start_x = character_spaces[0]
                end_x = character_spaces[-1]
                boxes.append((start_x, 0, end_x, new_height))
            character_spaces = []
    return boxes


def classify_spaces(spaces, multiplier=1.15):
    # Calculate the space widths and compute the mean and standard deviation
    space_widths = [x1 - x0 for x0, _, x1, _ in spaces[1:-1:1]]
    mean_width = np.mean(space_widths)
    std_deviation = np.std(space_widths)

    # Set the threshold as a multiple of the standard deviation away from the mean
    threshold = mean_width + multiplier * std_deviation  # You can adjust the multiplier as needed

    # space between characters in same word
    type_1_spaces = []

    # space between words
    type_2_spaces = []

    for contour in spaces:
        x0, y0, x1, y1 = contour
        space_width = x1 - x0

        if space_width <= threshold:
            type_1_spaces.append(contour)
        else:
            type_2_spaces.append(contour)

    spaces_between_words = type_2_spaces[1::]
    return spaces_between_words


def preprocess_and_crop(image, output_path):
    # Apply Gaussian blur to reduce noise
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=2))

    # Enhance brightness
    enhancer = ImageEnhance.Brightness(blurred_image)

    brightened_image = enhancer.enhance(1.5)  # Can adjust the enhancement factor

    # Find the bounding box of characters
    bbox = find_character_bbox(brightened_image)

    # Crop the image to the bounding box
    cropped_image = brightened_image.crop(bbox)

    # Save the preprocessed and cropped image
    cropped_image.save(output_path)


def find_character_bbox(image, threshold=200):
    # Convert the image to grayscale
    grayscale_image = image.convert('L')

    binary_image = grayscale_image.point(lambda p: p < threshold and 255)

    # Get the bounding box of non-white pixels
    bbox = binary_image.getbbox()

    return bbox


def box_to_images(image, combined_boxes, output_path):
    # Lưu từng ký tự và khoảng trắng thành ảnh riêng biệt theo thứ tự
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    for i, (x0, y0, x1, y1) in enumerate(combined_boxes):
        char_image = image.crop((x0, y0, x1, y1))  # Tạo ảnh con chứa ký tự hoặc khoảng trắng
        preprocess_and_crop(char_image, f'{output_path}/ky_tu_{i}.png')


def char_and_space_boxes(image, binary_image, multiplier=1.15):
    space_boxes = find_spaces(binary_image, image.width, image.height)
    spaces_between_word_boxes = classify_spaces(space_boxes, multiplier)

    # Gộp và sắp xếp lại thành một danh sách duy nhất
    combined_boxes = sorted(find_character_boxes(binary_image, image.width, image.height) + spaces_between_word_boxes,
                            key=lambda box: box[0])

    # draw = ImageDraw.Draw(image)
    # for box in combined_boxes:
    #     draw.rectangle(box, outline='green')
    # image.show()

    return combined_boxes


def clear_folder_contents(folder_path):
    # Iterate over the files and subdirectories in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            # If it's a file, remove it
            os.remove(item_path)

def resize_to_match(img1, img2):
    width1, height1 = img1.size
    width2, height2 = img2.size

    # Resize the bigger image to match the dimensions of the smaller image
    if width1 * height1 > width2 * height2:
        img1 = img1.resize((width2, height2))
    else:
        img2 = img2.resize((width1, height1))

    return img1, img2

def compare_matrices(image1, image2):
    # Ensure both images have the same dimensions
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions.")

    # Constants for SSIM calculation
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    # Compute mean of images
    mu1 = np.mean(image1)
    mu2 = np.mean(image2)

    # Compute variance of images
    sigma1_sq = np.var(image1)
    sigma2_sq = np.var(image2)

    # Compute covariance
    sigma12 = np.cov(image1.flatten(), image2.flatten())[0, 1]

    # SSIM calculation
    numerator = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
    denominator = (mu1 * 2 + mu2 * 2 + C1) * (sigma1_sq + sigma2_sq + C2)

    ssim_index = numerator / denominator

    return 1 - ssim_index  # Convert SSIM to a distance measure


def extract_char_number(file_name):
    return int(file_name.split("_")[2].split(".")[0])


def extract_line_number(file_name):
    return int(file_name.split(".")[0])

def get_name(name):
    if len(name) <= 2:
        return name[0]
    elif len(name) > 2:
        if name == 'slash':
            return ''
        if name == 'dot':
            return '.'
        if name == 'comma':
            return ','


# def resize_all(input_path):
#     files = os.listdir(input_path)
#     for file in files:
#         original_path = f"{input_path}/{file}"
#         no_bg_path = f"{input_path}/no_bg/{file}_no_bg.png"
#
#         if os.path.exists(original_path) and os.path.exists(no_bg_path):
#             image_original = Image.open(original_path)
#             image_no_bg = Image.open(no_bg_path)
#             image_1 = image_no_bg.resize((image_original.width, image_original.height))
#             image_1.save(no_bg_path)



def big_process():

    #Check if exist images/img_x.png before test this file

    start = time.time()
    remove_background_for_folder("images")
    # resize_all("images")
    preprocess_cards("images")
    page_path = "images/warped"
    line_path = "info"
    char_path = "chars"

    csv_file_path = "output.csv"
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        for page in os.listdir(page_path):
            id_card_data = {
                'id': '',
                'name': '',
                'dob': '',
                'gender': '',
                'nation': '',
                'region': ''
            }
            page_img_path = f"{page_path}/{page}"
            extract_info_to_imgs(page_img_path, line_path)

            line_files = sorted(os.listdir(line_path), key=extract_line_number)

            for line in line_files:
                print(line)

                if line == "4.gender.png":
                    line_img_path = f"{line_path}/{line}"
                    line_image = load_image(line_img_path)
                    line_binary_image = preprocess_image(line_image, threshold)
                    boxes = char_and_space_boxes(line_image, line_binary_image)
                    if len(boxes) == 3:
                        id_card_data['gender'] = "Nam"
                    else:
                        id_card_data['gender'] = "Nữ"
                    continue

                elif line == "5.nation.png":
                    line_img_path = f"{line_path}/{line}"
                    line_image = load_image(line_img_path)
                    line_binary_image = preprocess_image(line_image, threshold)
                    boxes = char_and_space_boxes(line_image, line_binary_image)
                    if len(boxes) == 8:
                        id_card_data['nation'] = "Việt Nam"
                    else:
                        id_card_data['nation'] = "Ngoại quốc"
                    continue

                elif line == "1.id.png" or line == "3.dob.png":
                    data_path = "data/roboto_char_img/num"
                    threshold = 95
                    multiplier = 2
                    line_img_path = f"{line_path}/{line}"
                    print(line_img_path)
                    line_image = load_image(line_img_path)
                    line_binary_image = preprocess_image(line_image, threshold)
                    boxes = char_and_space_boxes(line_image, line_binary_image, multiplier)
                    box_to_images(line_image, boxes, char_path)

                elif line == "6.origin.png":
                    data_path = "data/roboto_char_img/text_all"
                    line_img_path = f"{line_path}/{line}"
                    line_image = load_image(line_img_path)
                    line_binary_image = preprocess_image(line_image)
                    boxes = char_and_space_boxes(line_image, line_binary_image)
                    box_to_images(line_image, boxes, char_path)

                elif line == "2.name.png":
                    data_path = "data/roboto_char_img/text_uppercase"
                    line_img_path = f"{line_path}/{line}"
                    line_image = load_image(line_img_path)
                    line_binary_image = preprocess_image(line_image)
                    boxes = char_and_space_boxes(line_image, line_binary_image)
                    box_to_images(line_image, boxes, char_path)

                char_files = sorted(os.listdir(char_path), key=extract_char_number)
                ssim_values = {}
                line_data = []

                for char_to_check in char_files:
                    char_img_path = f"{char_path}/{char_to_check}"
                    char_img = Image.open(char_img_path).convert('L')
                    char_img_arr = np.array(char_img.getdata())
                    if np.mean(char_img_arr) > 240:
                        line_data.append(" ")
                        continue

                    for char_data in os.listdir(data_path):

                        if char_data.endswith('.png'):
                            data_image_path = os.path.join(data_path, char_data)
                            data_img = Image.open(data_image_path).convert('L')

                            char_img, data_img = resize_to_match(char_img, data_img)

                            char_img_arr = np.array(char_img.getdata())
                            data_img_arr = np.array(data_img.getdata())

                            ssim = compare_matrices(char_img_arr, data_img_arr)

                            image_name = os.path.splitext(char_data)[0]

                            ssim_values[image_name] = ssim

                        # Find the character with the highest correlation for the current line
                    if ssim_values:
                        best_match_name = min(ssim_values, key=ssim_values.get)
                        best_match_name = unicodedata.normalize("NFC", best_match_name)
                        # print(best_match_name)
                        name_to_write = get_name(best_match_name)
                        line_data.append(name_to_write)
                    ssim_values.clear()

                line_string = ''.join(line_data)
                if line == "3.dob.png":
                    line_string = line_string[:2] + '/' + line_string[2:4] + '/' + line_string[4:]

                # Xác định vị trí của dòng và gán giá trị vào id_card_data
                if line == "1.id.png":
                    id_card_data['id'] = line_string
                elif line == "2.name.png":
                    id_card_data['name'] = line_string
                elif line == "3.dob.png":
                    id_card_data['dob'] = line_string
                # elif line == "5.nation.png":
                #     id_card_data['nation'] = line_string
                elif line == "6.origin.png":
                    id_card_data['region'] = line_string

                clear_folder_contents(char_path)

            # Ghi dữ liệu vào file CSV sau khi xử lý một ID card
            csv_writer.writerow([id_card_data[key] for key in id_card_data])
    end = time.time()
    print(end - start)
    shutil.rmtree("chars")
    shutil.rmtree("images")
    shutil.rmtree("info")

big_process()