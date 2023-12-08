import cv2
import numpy as np

def get_outer_edges(img_path):
    # Read the image
    # image = cv2.imread('output_img.png', cv2.IMREAD_GRAYSCALE)

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Apply Canny edge detector
    edges = cv2.Canny(blurred, 30, 100)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty image to draw the outer edges
    outer_edges_image = np.zeros_like(image)

    # Draw the outer edges on the empty image
    cv2.drawContours(outer_edges_image, contours, -1, 255, 1)

    # Save the resulting image
    # cv2.imwrite('outer_edges_result.png', outer_edges_image)
    #
    # # Display the original image and the outer edges
    # cv2.imshow('Original Image', image)
    # cv2.imshow('Outer Edges Detection', outer_edges_image)
    #
    # # Wait indefinitely until you push a key, then close the windows
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return outer_edges_image