# Python Images for Gameboy (PIG)
#
# Convert 24bit color images to GBA BGR555 format
# Will Orr 10/14/25
#

import cv2
import sys
import numpy as np
import math
import os
import argparse

class Tile:
    tile_pixel_map = []
    def __init__(self, pixel_map, map_x, map_y):
        for _ in range(0,8):
           self.tile_pixel_map.append([0]*8)
        # TODO figure out a less dumb/lazy way.  too late at night
        self.tile_pixel_map = np.rot90(np.fliplr(np.array([pixel_map[i][map_y:(map_y+8)] for i in range(map_x, map_x+8)])), k=1).tolist()

    def __eq__(self, other):
        return self.tile_pixel_map == other.tile_pixel_map

    def __hash__(self):
        #return(hash(self.tile_pixel_map))
        return hash(tuple([tuple(self.tile_pixel_map[i]) for i in range(0, 8)]))

    def to_string():
        ret_str = ""
        for x in range(0,8):
            for y in range(0,8):
                ret_str += f"{self.tile_pixel_map[x][y]}" # FIXME just a placeholder

    def debug_print():
        print(self.tile_pixel_map())

def pig_picture():
    print(r"                      ---------- ")
    print(r"      ------   ----  (          )")
    print(r"     /      \-/ \/o\ (   Oink   )")
    print(r"    /            --: (          )")
    print(r"    \           /    /----------)")
    print(r"     \-  ---  -/    /            ")
    print(r"       | |  | |                  ")

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
    palette_rev = {}

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
            img_map[y].append(palette[(b, g, r)])
    
    for key in list(palette.keys()):
        #print(f"{key} {type(key)} {palette[key]}")
        palette_rev[palette[key]] = key

    return img_map, palette, palette_rev

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
        cv2.rectangle(pal_image, top_xy, bot_xy, pal_colors[counter], -1)
        counter += 1

    cv2.imshow("Original Palette", pal_image)

def write_palette(pal, asm_path, filename):
    # TODO quit writing fixed size
    PAL_WIDTH  = 8
    GRP_HEIGHT = 8
    GRP_COUNT  = 4

    with open(asm_path+"/"+filename+".s", "a") as file:
        # section header
        file.write("    .section .rodata\n")
        file.write("    .align  2\n")
        file.write(f"    .global {filename}_pal\n")
        file.write(f"    .hidden {filename}_pal\n")
        file.write(f"{filename}_pal:\n")

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
                file.write(line+"\n")
            file.write("\n")

def generate_tiles(pixel_map, pal):
    tile_dict = {}
    tile_map = []
    # TODO double check its multiple of 8
    for x in range(0,len(pixel_map),8):
        tile_map.append([])
        for y in range(0,len(pixel_map[0]),8):
            #print(f"{x},{y}")
            curr_tile = Tile(pixel_map, x, y)
            #draw_tile(curr_tile, pal)

            if curr_tile not in tile_dict:
                tile_dict[curr_tile] = len(tile_dict)

            tile_map[math.floor(x/8)].append(tile_dict[curr_tile])
    return tile_map, tile_dict

def draw_tile(tile, pal_colors):
    tile_image = np.zeros((500, 500, 3), dtype=np.uint8) + 255
    tile_colors = list(pal.keys())

    top_left_corner = (50, 50)
    bottom_right_corner = (200, 300)
    rect_size = 50
    for counter in range(0,64):
        top_xy = (rect_size*(counter%8), rect_size*int(counter/8))
        bot_xy = (rect_size*(counter%8)+rect_size, rect_size*int((counter/8))+rect_size)
        cv2.rectangle(tile_image, top_xy, bot_xy, pal_colors[tile.tile_pixel_map[counter%8][math.floor(counter/8)]], -1)
        counter += 1

    cv2.imshow("Tile", tile_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def write_tile_map(tile_map, asm_path, x_tile_count, y_tile_count, filename):

    with open(asm_path+"/"+filename+".s", "a") as file:
        # section header
        file.write("    .section .rodata\n")
        file.write("    .align  2\n")
        file.write(f"    .global {filename}_map\n")
        file.write(f"    .hidden {filename}_map\n")
        file.write(f"{filename}_map:\n")

        line_count = 0
        line = "    .hword "
        for x in range(0, x_tile_count):
            for y in range(0, y_tile_count):
                #print(f"{x},{y}")
                if line_count >= 8:
                    file.write(line+"\n")
                    line = "    .hword "
                    line_count = 0
                if x < len(tile_map) and y < len(tile_map[0]):
                    line += f"0x{tile_map[x][y]:04x}"
                else:
                    line += "0x0000"
                if line_count < 7:
                    line += ","
                line_count += 1

        file.write(line+"\n") # write final line

def write_tile_data(tiles, asm_path, filename):
    # TODO support other sizes
    GRP_WIDTH  =  8
    
    with open(asm_path+"/"+filename+".s", "w") as file:
        # section header
        file.write("    .section .rodata\n")
        file.write("    .align  2\n")
        file.write(f"    .global {filename}_tiles\n")
        file.write(f"    .hidden {filename}_tiles\n")
        file.write(f"{filename}_tiles:\n")

        flat_tiles = []
        for tile in tiles:
            for y in range(0, 8):
                for x in range(0, 8, 4):
                    num = (tile.tile_pixel_map[x+3][y]<<24) \
                        + (tile.tile_pixel_map[x+2][y]<<16) \
                        + (tile.tile_pixel_map[x+1][y]<<8 ) \
                        +  tile.tile_pixel_map[x][y]
                    flat_tiles.append(num)

        #print(f"flat tile count: {len(flat_tiles)}")
        tile_count = 0
        for _ in range(0, math.ceil(len(flat_tiles)/8)):
            line = "    .word "
            for width in range(0, GRP_WIDTH):
                if tile_count < len(flat_tiles):
                    #print(tile_map[tile_count])
                    line += f"0x{flat_tiles[tile_count]:08x}"
                else:
                    line += "0x00000000"
                if width < GRP_WIDTH-1:
                    line += ","
                tile_count += 1
            file.write(line+"\n")
        file.write("\n")
       # print(f"tile_count: {tile_count}")
        return tile_count

def write_header(tile_count, map_count, pal_count, header_path, filename):
    with open(header_path+"/"+filename+".h", "w") as file:
        # TODO add ifndef guards
        file.write(f"#define {filename}_tiles_len {tile_count*4}\n") # word, 4 bytes
        file.write(f"extern const unsigned int {filename}_tiles[{tile_count}];\n")
        file.write(f"#define {filename}_map_len {map_count*2}\n") # half word, 2 bytes
        file.write(f"extern const unsigned short {filename}_map[{map_count}];\n")
        file.write(f"#define {filename}_pal_len {pal_count*2}\n") # half word, 2 bytes
        file.write(f"extern const unsigned short {filename}_pal[{pal_count}];\n")

# arguments
parser = argparse.ArgumentParser(description="PIG")
parser.add_argument("image_path", type=str, help="Image to feed the pig") # required
parser.add_argument("--out_path", "-o", type=str, default="./", help="Output directory for the source files")
parser.add_argument("--x_tile_count", "-x", type=int, default=32, help="Output tile X dimension")
parser.add_argument("--y_tile_count", "-y", type=int, default=32, help="Output tile Y dimension")
parser.add_argument("--bg", "-b", action="store_true", help="Background Tile Mode") # TODO use me
parser.add_argument("--sprite", "-s", action="store_true", help="Sprite Tile Mode") # TODO use me
args = parser.parse_args()

image_path   = args.image_path
filename     = os.path.basename(image_path)[0:-4]
out_path     = args.out_path
x_tile_count = args.x_tile_count
y_tile_count = args.y_tile_count

if args.bg and args.sprite:
    print("Can't have both background and sprite modes selected. Try again :(")
    quit(0)

pig_picture()
image = cv2.imread(image_path)

img_map, pal, pal_rev = generate_map(image)
draw_palette(pal)
tile_map, tiles = generate_tiles(img_map, pal_rev)

#temp_count = 0
#for tile in list(tiles.keys()):
#    print(temp_count)
#    draw_tile(tile, pal_rev)
tile_count = write_tile_data(tiles, out_path, filename)
write_tile_map(tile_map, out_path, x_tile_count, y_tile_count, filename)
write_palette(pal, out_path, filename)

map_count = x_tile_count * y_tile_count
pal_count = len(pal_rev)
write_header(tile_count, map_count, pal_count, out_path, filename)


# TODO support other GBA map size (32x32, 64x32, etc) on CLI args
# TODO implement sprite mode
# TODO add unit tests using the test pattern

