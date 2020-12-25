#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-07-9
#

"""Benchmark the loading speed of Alfred-Workflow."""



import os
import subprocess
import sys
import time

mydir = os.path.abspath(os.path.dirname(__file__))
benchdir = os.path.join(mydir, 'benchmarks')
pydir = os.path.dirname(mydir)


def log(s, *args):
    """Simple logger."""
    if args:
        s = s % args
    print(s, file=sys.stderr)


class Table(object):
    """Generate a nicely-formatted plaintext table.

    Attributes:
        rows (list): Table data.
    """

    def __init__(self, titles=None):
        """Create a new table.

        Args:
            titles (list, optional): Sequence of column titles.
        """
        self.rows = []
        self._str_rows = []
        self._width = None
        if titles:
            self.add_row(titles, True)

    def add_row(self, row, title=False):
        """Add a new row to table.

        Args:
            row (iterable): Items for the row.
        """
        if self.width and len(row) != self.width:
            raise ValueError('Rows must have {} elements, not {}'.format(
                             self.width, len(row)))

        row = [title] + list(row)
        self.rows.append(row)

    @property
    def colwidths(self):
        """Return widths of columns.

        Returns:
            list: `int` width of each column.
        """
        self.width
        return self._colwidths

    @property
    def width(self):
        """Required length of each row.

        Returns:
            int: Length of first row.
        """
        if self._width is None:

            if not self.rows:
                return None

            self._width = len(self.rows[0]) - 1
            self._colwidths = [0 for _ in range(self._width)]

        return self._width

    def row_to_str(self, row):
        """Convert each object in `row` to a `str`.

        Args:
            row (list): Various objects.

        Returns:
            str: UTF-8 encoded string.
        """
        is_title, data = row[0], row[1:]
        str_row = [is_title]

        for cell in data:
            if isinstance(cell, str):
                cell = cell.encode('utf-8')
            elif isinstance(cell, str):
                pass
            else:
                cell = repr(cell)

            str_row.append(cell)

        return str_row

    def __str__(self):
        """Return UTF-8 representation of data.

        Returns:
            str: UTF-8 string of tabular data.
        """
        widths = [0 for _ in range(self.width)]
        table = []
        for row in self.rows:
            row = self.row_to_str(row)
            for i, s in enumerate(row[1:]):
                j = len(s)
                if j > widths[i]:
                    widths[i] = j

            table.append(row)

        padded = []
        for row in table:
            is_title, cells = row[0], row[1:]
            newrow = [is_title]
            for i, s in enumerate(cells):
                f = b'{{:{}s}}'.format(widths[i])
                newrow.append(f.format(s))
            padded.append(newrow)

        hr = [b' '] + [(b'-' * (w+2)) for w in widths] + [b'']
        hr = b'+'.join(hr)
        text = [hr]
        for row in padded:
            is_title, cells = row[0], row[1:]
            text.append(b''.join([b' | ',
                                  b' | '.join(cells),
                                  b' | ']))
            if is_title:
                text.append(hr)

        text.append(hr)

        return b'\n'.join(text)


class Benchmark(object):
    """Run script and store results."""

    def __init__(self, name, cmd, cwd=None):
        """Create a new benchmark.

        Args:
            cmd (list): Passed as first argument to `subprocess.call()`.
            cwd (str, optional): Change to this directory before running
                the script.
        """
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.errors = []
        self.results = []

    def run(self, times=1):
        """Run `self.cmd` `times` times.

        Save duration of each run to `self.results` and any Exceptions
        to `self.errors`.

        """
        self.results = []
        self.errors = []
        # Add grandparent directory to PYTHONPATH, so scripts can see
        # workflow package
        env = {
            'HOME': os.getenv('HOME'),
            'PATH': '/bin:/usr/bin',
            'PYTHONPATH': pydir,
        }
        # env.update(os.environ)
        # env['PYTHONPATH'] = ':'.join([pydir,
        #                              env.get('PYTHONPATH', '')]).strip(':')

        # Run the benchmark
        print(self.name)
        wrote = False
        for i in range(times):
            if i % 5 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
                wrote = True

            start = time.time()
            try:
                with open(os.devnull, 'w') as devnull:
                    subprocess.check_call(self.cmd, cwd=self.cwd, env=env,
                                          stdout=devnull,
                                          stderr=subprocess.STDOUT,
                                          )
            except subprocess.CalledProcessError as err:
                log('[ERROR] cmd=%r, err=%r', self.cmd, err)
                self.errors.append(err)
            else:
                elapsed = time.time() - start
                self.results.append(elapsed)

        if wrote:
            print('')


def find_benchmarks(rootdir):
    """Return list of directories containing benchmarks."""
    benchmarks = []

    for n in os.listdir(rootdir):
        p = os.path.join(rootdir, n)

        if not os.path.isdir(p):
            continue

        sh = os.path.join(p, 'run.sh')
        if os.path.exists(sh):
            benchmarks.append(p)

    return benchmarks


def main():
    """Run benchmarks."""
    times = 50
    benchmarks = []
    dirs = find_benchmarks(benchdir)

    log('%d benchmark(s).', len(dirs))

    for p in dirs:
        b = Benchmark(os.path.basename(p), ['/bin/bash', 'run.sh'], p)
        benchmarks.append(b)
        errors = b.run(times)
        if errors:
            log('%d errors', len(errors))

    t = Table(['Name', 'Runs', 'Errors', 'Total', 'Average'])
    for b in benchmarks:
        errn = len(b.errors)
        runn = times - errn
        total = sum(b.results)
        av = 0.0
        if runn > 0:
            av = total / runn
        t.add_row([b.name, times, errn, '{:0.1f}s'.format(total),
                  '{:0.4f}s'.format(av)])

    print(t)

if __name__ == '__main__':
    main()
