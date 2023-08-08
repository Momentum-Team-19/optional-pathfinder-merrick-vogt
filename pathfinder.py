from PIL import Image
import random


def elevation_to_grayscale(value, max_value):
    # Set elevation to gray scale color. Max value is 255 black.
    return int((value / max_value) * 255)


# Maximize contrast of the image by using max and min elevation
def contrast_stretch(image):
    # Get the minimum and maximum pixel values in the image
    min_pixel = image.getextrema()[0]
    max_pixel = image.getextrema()[1]

    # Apply contrast stretching to map the pixel values to the full grayscale range
    return image.point(lambda x: 255 * (x - min_pixel) / (max_pixel - min_pixel))


# create a 2D array from data points. Include the desired rows and columns
# number of data points must equal (num of rows) * (num of columns)
def create_2d_zero_array(data_points, rows, columns):
    if len(data_points) != rows * columns:
        raise ValueError("The number of data points should match the rows and columns specified.")
    zero_array = []
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(0)
        zero_array.append(row)
    return zero_array


def create_2d_array_from_list(data_points, rows, columns):
    if len(data_points) != rows * columns:
        raise ValueError("The number of data points should match the rows and columns specified.")
    data_array = []
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(data_points[i * columns + j])
        data_array.append(row)
    return data_array


def greedy_walk(data_array, rows, columns):
    y = 300
    # start path at [0, y]
    short_path = [[0, y]]
    # for x in range(columns-1):
    for x in range(250):
        current_elevation = data_array[x][y]
        # bounds for top of the map
        upright_elevation = data_array[x+1][min(y+1, columns-1)]
        right_elevation = data_array[x+1][y]
        # bounds for bottom of the map
        downright_elevation = data_array[x+1][max(y-1, 0)]

        options = [abs(current_elevation - upright_elevation),
                   abs(current_elevation - right_elevation),
                   abs(current_elevation - downright_elevation)]

        # logic for finding least elevation change of 3 options
        # if all options are unique
        if options[0] != options[1] and options[0] != options[2] and options[1] != options[2]:
            greedy_option = min(options)
        # if all options are equal
        elif options[0] == options[1] and options[1] == options[2]:
            greedy_option = options[1]

        # if only option 0 equals option 1
        elif options[0] == options[1]:
            greedy_option = options[1]
            if options[1] > options[2]:
                greedy_option = options[2]

        # if only option 2 equals option 1
        elif options[1] == options[2]:
            greedy_option = options[1]
            if options[1] > options[0]:
                greedy_option = options[0]

        # if options 0 equals option 2
        elif options[0] == options[2]:
            greedy_option = random.choice([options[0], options[2]])
            if options[1] < options[0]:
                greedy_option = options[1]

        # move to greedy option
        if greedy_option == options[0]:
            y += 1
        elif greedy_option == options[1]:
            y += 0
        elif greedy_option == options[2]:
            y += -1

        if x < 11:
            print(f'current_elevation: {current_elevation}')
            print(f'up: {upright_elevation} right: {right_elevation} down: {downright_elevation}')
            print(options)
            print(f'option picked: {greedy_option}')
            print(f'x: {x+1} y: {y}')

        # start appending at index 1 instead of 0.
        short_path.append([x+1, y])

    return short_path


def draw_short_path(text_file_path, input_img_path, output_img_path):
    # Open the image
    image = Image.open(input_img_path)

    # Ensure that the image is in RGB mode (necessary for setting pixel colors)
    image = image.convert("RGB")

    # Get the pixel data
    pixels = image.load()

    columns, rows = image.size

    # Read elevation data from text file
    data_points = []
    with open(text_file_path, 'r') as file:
        for line in file:
            # strip takes off whitespace on the left and right of the line
            # split, separates the data between each space
            # int converts the data as a string into integer
            # extend adds all the elements to the data_points list
            data_points.extend(map(int, line.strip().split()))

    # Using Greedy Algorithm
    data_array = create_2d_array_from_list(data_points, rows, columns)
    # print(data_array)
    greedy_walk_array = greedy_walk(data_array, rows, columns)
    
    # print(greedy_walk_array)

    for index, location in enumerate(greedy_walk_array):
        pixels[location[0], location[1]] = (255, 0, 0)  # set pixel to red
        if index > 130:
            pixels[location[0], location[1]] = (0, 255, 0)  # set pixel to green
    # Save the modified image
    image.save(output_img_path)


def create_img_from_elevation(text_file_path, output_image_path):
    # Read elevation data from text file
    data_points = []
    with open(text_file_path, 'r') as file:
        for line in file:
            # strip takes off whitespace on the left and right of the line
            # split, separates the data between each space
            # int converts the data as a string into integer
            # extend adds all the elements to the data_points list
            data_points.extend(map(int, line.strip().split()))

    # Calculate the size of the square image based on the total number of data points
    image_size = int(len(data_points) ** 0.5)

    # Get Max value of elevation
    max_value = max(data_points)

    # Create a blank image with the calculated size
    image = Image.new('L', (image_size, image_size))

    # Set color of each pixel based on the elevation
    # create an object of the PixelAccess class
    pixels = image.load()
    # Loop through each data point with index and element
    for i, data_point in enumerate(data_points):
        # Clever way of getting the x-index with using the 
        # modulo of the image_size so it sets to zero after 
        # moving on to the next line below
        x = i % image_size

        # Clever way of getting the y-index by dividing the 
        # index by the image size and rounding down. 
        y = i // image_size

        # use the function to get the grayscale value
        grayscale_value = elevation_to_grayscale(data_point, max_value)
        # set each pixel in the pixel 2D array to the grayscale
        pixels[x, y] = grayscale_value

        # Show processing progress
        # if x % image_size - 1 == 0 and y % 10 == 0:
        #     print(f"Finished processing line {y + 1} out of {image_size}")

    # Apply contrast stretching to the image
    image = contrast_stretch(image)

    # save the impage to the output path.
    image.save(output_image_path)


# Creating Images from text file data
# Elevation points must be separated by a space
small_input_file = 'elevation_small.txt'
small_output_image = 'small_elevation_image.png'
create_img_from_elevation(small_input_file, small_output_image)
small_one_path_output_image = 'small_one_path_output_image.png'
draw_short_path(small_input_file, small_output_image, small_one_path_output_image)

large_input_file = 'elevation_large.txt'
large_output_image = 'large_elevation_image.png'
create_img_from_elevation(large_input_file, large_output_image)
# short_path_output_image = 'short_path_output_image.png'
# draw_short_path(large_input_file, large_output_image, short_path_output_image)

# Testing

