#!/usr/bin/env python3
"""
This functions has lax approach to variable scope, relying on semi-accidental
closures, for example fails is accessed as if it was passed. Meant for
readability. Don't complain.

YOU CAN MAINLY IGNORE THIS FILE, but well done if you do! And say so
in the interview.
"""
from argparse import ArgumentParser
from collections import namedtuple
import functools
import logging
import os
from pprint import pformat
import re
import subprocess
import sys
from typing import Match, Optional

from binaryornot.check import is_binary
from flake8.main.git import find_modified_files

CMD_NOT_FOUND_MSG = 'No such file or directory'

CMD_NOT_FOUND_RC = -100

EXCLUDED_FILES = set()

# common part (copied verbatim to other hooks, no imports please)
JIRA_PROJECT_SYMBOL = 'RE'
DEBUG = False
LINE = '█' * 70
Result = namedtuple('Result', ['out', 'rc'])

colours = {'RED': 41, 'GREEN': 42, 'YELLOW': 43, 'blue': 94, 'magenta': 95, 'red': 31, 'green': 32, 'yellow': 33}


def step(func):
    # collect step functions, run conditionally
    step.collect.append(func.__name__)

    def inner(*args_, **kwargs):
        # either of lists defined and contains or both empty
        if (skip and func.__name__ not in skip) or (only and func.__name__ in only) or (not skip and not only):
            title(func.__name__)
            fails.update(func(*args_, **kwargs))
        else:
            debug(func.__name__, 'skipped')
    return inner


step.collect = []


def set_logging():
    if DEBUG:
        # flake has nice logs, useful for getting setup.cfg right, isort doesn't have logs
        log = logging.getLogger('flake8.options.config')
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'\033[{colours["yellow"]}m%(name)s %(message)s\033[0m', datefmt='%H:%M:%S')
        ch.setFormatter(formatter)
        log.addHandler(ch)


def colour(colour_label: str, msg: str):
    sys.stdout.write(f'\033[{colours[colour_label]:d}m{msg}\033[0m\n')


def debug(*msgs, c='yellow'):
    # takes strings or callables to save time if not DEBUG
    if DEBUG:
        colour(c, ' '.join(str(x()) if callable(x) else str(x) for x in msgs))


def git_available():
    return os.path.exists('.git')


@functools.lru_cache()
def run(cmd: str, fine_if_command_not_found=False, doprint=False, **kwargs) -> Result:
    # pass shell=True to use bash globs, pipes and other builtins
    # TODO: fine_if_command_not_found logic is getting out of hand
    try:
        result = subprocess.run(
            cmd if kwargs.get('shell', False) else cmd.split(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs
        )
        out, rc = result.stdout.decode('utf-8'), result.returncode
    except Exception as e:
        # won't raise if shell=True
        out, rc = str(e), CMD_NOT_FOUND_RC
        if fine_if_command_not_found and CMD_NOT_FOUND_MSG in str(e):
            rc = 0
    if CMD_NOT_FOUND_MSG in str(out):
        rc = CMD_NOT_FOUND_RC
        if fine_if_command_not_found:
            rc = 0

    debug('run', cmd, kwargs, out.strip(), rc, c='blue')
    if doprint:
        sys.stdout.write(out)
    return Result(out, rc)


def generic_debug_info():
    debug('in:', __file__, c='magenta')
    debug('repo exists:', lambda: git_available())
    debug('cwd:', lambda: os.getcwd())
    debug('last commit:', lambda: run('git rev-parse --short=8 HEAD~1').out)
    debug('branch_name:', lambda: repr(run('git rev-parse --abbrev-ref HEAD').out.rstrip()))


# hook specific
fails = {}

valid_branch_name = (
    '(?P<branch_name>'
    '(?P<front_or_back>frontend|backend)'
    '/'
    f'{JIRA_PROJECT_SYMBOL}-(?P<task_no>\d+)'
    '/'
    '(?P<description>.*)'
    # during rebase branch name is called HEAD
    '|master'
    '|HEAD'
    '|wip_.*'
    ')'
)


def title(msg: str):
    sys.stdout.write(f'\n{LINE}\r\t {msg} \n')


@step
def frontend_lint() -> dict:
    lint = run('yarn lint', cwd='frontend', fine_if_command_not_found=True)
    sys.stdout.write(lint.out)
    return {'frontend': lint.rc,}


@step
def backend_flake8_isort() -> dict:
    from flake8.main.git import hook as flake8_hook
    from isort.hooks import git_hook as isort_hook
    return {
        'isort': isort_hook(strict=True),
        'flake8': flake8_hook(strict=True),
    }


@step
def run_backend_tests():
    tests = run('pytest backend --create-db')
    if tests.rc != 0:
        sys.stdout.write(tests.out)
    return {
        'backend_tests': tests.rc
    }


@step
def yamllint():
    lint = run(
        'find -name \*yml -not -path "./frontend/*" | xargs yamllint',
        fine_if_command_not_found=True,
        shell=True,
    )
    if CMD_NOT_FOUND_MSG in lint.out:
        return {}
    ret = 0
    out = lint.out.rstrip()
    if out:
        sys.stdout.write(lint.out)
        ret = len([line for line in out.split('\n') if ':' in line])
    return {
        'yamllint': ret
    }


@step
def backend_no_git():
    i = run('isort -c -rc backend *.py', shell=True)
    sys.stdout.write(i.out)
    f = run('flake8 backend *.py', shell=True)
    sys.stdout.write(f.out)
    return {
        'isort': len(i.out.rstrip().split('\n')) if i.rc else i.rc,
        'flake8': len(f.out.rstrip().split('\n')) if f.rc else f.rc,
    }


def validate_branch(branch_name_) -> Optional[Match]:
    return re.match(valid_branch_name, branch_name_)


prod = [line.rstrip() for line in open('backend/requirements.txt').readlines() if not line.startswith('#')]
dev = [line.rstrip() for line in open('backend/requirements_dev.txt').readlines() if not line.startswith('#')]


INVALID_PATTERNS = re.compile(
    '\n([^#].*'
    '('
    '<<<<<<< '  # noqa
    '|======= '  # noqa
    '|=======\n'
    '|>>>>>>> '  # noqa
    '|[\n ]print\('
    '|dupa'  # noqa
    '|#, fuzzy'  # noqa
    '|console.log'  # noqa
    ').*'
    ')'
)


@step
def detect_invalid_patterns(modified_files):
    debug('modified_files', modified_files)
    count = 0

    for filename in modified_files:
        if is_binary(filename):
            continue
        with open(filename, 'r', encoding='utf8') as inputfile:
            read = inputfile.read()
            for m in INVALID_PATTERNS.finditer(read):
                line, pattern = m.groups()
                if '# noqa' in line:
                    continue
                count += 1
                line_no = read[:m.start()].count('\n') + 2
                sys.stdout.write('%s:%s :\n' % (filename, line_no))
                sys.stdout.write(f'\033[0;33m{pattern}\033[0m'.join(line.split(pattern)).replace('\n', '') + '\n')
    return {'invalid_patterns': count}


@step
def requirements_are_sorted():
    # maybe let's not do this
    return {
        'requirements_sorted_prod': int(not prod == sorted(prod, key=lambda s: s.lower())),
        'requirements_sorted_dev': int(not dev == sorted(dev, key=lambda s: s.lower()))
    }


@step
def requirements_are_pinned():
    prod_not_pinned = [l for l in prod if not l.startswith('#') and '==' not in l and l]
    dev_not_pinned = [l for l in dev if not l.startswith('#') and '==' not in l and l]
    if prod_not_pinned:
        sys.stdout.write('prod_not_pinned %r\n' % prod_not_pinned)
    debug('prod_not_pinned', prod_not_pinned)
    debug('dev_not_pinned', dev_not_pinned)
    return {
        'requirements_pinned_prod': len(prod_not_pinned),
    }


@step
def find_markers():
    run(
        '''
        egrep -Irn \
        --exclude-dir=node_modules --exclude-dir=build --exclude-dir=.git --exclude-dir=.idea \
        --exclude-dir=dist \
        --exclude=\*pyc -e "TODO|HACK|EXPLAIN|REMOVE|THINK|@[A-Z][a-z]+: " |
        GREP_COLORS='mt=01;33' egrep --color=always "TODO|$" |
        GREP_COLORS='mt=01;31' egrep --color=always "HACK|$" |
        GREP_COLORS='mt=01;32' egrep --color=always "EXPLAIN|$" |
        GREP_COLORS='mt=01;34' egrep --color=always "REMOVE|$" |
        GREP_COLORS='mt=01;35' egrep --color=always "THINK|$" |
        GREP_COLORS='mt=01;36' egrep --color=always "@[A-Z][a-z]+: |$" |
        egrep -v "egrep|exclude|title\("
        ''',
        doprint=True,
        shell=True,
    )
    return {}


def hook():
    generic_debug_info()
    debug('all_files', all_files)
    run_backend_tests()
    backend_no_git()

    files = set(find_modified_files(True)) - EXCLUDED_FILES
    detect_invalid_patterns(files)
    requirements_are_pinned()
    find_markers()
    any_fails = sum(fails.values())
    if any_fails:
        colour('RED', pformat(fails))
    debug('fails', fails)
    return any_fails


parser = ArgumentParser()
parser.add_argument(
    '-a', '--all-files',
    help='Run on all files rather on git "Changes to be committed", the default.',
    action='store_true'
)
parser.add_argument(
    '-d', '--debug',
    action='store_true'
)
parser.add_argument(
    '-s', '--skip',
    help='Functions to skip',
    default=[],
    choices=step.collect
)
parser.add_argument(
    '-o', '--only',
    help='Only run these functions',
    default=[],
    choices=step.collect
)
args = parser.parse_args()
assert not all((args.only, args.skip)), '--skip and --only are mutually exclusive.'
if args.debug:
    DEBUG = True
debug('argparse', args)
all_files = args.all_files
skip = args.skip
only = args.only
set_logging()
sys.exit(hook())
