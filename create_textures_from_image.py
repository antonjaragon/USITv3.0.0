import subprocess
from pathlib import Path

# Base paths
masks_base = Path('./masks')
circles_base = Path('./circles')
input_base = Path('./input_images')
textures_base = Path('./textures')
cnn_script = Path('./packages/cnnmasktomanuseg/cnnmasktomanuseg.py')

# Scan all PNG files inside the masks directory (including subfolders)
for mask_file in masks_base.rglob('*.png'):
    # Get relative path from the masks folder (e.g., subfolder1/subfolder2/file1.png)
    relative_path = mask_file.relative_to(masks_base)
    stem = mask_file.stem  # "file1"

    # Folder paths based on relative structure
    circle_dir = circles_base / relative_path.parent
    input_tiff = input_base / relative_path.with_suffix('.tiff')
    inner_txt = circle_dir / f'{stem}.inner.txt'
    outer_txt = circle_dir / f'{stem}.outer.txt'
    output_texture = textures_base / relative_path.with_name(f"{stem}_texture.bmp")
    output_texture_enhanced = textures_base / relative_path.with_name(f"{stem}_enhanced_texture.bmp")

    # Make sure necessary folders exist
    circle_dir.mkdir(parents=True, exist_ok=True)
    output_texture.parent.mkdir(parents=True, exist_ok=True)

    # Command 1: run the python script with directory as output
    cmd1 = [
        'python', str(cnn_script),
        str(mask_file),
        str(circle_dir)
    ]

    # Command 2: run manuseg
    cmd2 = [
        'manuseg',
        '-i', str(input_tiff),
        '-c', str(inner_txt), str(outer_txt),
        '', '',
        '-o', str(output_texture),
        '-q'
    ]

    # Command 3: same as cmd2, but with -e and different output name
    cmd3 = [
        'manuseg',
        '-i', str(input_tiff),
        '-c', str(inner_txt), str(outer_txt),
        '', '',
        '-o', str(output_texture_enhanced),
        '-q',
        '-e'
    ]

    print(f"\nRunning CNN mask to manuseg for: {mask_file}")
    subprocess.run(cmd1, check=True)

    print(f"Running manuseg (default) for: {input_tiff}")
    subprocess.run(cmd2, check=True)

    print(f"Running manuseg (enhanced) for: {input_tiff}")
    subprocess.run(cmd3, check=True)

print("\n✅ All files processed.")
