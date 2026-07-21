#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Das Lebensspiel und seine Regeln",
    "--doc-subtitle", """
Sammelband:
Das geheime Tor zu Fortschritt und Erfolg.
Die Kraft des gesprochenen Wortes.
Dein Wort ist dein Zauberstab
    """,
    # "--doc-original-title", "The Game of Life and How to Play It", # TODO
    "--doc-description", """
Unser Leben funktioniert nach bestimmten Regeln.
Wenn wir sie beachten, dann geht es uns gut
und wir können das Spiel des Lebens erfolgreich spielen.

Florence Shinn war eine der berühmtesten Weisheitslehrerinnen des vergangenen Jahrhunderts.
Für jeden von uns, so betont sie, steht die vollkommene Fülle bereit.
Wir müssen sie nur sehen.
Denn geleitet durch Gottes Vorsehung kann jeder von uns eine positive Lebenseinstellung entwickeln -
und glücklich sein!
""",
    # "--doc-subject", "",
    "--doc-date", "2016",

    # "--doc-edition", "13", # 2011
    "--doc-edition", "14", # 2016?
    # "--doc-edition", "15", # 2024

    "--doc-extent", "306 pages",
    "--doc-author", "Florence Scovel Shinn",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "TODO",
    "--doc-publisher", "Freya Verlag",
    "--doc-language", "de",
    "--doc-isbn", "9783990250273",
    "--doc-cover-image", "070-deskew/307.tiff",
    "--canonical-url-base", "https://milahu.github.io/shinn-florence-scovel-das-lebensspiel-und-seine-regeln-2016/",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = src.glob("*.hocr")

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
