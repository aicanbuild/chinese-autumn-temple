"""Current sculpture rebuild: preserve original hand losses as requested.
Historical reconstruction scripts remain archived; do not reintroduce their hands.
"""
import runpy
from pathlib import Path
SOURCE=Path(__file__).resolve().parent
for step in [
 'remove_buddha_hands.py',
 'build_sculpture_lod.py',
]:
 runpy.run_path(str(SOURCE/step),run_name='__main__')
