## PIG
# Python Images for Gameboy
Convert 24bit color images into GBA tilemaps and palettes.  Allows for visualization of palette colors and tiles.

# Usage
```
pig.py [-h] [--out_path OUT_PATH] [--x_tile_count X_TILE_COUNT] [--y_tile_count Y_TILE_COUNT] [--bg] [--sprite] image_path

positional arguments:
  image_path            Image to feed the pig

options:
  -h, --help            show this help message and exit
  --out_path, -o OUT_PATH
                        Output directory for the source files
  --x_tile_count, -x X_TILE_COUNT
                        Output tile X dimension
  --y_tile_count, -y Y_TILE_COUNT
                        Output tile Y dimension
  --bg, -b              Background Tile Mode
  --sprite, -s          Sprite Tile Mode
```
**Subject to change with future improvements
