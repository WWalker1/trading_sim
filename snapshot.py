import os

def create_snapshot(root_dir, output_file):
    project_files = [
        'main.py',
        'core/__init__.py',
        'core/config.py',
        'core/player.py',
        'core/factory.py',
        'core/market.py',
        'core/button.py',
        'core/game.py', 
        'core/faction.py'
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write directory structure
        f.write("Directory Structure:\n")
        f.write("project_root/\n")
        f.write("├── main.py\n")
        f.write("└── core/\n")
        for file in project_files[1:]:  # Skip main.py
            f.write(f"    └── {os.path.basename(file)}\n")
        f.write("\n" + "=" * 80 + "\n\n")

        # Write file contents
        for file_path in project_files:
            full_path = os.path.join(root_dir, file_path)
            f.write(f"File: {file_path}\n")
            f.write("=" * (len(file_path) + 6) + "\n\n")
            try:
                with open(full_path, 'r', encoding='utf-8') as source_file:
                    f.write(source_file.read())
            except FileNotFoundError:
                f.write(f"Error: File not found - {file_path}\n")
            f.write("\n\n" + "=" * 80 + "\n\n")

if __name__ == "__main__":
    root_directory = "."  # Assumes the script is run from the project root
    output_file = "code_snapshot.txt"
    create_snapshot(root_directory, output_file)
    print(f"Code snapshot created: {output_file}")