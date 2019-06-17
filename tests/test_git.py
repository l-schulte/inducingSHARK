#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import tempfile
import os
import math
import logging
import sys
import pprint

from datetime import datetime

from inducingSHARK.util.git import CollectGit

logger = logging.getLogger()
logger.level = logging.DEBUG


class TestGit(unittest.TestCase):

    def test_bug_introducing_comment(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = subprocess.run(['/bin/bash', './tests/scripts/repo_bug_introducing_comment.sh', '{}'.format(tmpdirname)], stdout=subprocess.PIPE)
            self.assertEqual(r.returncode, 0)

            # read git information
            cg = CollectGit(tmpdirname)
            cg.collect()

            c = subprocess.run(['git', 'log', '--pretty=tformat:"%H %ci"'], cwd=tmpdirname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(c.returncode, 0)
            lines = c.stdout.decode('utf-8').split('\n')

            # last is top
            last = lines[0].split(' ')[0].replace('"', '')
            first = lines[-2].split(' ')[0].replace('"', '')  # last is \n therefore we want the second from last in the output

            # pprint.pprint(lines)

            commits = cg.blame(last, 'test2.py')

            # we get the old name
            second = (lines[-3].split(' ')[0].replace('"', ''), 'test2.py')

            self.assertEqual(len(commits), 1)  # we can only find one because we ignore the change of the comment
            self.assertEqual(commits[0], second)  # the middle commit introduced the bug

    def test_bug_introducing_rename(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = subprocess.run(['/bin/bash', './tests/scripts/repo_bug_introducing_rename.sh', '{}'.format(tmpdirname)], stdout=subprocess.PIPE)
            self.assertEqual(r.returncode, 0)

            # read git information
            cg = CollectGit(tmpdirname)
            cg.collect()

            c = subprocess.run(['git', 'log', '--pretty=tformat:"%H %ci"'], cwd=tmpdirname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(c.returncode, 0)
            lines = c.stdout.decode('utf-8').split('\n')

            # last is top
            last = lines[0].split(' ')[0].replace('"', '')
            first = lines[-2].split(' ')[0].replace('"', '')  # last is \n therefore we want the second from last in the output

            commits = cg.blame(last, 'test1.py')

            # we get the old name
            second = (lines[-3].split(' ')[0].replace('"', ''), 'test2.py')

            self.assertEqual(len(commits), 1)  # we can only find one
            self.assertEqual(commits[0], second)  # the middle commit introduced the bug

    def test_bug_introducing_simple2(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = subprocess.run(['/bin/bash', './tests/scripts/repo_bug_introducing_simple2.sh', '{}'.format(tmpdirname)], stdout=subprocess.PIPE)
            self.assertEqual(r.returncode, 0)

            # read git information
            cg = CollectGit(tmpdirname)
            cg.collect()

            c = subprocess.run(['git', 'log', '--pretty=tformat:"%H %ci"'], cwd=tmpdirname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(c.returncode, 0)
            lines = c.stdout.decode('utf-8').split('\n')

            # last is top
            last = lines[0].split(' ')[0].replace('"', '')
            first = (lines[-2].split(' ')[0].replace('"', ''), 'test1.py')  # last is \n therefore we want the second from last in the output

            changed_lines = cg._blame_lines(last, 'test1.py', 'code_only')
            commits = cg.blame(last, 'test1.py')

            self.assertEqual(changed_lines, [(1, 'dddd'), (2, 'bbbb'), (4, 'bbbb')])

            # change was on second commit and first commit, we sort because we convert it to a set in Git to make the list unique
            second = (lines[1].split(' ')[0].replace('"', ''), 'test1.py')
            self.assertEqual(sorted(commits), sorted([first, second]))

    def test_bug_introducing_simple(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            r = subprocess.run(['/bin/bash', './tests/scripts/repo_bug_introducing_simple.sh', '{}'.format(tmpdirname)], stdout=subprocess.PIPE)
            self.assertEqual(r.returncode, 0)

            # read git information
            cg = CollectGit(tmpdirname)
            cg.collect()

            c = subprocess.run(['git', 'log', '--pretty=tformat:"%H %ci"'], cwd=tmpdirname, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(c.returncode, 0)
            lines = c.stdout.decode('utf-8').split('\n')

            # last is top
            last = lines[0].split(' ')[0].replace('"', '')
            first = lines[-2].split(' ')[0].replace('"', '')  # last is \n therefore we want the second from last in the output

            commits = cg.blame(last, 'test2.py')

            self.assertEqual(len(commits), 1)  # we can only find one
            self.assertTrue(commits[0] not in [last, first])  # the middle commit introduced the bug
