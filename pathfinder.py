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
    short_path = []
    shortest_path = []
    short_path_array = []
    for y in range(rows-1):
        # restart elevation change count for each path
        total_elevation_change = 0
        path_row = []

        # for x in range(columns-1):
        for x in range(columns-1):
            current_elevation = data_array[y][x]
            # bounds for top of the map. min(y+1, columns-1)
            upright_elevation = data_array[max(y-1, 0)][x+1]
            right_elevation = data_array[y][x+1]
            # bounds for bottom of the map. max(y-1, 0)
            downright_elevation = data_array[min(y+1, columns-1)][x+1]

            options = [abs(current_elevation - upright_elevation),
                       abs(current_elevation - right_elevation),
                       abs(current_elevation - downright_elevation)]
        
            # Default to an invalid index
            greedy_option_index = 1

            # If all options are distinct
            if options[0] != options[1] and options[0] != options[2] and options[1] != options[2]:
                greedy_option_index = options.index(min(options))
            # If all options are equal
            elif options[0] == options[1] and options[1] == options[2]:
                greedy_option_index = 1
            # If only option 0 equals option 1
            elif options[0] == options[1]:
                greedy_option_index = 1
                if options[1] > options[2]:
                    greedy_option_index = 2
            # If only option 2 equals option 1
            elif options[1] == options[2]:
                greedy_option_index = 1
                if options[1] > options[0]:
                    greedy_option_index = 0
            # If options 0 equals option 2
            elif options[0] == options[2]:
                greedy_option_index = 0 if random.choice([0, 2]) == 0 else 2
                if options[1] < options[0]:
                    greedy_option_index = 1

            # Move to greedy option
            if greedy_option_index == 0:
                y += -1
            elif greedy_option_index == 1:
                y += 0
            elif greedy_option_index == 2:
                y += 1

            # start appending at index 1 instead of 0.
            short_path.append([x+1, y])
            path_row.append([x+1, y]) 
            
            total_elevation_change += options[greedy_option_index]
        shortest_path.append(total_elevation_change)
        short_path_array.append(path_row)
        
    shortest_path_index = shortest_path.index(min(shortest_path))
    
    return short_path, short_path_array[shortest_path_index]


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
    
    greedy_walk_paths = greedy_walk(data_array, rows, columns)
    

    for index, location in enumerate(greedy_walk_paths[0]):
        pixels[location[0], location[1]] = (255, 0, 0)  # set pixel to red

    for index, location in enumerate(greedy_walk_paths[1]):
        pixels[location[0], location[1]] = (0, 255, 0) # set pixel to green
   
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
short_path_output_image = 'short_path_output_image.png'
draw_short_path(large_input_file, large_output_image, short_path_output_image)

# Testing

test_input_file = 'test.txt'
test_output_image = 'test_image.png'
create_img_from_elevation(test_input_file, test_output_image)
test_one_path_output_image = 'test_one_path_output_image.png'
draw_short_path(test_input_file, test_output_image, test_one_path_output_image)