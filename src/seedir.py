# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:34:12 2020

@author: earne
"""

import os
import re

import natsort

from errors import SeedirError
import printing

def count_files(paths):
    files = sum([os.path.isfile(p) for p in paths])
    return files

def count_folders(paths):
    folders = sum([os.path.isdir(p) for p in paths])
    return folders

def beyond_depth_str(beyond, paths=None):
    if beyond == 'ellipsis':
        return '...'
    elif beyond in ['contents','content']:
        folders = count_folders(paths)
        files = count_files(paths)
        return '{} folder(s), {} file(s)'.format(folders, files)
    elif beyond and beyond[0] == '_':
        return beyond[1:]
    else:
        s1 = '"beyond" must be "ellipsis", "content", or '
        s2 = 'a string starting with "_"'
        raise SeedirError(s1 + s2)

def sort_dir(root, paths, first=None, sort_reverse=False, sort_key=None):
    if first in ['folders', 'files']:
        folders = [p for p in paths if
                   os.path.isdir(os.path.join(root, p))]
        files = [p for p in paths if not
                 os.path.isdir(os.path.join(root, p))]
        folders = natsort.natsorted(folders, reverse=sort_reverse, key=sort_key)
        files = natsort.natsorted(files, reverse=sort_reverse, key=sort_key)
        return folders + files if first == 'folders' else files + folders
    else:
        return natsort.natsorted(paths, reverse=sort_reverse, key=sort_key)

def get_base_header(incomplete, extend, space):
    base_header = []
    max_i = max(incomplete)
    for p in range(max_i):
        if p in incomplete:
            base_header.append(extend)
        else:
            base_header.append(space)
    return "".join(base_header)

def recursive_folder_structure(path, depth=0, incomplete=None, split='├─',
                                extend='│ ', space='  ', final='└─',
                                filestart='', folderstart='', depthlimit=None,
                                itemlimit=None, beyond=None, first=None,
                                sort=True, sort_reverse=False, sort_key=None,
                                include_folders=None, exclude_folders=None,
                                include_files=None, exclude_files=None,
                                regex=True):
    output = ''
    if incomplete is None:
        incomplete = []
    if depth == 0:
        output += folderstart + os.path.basename(path) + os.sep +'\n'
    if depth == depthlimit and beyond is None:
        return output
    listdir = os.listdir(path)
    incomplete.append(depth)
    depth += 1
    if depthlimit and depth == depthlimit + 1:
        paths = [os.path.join(path, item) for item in listdir]
        extra = beyond_depth_str(beyond, paths)
        if beyond is not None and extra:
            base_header = get_base_header(incomplete, extend, space)
            output += base_header + final + extra + '\n'
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
        incomplete = [n for n in incomplete if n < depth]
        return output
    if sort or first is not None:
        listdir = sort_dir(path, listdir, first=first,
                            sort_reverse=sort_reverse, sort_key=sort_key)
    if any(isinstance(i, str) for i in [
            include_folders,
            exclude_folders,
            include_files,
            exclude_files]):
        keep = []
        for l in listdir:
            sub = os.path.join(path, l)
            if os.path.isdir(sub):
                if isinstance(include_folders, str):
                    if not printing.is_match(include_folders, l, regex):
                        continue
                if isinstance(exclude_folders, str):
                    if printing.is_match(exclude_folders, l, regex):
                        continue
            else:
                if isinstance(include_files, str):
                    if not printing.is_match(include_files, l, regex):
                        continue
                if isinstance(exclude_files, str):
                    if printing.is_match(exclude_files, l, regex):
                        continue
            keep.append(l)
        listdir = keep
    if not listdir:
        if depth - 1 in incomplete:
            incomplete.remove(depth-1)
    for i, f in enumerate(listdir):
        sub = os.path.join(path, f)
        base_header = get_base_header(incomplete, extend, space)
        if i == len(listdir) - 1:
            branch = final
            incomplete.remove(depth-1)
            incomplete = [n for n in incomplete if n < depth]
        elif itemlimit and i == itemlimit - 1 and beyond is None:
            branch = final
        else:
            branch = split
        header = base_header + branch
        if i == itemlimit:
            paths = [os.path.join(path, rem) for rem in listdir[i:]]
            if beyond is not None:
                extra = beyond_depth_str(beyond, paths)
                output += base_header + final + extra + '\n'
            return output
        if os.path.isdir(sub):
            output += header + folderstart + f + os.sep +'\n'
            output += recursive_folder_structure(sub, depth=depth,
                                                 incomplete=incomplete,
                                                 split=split, extend=extend,
                                                 space=space,
                                                 final=final,
                                                 filestart=filestart,
                                                 folderstart=folderstart,
                                                 depthlimit=depthlimit,
                                                 itemlimit=itemlimit,
                                                 beyond=beyond,
                                                 first=first,
                                                 sort_reverse=sort_reverse,
                                                 sort_key=sort_key,
                                                 include_folders=include_folders,
                                                 exclude_folders=exclude_folders,
                                                 include_files=include_files,
                                                 exclude_files=exclude_files,
                                                 regex=regex)
        else:
            output += header + filestart + f + '\n'
    return output

def seedir(path, style='lines', indent=2, uniform='', depthlimit=None,
           itemlimit=None, beyond=None, first=None, sort=True,
           sort_reverse=False, sort_key=None, include_folders=None,
           exclude_folders=None, include_files=None,
           exclude_files=None, regex=True, **kwargs):
    if style:
        styleargs = printing.get_styleargs(style)
    styleargs = printing.format_indent(styleargs, indent=indent)
    if uniform:
        for arg in ['extend', 'split', 'final', 'space']:
            styleargs[arg] = uniform
    for k in kwargs:
        if k in styleargs:
            styleargs[k] = kwargs[k]
    if sort_key is not None or sort_reverse == True:
        sort = True
    return recursive_folder_structure(path,
                                      depthlimit=depthlimit,
                                      itemlimit=itemlimit,
                                      beyond=beyond,
                                      first=first,
                                      sort=sort,
                                      sort_reverse=sort_reverse,
                                      sort_key=sort_key,
                                      include_folders=include_folders,
                                      exclude_folders=exclude_folders,
                                      include_files=include_files,
                                      exclude_files=exclude_files,
                                      regex=regex,
                                      **styleargs)
