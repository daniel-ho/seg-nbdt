"""Generate copies of template but with jinja2 template populated with dir files

Assumes that filenames match in all passed dirs. e.g.,

dir1/file1.jpg
dir2/file1.jpg
dir3/file1.jpg

then give this script

dir1=var1 dir2=var2 dir3=var3

then this script will output

file1.html

where all var1 are replaced with dir1/file1.jpg, var2 with dir2/file1.jpg...
"""

import argparse
from jinja2 import Template
from vis_grid import paths_from_directories
from pathlib import Path
import glob


parser = argparse.ArgumentParser()
parser.add_argument('template', help='Jinja2 template HTML')
parser.add_argument('--dirs-for-cls', type=str)
parser.add_argument('--dir', nargs=2, action='append', help='Dir name, then the var in the Jinja2 template to replace')
parser.add_argument('--file', choices=('sort', 'match'), default='match')
parser.add_argument('--suffix', type=str, help='Suffix for all output file names')
args = parser.parse_args()


with open(args.template) as f:
    template = Template(f.read())


assert args.dir or args.dirs_for_cls, 'Need at least one dir OR specify cls'

if args.dirs_for_cls:
    dir_to_var = {dir: dir.split('_')[3] for dir in glob.iglob(f'*whole*{args.dirs_for_cls}*crop400')}
    dir_to_var[next(glob.iglob(f'*{args.dirs_for_cls}*original'))] = 'original'
else:
    dir_to_var = {dir: var for (dir, var) in args.dir}

for dir in sorted(dir_to_var):
    print(dir, ':', dir_to_var[dir])

paths_per_fnames = paths_from_directories(dir_to_var, args.file,
    filt=lambda path: 'pixel' in path)
print('Paths:', len(paths_per_fnames))
for paths_per_fname in paths_per_fnames:
    context = {}
    for path in paths_per_fname:
        path = Path(path)
        var = dir_to_var[str(path.parent)]
        context[var] = str(path)

    stem = Path(paths_per_fname[0]).stem
    path = f'{stem}{args.suffix}.html'
    with open(path, 'w') as f:
        f.write(template.render(**context))
