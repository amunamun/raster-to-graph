import cv2

# Read walls from file
def read_walls(file_path):
    walls = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 8 and parts[-2] == 'wall':
                coords = list(map(int, parts[:8]))
                walls.append(coords)
    return walls

# Plotting the walls on an existing image
def plot_walls(walls, background_image, output_file='floor_plan.png'):
    # Load the background image
    img = cv2.imread(background_image)

    if img is None:
        raise FileNotFoundError(f"The background image '{background_image}' was not found.")

    # Draw walls
    for wall in walls:
        points = [(wall[0], wall[1]), (wall[2], wall[3]), (wall[4], wall[5]), (wall[6], wall[7]), (wall[0], wall[1])]
        for i in range(len(points) - 1):
            cv2.line(img, points[i], points[i + 1], color=(0, 0, 0), thickness=5)

    # Save and display the output
    cv2.imwrite(output_file, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Main execution
if __name__ == "__main__":
    file_path = 'frederik_stangs_gate_11_0.etg_0000.txt'  # Replace with your file path
    background_image = 'plain_sheet.png'  # Replace with your PNG file path
    walls = read_walls(file_path)
    plot_walls(walls, background_image)