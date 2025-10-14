# Python Images for Gameboy (PIG)
#
# Convert 24bit color images to GBA BGR555 format
# Will Orr 10/14/25
#

import cv2
import sys
import numpy as np

def rgb888_to_bgr555_str(rgb):
    #bgr = (rgb[2]>>3, rgb[1]>>3, rgb[0]>>3)
    bgr = (rgb[0]>>3)<<10 | (rgb[1]>>3)<<5 | (rgb[2]>>3)
    #print(rgb)
    bgr_str = f"{bgr:04x}"
    #print(bgr_str)
    #print("---------------------")
    return bgr_str

def generate_map(image):
    img_map = []
    palette = {}

    for y in range(0,len(image)):
        img_map.append([])
        for x in range(0,len(image[y])):
            (b, g, r) = image[y][x]
            # defaults to np uint8, cast to int
            (b, g, r) = tuple([int(item) for item in (b, g, r)])

            # create new entry for this color if it doesn't exist
            if (b, g, r) not in palette:
                palette[(b, g, r)] = len(palette)

            # look up palette ID for color and insert into the map
            #print(len(palette))
            img_map[y].append(palette[(b, g, r)])
    return img_map, palette

def draw_palette(pal):
    pal_image = np.zeros((500, 500, 3), dtype=np.uint8) + 255
    pal_colors = list(pal.keys())

    top_left_corner = (50, 50)
    bottom_right_corner = (200, 300)
    counter = 0
    rect_size = 50
    for color in pal_colors:
        top_xy = (rect_size*(counter%5), rect_size*int(counter/5))
        bot_xy = (rect_size*(counter%5)+rect_size, rect_size*int((counter/5))+rect_size)
        #print(top_xy)
        #print(bot_xy)
        cv2.rectangle(pal_image, top_xy, bot_xy, pal_colors[counter], -1)
        counter += 1

    cv2.imshow("Original Palette", pal_image)

def write_palette(pal):
    # TODO support other sizes
    PAL_WIDTH  = 8
    GRP_HEIGHT = 8
    GRP_COUNT  = 4

    # TODO convert to file write
    # section header
    print("    .section .rodata")
    print("    .align  2")
    print("    .global bowl_bgPal      @ 512 unsigned chars")
    print("    .hidden bowl_bgPal") # TODO fix the name
    print("bowl_bgPal:")

    pal_colors = list(pal.keys())
    color_idx = 0
    for group in range(0, GRP_COUNT):
        for height in range(0, GRP_HEIGHT):
            line = "    .hword "
            for width in range(0, PAL_WIDTH):
                if color_idx < len(pal_colors):
                    line += f"0x{rgb888_to_bgr555_str(pal_colors[color_idx])}"
                else:
                    line += "0x0000"
                if width < PAL_WIDTH-1:
                    line += ","
                color_idx += 1
            print(line)
        print("")


image_path = sys.argv[1]
print(image_path)
image = cv2.imread(image_path)

img_map, pal = generate_map(image)
draw_palette(pal)
write_palette(pal)

cv2.imshow("Original", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
