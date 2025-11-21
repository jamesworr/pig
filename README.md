## PIG
# Python Images for Gameboy
Convert 24bit color images into GBA tilemaps and palettes.  Allows for visualization of palette colors and tiles.

# Usage
```
usage: pig.py [-h] [--out_path OUT_PATH] [--x_tiles X_TILES] [--y_tiles Y_TILES] mode image_path

positional arguments:
  mode                  sprite or bg mode
  image_path            Image to feed the pig

options:
  -h, --help            show this help message and exit
  --out_path, -o OUT_PATH
                        Output directory for the source files
  --x_tiles, -x X_TILES
                        Output tile X dimension
  --y_tiles, -y Y_TILES
                        Output tile Y dimension
```
**Subject to change with future improvements
