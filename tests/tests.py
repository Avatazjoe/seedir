# -*- coding: utf-8 -*-
"""
Unittests for seedir.

Run from PARENT directory on command line, i.e.:

seedir\  < here!
├─.git\
├─.gitignore
├─LICENSE
├─README.md
├─seedir\
├─seedirpackagetesting.py
├─stackoverflow.txt
└─tests\

With the command:
    python -m tests.tests

Test methods MUST start with "test"
"""
import os
import unittest

import seedir as sd
from seedir.seedir import get_base_header
from seedir.fakedir import (count_fakedirs,
                            count_fakefiles,
                            sort_fakedir)

example = """mypkg/
    __init__.py
    app.py
    view.py
    test/
        __init__.py
        test_app.py
        test_view.py"""

no_init = """mypkg/
    app.py
    view.py
    test/
        test_app.py
        test_view.py"""

example_with_comments="""mypkg/
    __init__.py #some comments
    app.py #####        more comments
    view.py #how about## this one
    test/
        __init__.py
        test_app.py
        test_view.py"""

try:
    testdir = os.path.join(os.environ['USERPROFILE'], 'Desktop')
except:
    try:
        testdir = os.environ['USERPROFILE']
    except:
        try:
            testdir = os.path.dirname(os.path.abspath(__file__))
        except:
            testdir = input('Cannot automatically find a directory for '
                            'testing seedir.seedir() - please enter a '
                            'path to test with depthlimit=1:\n')
            while not os.path.isdir(testdir):
                testdir = input('Not found, try again:\n')

class PrintSomeDirs(unittest.TestCase):
    print('\n--------------------'
          '\n\nTesting seedir.seedir() against {}:\n\n'
          '--------------------'
          '\n'.format(testdir))
    def test_a_print_userprofile(self):
        print('Basic seedir (depthlimit=2, itemlimit=10):\n')
        sd.seedir(testdir, depthlimit=2, itemlimit=10)

    def test_b_styles(self):
        print('\nDifferent Styles (depthlimit=1, itemlimit=5):')
        for style in sd.STYLE_DICT.keys():
            print('\n{}:\n'.format(style))
            sd.seedir(testdir, style=style, depthlimit=1, itemlimit=5)

    def test_c_custom_styles(self):
        print('\nCustom Styles (depthlimit=1, itemlimit=5):')
        sd.seedir(testdir, depthlimit=1, itemlimit=5, space='>>',
                  split='>>', extend='II', final='->',
                  folderstart='Folder: ', filestart='File: ')

    def test_d_indent(self):
        print('\nDifferent Indents (depthlimit=1, itemlimit=5):')
        for i in list(range(3)) + [8]:
            print('\nindent={}:\n'.format(str(i)))
            sd.seedir(testdir, depthlimit=1, itemlimit=5, indent=i)

    def test_e_beyond(self):
        print('\nItems Beyond Limit (depthlimit=1, itemlimit=1, beyond="content")')
        sd.seedir(testdir, itemlimit=1, beyond='content')

    def test_improper_kwargs(self):
        with self.assertRaises(sd.SeedirError):
            sd.seedir(testdir, spacing=False)

class TestSeedirStringFormatting(unittest.TestCase):
    def test_get_base_header(self):
        a = '| '
        b = '  '
        self.assertEqual('', get_base_header([0], a, b))
        self.assertEqual('| |   ', get_base_header([0, 1, 3], a, b))
        with self.assertRaises(ValueError):
            get_base_header([], a, b)

    def test_STYLE_DICT_members(self):
        keys = set(sd.STYLE_DICT.keys())
        self.assertEqual(keys, set(['lines', 'dash', 'spaces',
                                    'arrow', 'plus', 'emoji']))

    def test_get_style_args_all_accessible(self):
        styles = ['lines', 'dash', 'spaces',
                  'arrow', 'plus', 'emoji']
        for s in styles:
            d = sd.get_styleargs(s)
            self.assertTrue(isinstance(d, dict))
        with self.assertRaises(sd.SeedirError):
            d = sd.get_styleargs('missing_style')

    def test_get_style_args_deepcopy(self):
        x = sd.STYLE_DICT['lines']
        y = sd.get_styleargs('lines')
        self.assertTrue(x is not y)

    def test_format_indent(self):
        d = sd.get_styleargs('lines')
        f1 = sd.format_indent(d, indent=4)
        f2 = sd.format_indent(d, indent=1)
        chars = ['extend', 'space', 'split', 'final']
        self.assertTrue(all(len(f1[c])==4 for c in chars))
        self.assertTrue(all(len(f2[c])==1 for c in chars))

    def test_words_list(self):
        self.assertTrue(sd.words[0] == 'a')
        self.assertTrue(len(sd.words) == 25487)

class TestFakeDirReading(unittest.TestCase):
    def test_read_string(self):
        x = sd.fakedir_fromstring(example)
        self.assertTrue(isinstance(x, sd.FakeDir))

    def test_parse_comments(self):
        x = sd.fakedir_fromstring(example)
        y = sd.fakedir_fromstring(example_with_comments)
        z = sd.fakedir_fromstring(example_with_comments, parse_comments=False)
        self.assertEqual(x.get_child_names(), y.get_child_names())
        self.assertNotEqual(x.get_child_names(), z.get_child_names())

class TestFakeDir(unittest.TestCase):
    def test_count_fake_items(self):
        x = sd.fakedir_fromstring(example)
        self.assertEqual(count_fakedirs(x.listdir()), 1)
        self.assertEqual(count_fakefiles(x.listdir()), 3)

    def test_sort_fakedir(self):
        x = sd.fakedir_fromstring(example).listdir()
        sort = sort_fakedir(x, sort_reverse=True, sort_key=lambda x : x[1])
        sort = [f.name for f in sort]
        correct = ['app.py', 'view.py', 'test', '__init__.py']
        self.assertEqual(sort, correct)

    def test_exclude_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, exclude_files='.*\..*', regex=True)
        z = sd.fakedir_fromstring(y)
        self.assertEqual(set(z.get_child_names()), set(['test']))

    def test_include_files_and_reread(self):
        x = sd.fakedir_fromstring(example)
        y = x.seedir(printout=False, include_files=['app.py', 'view.py'],
                     regex=False)
        z = sd.fakedir_fromstring(y)
        self.assertEqual(set(z.get_child_names()),
                         set(['app.py', 'view.py', 'test', ]))

    def test_delete_string_names(self):
        x = sd.randomdir()
        x.delete(x.get_child_names())
        self.assertTrue(len(x.listdir()) == 0)

    def test_delete_objects(self):
        x = sd.randomdir()
        x.delete(x.listdir())
        self.assertTrue(len(x.listdir()) == 0)

    def test_set_parent(self):
        x = sd.fakedir_fromstring(example)
        x['test/test_app.py'].parent = x
        self.assertTrue('test_app.py' in x.get_child_names())

    def test_walk_apply(self):
        def add_0(f):
            f.name += ' 0'
        x = sd.fakedir_fromstring(example)
        x.walk_apply(add_0)
        for f in x.get_child_names():
            self.assertEqual(f[-1], '0')

    def test_depth_setting(self):
        x = sd.fakedir_fromstring(example)
        x['test'].create_folder('A')
        x['test/A'].create_folder('B')
        x['test/A/B'].create_file('boris.txt')
        self.assertEqual(x['test/A/B/boris.txt'].depth, 4)
        x['test/A/B/boris.txt'].parent = x
        self.assertEqual(x['boris.txt'].depth, 1)

    def test_randomdir_seed(self):
        x = sd.randomdir(seed=4.21)
        y = sd.randomdir(seed=4.21)
        self.assertEqual(x.get_child_names(), y.get_child_names())

    def test_populate_fakedir(self):
        x = sd.FakeDir('BORIS')
        self.assertFalse(x.get_child_names())
        sd.populate(x)
        self.assertTrue(x.get_child_names())

class TestMask(unittest.TestCase):
    def test_mask_no_folders_or_files(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False

        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=foo,)
        s = s.split('\n')
        self.assertEqual(len(s), 1)

    def test_mask_always_false(self):
        def bar(x):
            return False
        s = sd.seedir(testdir, printout=False, depthlimit=2, itemlimit=10, mask=bar)
        s = s.split('\n')
        self.assertEqual(len(s), 1)

    def test_mask_fakedir_fromstring(self):
        x = sd.fakedir_fromstring(example)
        s = x.seedir(printout=False, mask=lambda x : not x.name[0] == '_',
                     style='spaces', indent=4)
        self.assertEqual(no_init, s)

    def test_mask_fakedir(self):
        def foo(x):
            if os.path.isdir(x) or os.path.isfile(x):
                return False
        f = sd.fakedir(testdir, mask=foo)
        self.assertEqual(len(f.listdir()), 0)

if __name__ == '__main__':
    unittest.main()