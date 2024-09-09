import os
from pathlib import Path

# List of folders to exclude (dependencies, builds, etc.)
excluded_dirs = ['node_modules', 'venv', '.git', 'dist',
                 'build', 'vendor', 'bin', 'out', '__pycache__']

# List of file extensions to include
included_extensions = [
    # Go
    '.go', '.mod', '.sum',
    # Python
    '.py', 'requirements.txt', 'Pipfile', 'pyproject.toml', '.json'
    # React (JavaScript, TypeScript)
    '.js', '.jsx', '.ts', '.tsx', 'package.json',
    # General (Markdown, YAML, HTML, CSS)
    '.md', '.yaml', '.yml', '.html', '.css'
]


def load_gitignore_patterns():
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = [line.strip() for line in f if line.strip()
                        and not line.startswith("#")]
        return patterns
    return []


def is_ignored(filepath, patterns):
    try:
        relative_filepath = filepath.relative_to(Path.cwd())
    except ValueError:
        return False
    for pattern in patterns:
        if relative_filepath.match(pattern):
            return True
    return False


# Define the directory containing your files
root_dir = "."

# Load gitignore patterns
ignore_patterns = load_gitignore_patterns()

# Open a new text file to write the combined contents
with open("source.txt", "w", encoding="utf-8") as outfile:
    # Walk through all directories and files
    for subdir, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            filepath = Path(subdir) / file
            # Check if the file has the correct extension and is not ignored
            if any(str(filepath).endswith(ext) for ext in included_extensions) and not is_ignored(filepath, ignore_patterns):
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(f"\n--- Start of {filepath} ---\n")
                        outfile.write(infile.read())
                        outfile.write(f"\n--- End of {filepath} ---\n")
                except Exception as e:
                    pass  # Skip unreadable files
