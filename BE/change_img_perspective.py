import cv2
import numpy as np
from outer_egdes import get_outer_edges
import os
def read_edge_img(original_img_path):
    # Read the image
    # image = cv2.imread('/Users/hoaithuong/SchoolProjects/Parallel Computing/preprocessing/outer_edges_result.png')
    # imageSource = cv2.imread('/Users/hoaithuong/SchoolProjects/Parallel Computing/preprocessing/output_images/output_img.png')

    # original_img = cv2.imread(original_img_path)
    edge_img = get_outer_edges(original_img_path)

    return edge_img

def find_lines(edge_image):

    # Apply Canny edge detection
    edges = cv2.Canny(edge_image, 50, 150, apertureSize=3)

    # Use Hough Line Transform to find lines
    lines = cv2.HoughLines(edges, 2, np.pi / 180, threshold=400)

    return lines
def get_corners_coordinates(edge_img):

    # lines, imageSource = read_image_return_lines("outer_edges_result.png", "output_img.png")
    lines = find_lines(edge_img)

    # Tạo một danh sách chứa tất cả các điểm giao nhau
    intersection_points = []

    # Tìm tất cả các điểm giao nhau của các đường thẳng
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            rho1, theta1 = lines[i][0]
            rho2, theta2 = lines[j][0]

            # Kiểm tra xem hai đường thẳng có gần song song không
            if np.abs(theta1 - theta2) > np.pi / 180:
                # Giải hệ phương trình tìm điểm giao nhau
                A = np.array([
                    [np.cos(theta1), np.sin(theta1)],
                    [np.cos(theta2), np.sin(theta2)]
                ])
                b = np.array([rho1, rho2])

                try:
                    intersection = np.linalg.solve(A, b)
                    intersection_points.append(intersection.astype(int))
                except np.linalg.LinAlgError:
                    # Bắt lỗi nếu ma trận suy biến
                    continue

    # Filter out only positive intersection points
    positive_intersection_points = [point for point in intersection_points if all(coord > 0 for coord in point)]

    # Sort intersection points in clockwise order
    center = np.mean(positive_intersection_points, axis=0)
    positive_intersection_points.sort(key=lambda point: np.arctan2(point[1] - center[1], point[0] - center[0]))

    # Convert to NumPy array
    positive_intersection_points = np.array(positive_intersection_points)

    return positive_intersection_points

# positive_intersection_points = get_corners_coordinates(edge_img)

def transform_perspective(original_img_path, positive_intersection_points,output_path = None):

    original_img = cv2.imread(original_img_path)

    # Use positive_intersection_points in the perspective transformation
    width = 1000
    height = 600
    input_pts = positive_intersection_points.astype(np.float32)
    output_pts = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])

    # Get perspective transformation matrix
    matrix = cv2.getPerspectiveTransform(input_pts, output_pts)


    # Do perspective transformation setting area outside input to black
    img_output = cv2.warpPerspective(original_img, matrix, (width, height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    img_file = open(original_img_path, 'rb') # 'rb' stands for "read binary." In Python, the 'rb' mode is used when opening a file to indicate that you want to read the file in binary mode

    # Create output folder to contain warped image
    if output_path != None:
        os.makedirs(output_path, exist_ok=True)
    # Get the base name (without extension) of the file
    base_name = os.path.splitext(os.path.basename(img_file.name))[0]

    # Save the warped output with the desired file name
    cv2.imwrite(f"{output_path}/{base_name}_warped.jpg", img_output)

    # Show the result
    # cv2.imshow('Result', img_output)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def wrap_perspective(img_path, output_path):

    edge_img = read_edge_img(img_path)
    positive_intersection_points = get_corners_coordinates(edge_img)
    transform_perspective(img_path, positive_intersection_points, output_path)

# wrap_perspective("C:/Users/ttvux/PycharmProjects/Parallel/final_final/images/no_bg/cccd2.png_no_bg.png", 'def')
# wrap_perspective("output_img.png", 'def')
