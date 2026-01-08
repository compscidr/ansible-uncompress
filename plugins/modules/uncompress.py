#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Jonathan Mainguy <jon@soh.re>
# (c) 2022, Jason Ernst <ernstjason1@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: uncompress
version_added: 2.4
short_description: Uncompresses an file after (optionally) copying it from the local machine.
extends_documentation_fragment: files
description:
     - Uncompresses an file. By default, it will copy the source file from the local system to the target before unpacking.
     - set copy=no to uncompress an file which already exists on the target.
options:
  src:
    description:
      - If copy=yes (default), local path to compressed file to copy to the target server; can be absolute or relative.
      - If copy=no, path on the target server to existing compressed file to unpack.
      - If copy=no and src contains ://, the remote machine will download the file from the url first.
    required: true
    default: null
  dest:
    description:
      - Remote absolute path where the file should be uncompressed.
      - If dest is an existing directory, the uncompressed filename will be derived from the source filename with compression extension removed.
      - If dest is a file path (or does not exist), it will be treated as the full file path including filename.
    required: true
    default: null
  copy:
    description:
      - "If true, the file is copied from local 'master' to the target machine, otherwise, the plugin will look for src file at the target machine."
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  deep_check:
    description:
      - "If true, and dest already exists, the file performs a longer and more extensive test than just filesize before deciding to overwrite or not"
    required: false
    choices: [ "yes", "no" ]
    default: "no"
author: "Jonathan Mainguy (@Jmainguy)"
notes:
    - requires C(file)/C(xz) commands on target host
    - requires gzip and bzip python modules
    - can handle I(gzip), I(bzip2) and I(xz) compressed files
    - detects type of compressed file automatically
'''


EXAMPLES = '''
# Explicit file path as dest (traditional usage)
- name: Uncompress foo.gz to /tmp/foo
  uncompress: src=foo.gz dest=/tmp/foo

- name: Uncompress a file that is already on the remote machine
  uncompress: src=/tmp/foo.xz dest=/usr/local/bin/foo copy=no

- name: Uncompress a file that needs to be downloaded
  uncompress: src=https://example.com/example.bz2 dest=/usr/local/bin/example copy=no

# Directory as dest (filename auto-derived from source)
- name: Uncompress to a directory (filename derived from source)
  uncompress: src=foo.gz dest=/tmp/
  # Results in /tmp/foo

- name: Uncompress downloaded file to directory
  uncompress: src=https://example.com/app.bz2 dest=/usr/local/bin/ copy=no
  # Results in /usr/local/bin/app

- name: Uncompress URL with query parameters to directory
  uncompress: src=https://example.com/download/file.gz?version=1.0&token=abc dest=/opt/myapp/ copy=no
  # Query parameters are stripped - results in /opt/myapp/file

- name: Uncompress tar.gz to directory (strips .gz, keeps .tar)
  uncompress: src=archive.tar.gz dest=/tmp/
  # Results in /tmp/archive.tar
'''


RETURN = '''
changed:
    description: Whether anything was changed
    returned: always
    type: boolean
    sample: True
dest:
    description: Destination file path of the uncompressed file
    returned: always
    type: string
    sample: /tmp/foo
'''

import os
import shutil
import gzip
import bz2
import filecmp
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


# When downloading an archive, how much of the archive to download before
# saving to a tempfile (64k)
BUFSIZE = 65536


def derive_uncompressed_filename(src):
    """
    Derive the uncompressed filename from a source path or URL.
    Strips compression extensions: .gz, .bz2, .xz, .lzma
    Replaces .txz/.tlz with .tar
    """
    # Extract filename from URL or path
    # Check for common URL schemes to avoid false positives with Windows paths like C:/path/file.gz
    if '://' in src and any(src.startswith(scheme + '://') for scheme in ['http', 'https', 'ftp', 'ftps', 'file']):
        # URL: extract path portion and get filename
        path_part = src.split('://', 1)[1]
        filename = path_part.rsplit('/', 1)[-1]
        # Strip query parameters
        filename = filename.split('?', 1)[0]
    else:
        # Local path: get basename
        filename = os.path.basename(src)

    # Strip compression extensions
    if filename.endswith('.gz'):
        return filename[:-3]
    elif filename.endswith('.bz2'):
        return filename[:-4]
    elif filename.endswith('.xz'):
        return filename[:-3]
    elif filename.endswith('.lzma'):
        return filename[:-5]
    elif filename.endswith('.txz'):
        return filename[:-4] + '.tar'
    elif filename.endswith('.tlz'):
        return filename[:-4] + '.tar'
    else:
        # No recognized compression extension, return as-is
        return filename


def ungzip(src, dest):
    """
    Uncompress gzip files.
    """
    try:
        with gzip.open(src, 'rb') as f_in:
            with open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        msg = ""
    except Exception as e:
        msg = "%s" % e

    return msg


def unbzip(src, dest):
    """
    Uncompress bzip files.
    """
    try:
        with bz2.BZ2File(src, 'rb') as f_in:
            with open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        msg = ""
    except Exception as e:
        msg = "%s" % e

    return msg


def unxzip(module, src, dest):
    """
    Uncompress xz files. Since we must support python 2.4 (EL 5) we cannot import lzma and use native python.
    We guess the filename of the output. .xz and .lzma get stripped, .txz and .lzma get replaced with .tar
    """
    cmd_path = module.get_bin_path('xz')
    cmd = '%s -k -d %s' % (cmd_path, src)
    # Guess filename of output
    prefix, suffix = os.path.splitext(src)
    if (suffix == '.xz') or (suffix == '.lzma'):
        ufile = prefix
    elif (suffix == '.txz') or (suffix == '.tlz'):
        ufile = prefix + '.tar'
    else:
        module.fail_json(msg="xz does not understand suffix %s" % suffix)
    try:
        module.run_command(cmd)
        if not os.path.isfile(ufile):
            module.fail_json(msg="%s should have uncompressed to %s, but alas it did not" % (src, ufile))
        shutil.move(ufile, dest)
        msg = ""
    except Exception as e:
        msg = "%s" % e

    return msg


def filetype(module, src):
    """
    Get the filetype from the unix command file, and then pick the correct compression method to use for it
    """
    cmd_path = module.get_bin_path('file')
    cmd = "%s -b -i %s" % (cmd_path, src)
    ftype = module.run_command(cmd)

    return ftype


def copyfile(src, dest, deep_check):
    """
    Copy file from tempsrc to final destination. Unless its already at dest, and the same as tempsrc.
    """
    changed = False
    if os.path.isfile(dest):
        # This takes a long time
        if deep_check:
            nodiff = filecmp.cmp(src, dest, shallow=True)
        # This is much quicker
        else:
            destsize = os.path.getsize(dest)
            srcsize = os.path.getsize(src)
            if destsize != srcsize:
                nodiff = False
            else:
                nodiff = True
        # If there is a difference, then we change the destination
        if nodiff is False:
            shutil.move(src, dest)
            changed = True
    # If the destination file does not exist, then place it.
    else:
        shutil.move(src, dest)
        changed = True

    return changed


def main():
    module = AnsibleModule(
        # not checking because of daisy chain to file module
        argument_spec=dict(
            src=dict(required=True),
            dest=dict(required=True),
            copy=dict(default=True, type='bool'),
            original_basename=dict(required=False),  # used to handle 'dest is a directory' via template, a slight hack
            deep_check=dict(default=False, type='bool'),  # This check takes a long time if dest already exists.
        ),
        add_file_common_args=True,
    )

    src = os.path.expanduser(module.params['src'])
    dest = os.path.expanduser(module.params['dest'])
    copy = module.params['copy']
    deep_check = module.params['deep_check']
    file_args = module.load_file_common_arguments(module.params)
    tempdir = "/tmp/"

    # If dest is an existing directory, derive the filename from src
    if os.path.isdir(dest):
        derived_filename = derive_uncompressed_filename(src)
        dest = os.path.join(dest, derived_filename)

    fdir, ffile = os.path.split(dest)

    # did tar file arrive?
    if not os.path.exists(src):
        if copy:
            module.fail_json(msg="Source '%s' failed to transfer" % src)
        # If copy=false, and src= contains ://, try and download the file to a temp directory.
        elif '://' in src:
            package = os.path.join(tempdir, str(src.rsplit('/', 1)[1]))
            try:
                rsp, info = fetch_url(module, src)
                status_code = info["status"]

                if status_code != 200:
                    module.fail_json(msg="Failure downloading %s, %s" % (src, status_code))

                f = open(package, 'wb')

                f.write(rsp.read())
                f.close()
                src = package
            except Exception as e:
                # f.close()
                module.fail_json(msg="Failure downloading %s, %s" % (src, e))
        else:
            module.fail_json(msg="Source '%s' does not exist" % src)

    # skip working with 0 size archives
    try:
        if os.path.getsize(src) == 0:
            module.fail_json(msg="Invalid archive '%s', the file is 0 bytes" % src)
    except Exception:
        module.fail_json(msg="Source '%s' not readable" % src)

    # is dest OK to receive tar file?
    if not os.path.isdir(fdir):
        module.fail_json(msg="Destination '%s' is not a directory" % dest)

    if not os.access(src, os.R_OK):
        module.fail_json(msg="Source '%s' not readable" % src)

    # Full path to the uncompressed file in the temp directory.
    tempsrc = os.path.join(tempdir, ffile)

    # Check what kind of compressed file the src is.
    ftype = filetype(module, src)[1]
    if "gzip" in ftype:
        msg = ungzip(src, tempsrc)
    elif "x-bzip2" in ftype:
        msg = unbzip(src, tempsrc)
    elif "x-xz" in ftype:
        msg = unxzip(module, src, tempsrc)
    else:
        module.fail_json(msg="Filetype not supported by uncompress module. %s" % ftype)
    if msg != "":
        module.fail_json(msg=msg)
    # If file already exists at dest, compare uncompressed file and dest, and replace if different.
    changed = copyfile(tempsrc, dest, deep_check)

    # do we need to change perms?
    file_args['path'] = dest
    try:
        changed = module.set_fs_attributes_if_different(file_args, changed)
    except (IOError, OSError) as e:
        module.fail_json(msg="Unexpected error when accessing exploded file: %s" % str(e))

    module.exit_json(changed=changed, dest=dest)

if __name__ == '__main__':
    main()
