import argparse
import difflib
import json
import os
import subprocess
import sys

from typing import Dict, Union, List

from natsort import os_sorted

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("-o", "--output", default="README.md")


def get_name(manifest_name: str, manifest: Dict):
    try:
        name = manifest["shortcuts"][0][1]
    except (KeyError, IndexError):
        name = get_name_from_comment(manifest)
        if not name:
            name = (
                manifest_name.replace("-portable", "")
                .replace("-np", "")
                .replace("-py", "")
                .replace("-nightly", "")
            )
    if manifest_name.endswith("-portable"):
        name += " (Portable)"
    if manifest_name.endswith("-np"):
        name += " (Non-Portable)"
    if manifest_name.endswith("-nightly"):
        name += " (Nightly)"
    return name


def get_name_from_comment(manifest: Dict):
    comments: Union[str, List[str]] = manifest.get("##", [])
    if type(comments) == str:
        comments = [comments]
    for comment in comments:
        if comment.startswith(":"):
            return comment[1:]


def get_tracked_files():
    return subprocess.check_output(["git", "ls-files"]).decode()


def print_diff(output: str):
    def color(diff):
        for line in diff:
            if line.startswith("+"):
                yield "\x1b[32m" + line + "\x1b[0m"
            elif line.startswith("-"):
                yield "\x1b[31m" + line + "\x1b[0m"
            elif line.startswith("^"):
                yield "\x1b[34m" + line + "\x1b[0m"
            else:
                yield line

    with open("README.md", encoding="UTF-8") as file:
        current_readme = file.readlines()

    sys.stdout.writelines(
        color(difflib.unified_diff(current_readme, output.splitlines(keepends=True)))
    )


def main():
    args = parser.parse_args()
    tracked_files = get_tracked_files()

    with open("README.template.md", encoding="UTF-8") as file:
        output = file.read()
    output += "<table>\n"

    for filename in os_sorted(os.listdir("bucket")):
        path = f"bucket/{filename}"
        if path not in tracked_files:
            continue
        with open(path) as file:
            manifest = json.loads(file.read())
        manifest_name = os.path.splitext(filename)[0]
        name = get_name(manifest_name, manifest)
        output += f"<tr><td><a href='{manifest['homepage']}'><b>{name}</b></a> — <a href='{path}'><code>{manifest_name}</code></a>"
        if "description" in manifest:
            output += f" <br> {manifest['description']} <br><br>"
        output += "</td></tr>\n"

    output += "</table>\n"
    print_diff(output)

    if not args.dry_run:
        with open(args.output, "w+", encoding="UTF-8") as file:
            file.write(output)


if __name__ == "__main__":
    main()
