# ansible-uncompress
[![Static Badge](https://img.shields.io/badge/Ansible_galaxy-Download-blue)](https://galaxy.ansible.com/ui/standalone/roles/compscidr/uncompress/)
[![ansible lint](https://github.com/compscidr/ansible-uncompress/actions/workflows/check.yml/badge.svg)](https://github.com/compscidr/ansible-uncompress/actions/workflows/check.yml)
[![ansible lint rules](https://img.shields.io/badge/Ansible--lint-rules%20table-blue.svg)](https://ansible.readthedocs.io/projects/lint/rules/)

Uncompress collection for ansible. Lets you download an uncompress .gz and .bz2 files
which currently isn't possible with the unarchive built-in module.
https://galaxy.ansible.com/ui/repo/published/compscidr/uncompress/

Motivated by the push-back against .gz .bz2 not being supported for compressed
files: https://github.com/ansible/ansible-modules-core/issues/3241#issuecomment-240991265

and the existance of this project: https://github.com/vadikgo/uncompress.

Updating the existing project to support installation via a `meta/requirements.yml`
file and then submitting to ansible galaxy so that it can be found and installed
easily.

## installation via galaxy:
`ansible-galaxy collection install compscidr.uncompress`

## installation via galaxy / requirements
Add the following to `requirements.yml`
```
collections:
- name: compscidr.uncompress
```
Then run
`ansible-galaxy install -r requirements.yml`

## installation via git / requirements
Add the following to your `requirements.yml` file:
```
collections:
  - name: git+https://github.com/compscidr/ansible-uncompress.git,main
```
Then run
`ansible-galaxy install -r requirements.yml`

## Why This Module Exists

Ansible's built-in `unarchive` module handles archives (like `.tar.gz`), but refuses to decompress plain compressed files (like `.gz` alone). This module fills that gap.

### What Each Module Can Do

**`ansible.builtin.unarchive` can:**
- ✅ `.tar.gz` - decompress and extract
- ✅ `.tar.bz2` - decompress and extract
- ✅ `.tar.xz` - decompress and extract
- ✅ `.zip` - extract
- ❌ `.gz` alone - won't handle (no archive inside)
- ❌ `.bz2` alone - won't handle (no archive inside)
- ❌ `.xz` alone - won't handle (no archive inside)

**`compscidr.uncompress` can:**
- ✅ `.gz` - decompress single files
- ✅ `.bz2` - decompress single files
- ✅ `.xz` - decompress single files
- ✅ `.lzma` - decompress single files
- ✅ `.tar.gz` - decompress to `.tar` (but not extract)
- ❌ Won't extract archives - use `unarchive` for that

### When to Use Which Module

**Use `compscidr.uncompress`** for:
- Single compressed files: `binary.gz`, `config.bz2`, `data.xz`
- When you need just the uncompressed file, not archive extraction
- Example: compressed executables, config files, data files

**Use `ansible.builtin.unarchive`** for:
- Archive files: `.tar.gz`, `.tar.bz2`, `.tar.xz`, `.zip`
- When you want to extract multiple files from an archive
- Example: application packages, source code archives

**Important:** This module handles **decompression** (removing compression like `.gz`), not **unarchiving** (extracting archive contents like `.tar`). If you uncompress `archive.tar.gz`, you'll get `archive.tar` - you'd still need to extract the tar archive separately (see examples below).

## Example Usage

### Traditional Usage (Explicit File Path)

Specify the exact destination file path:

```yaml
---
- name: Install cheat binary
  become: true
  compscidr.uncompress.uncompress:
    copy: false
    src: https://github.com/cheat/cheat/releases/download/4.3.1/cheat-linux-amd64.gz
    dest: /usr/local/bin/cheat
    mode: '755'

- name: Uncompress local file
  compscidr.uncompress.uncompress:
    src: /tmp/myfile.bz2
    dest: /opt/myapp/data.txt
    copy: true
```

### Directory Destination (Auto-Derived Filename)

New in v0.0.8: Specify a directory and let the module automatically derive the filename from the source:

```yaml
---
- name: Uncompress to directory (filename auto-derived)
  compscidr.uncompress.uncompress:
    src: foo.gz
    dest: /tmp/
  # Results in /tmp/foo

- name: Download and uncompress to directory
  compscidr.uncompress.uncompress:
    copy: false
    src: https://example.com/app.bz2
    dest: /usr/local/bin/
  # Results in /usr/local/bin/app

- name: Handle URLs with query parameters
  compscidr.uncompress.uncompress:
    copy: false
    src: https://example.com/file.gz?version=1.0&token=abc
    dest: /opt/myapp/
  # Query parameters are stripped - results in /opt/myapp/file

- name: Uncompress tar.gz (strips .gz, keeps .tar)
  compscidr.uncompress.uncompress:
    src: archive.tar.gz
    dest: /tmp/
  # Results in /tmp/archive.tar
```

### Registering Output

The module returns the destination path, making it easy to use in subsequent tasks:

```yaml
---
- name: Uncompress file to directory
  compscidr.uncompress.uncompress:
    src: myapp.gz
    dest: /opt/
  register: result

- name: Use the uncompressed file
  ansible.builtin.debug:
    msg: "File uncompressed to {{ result.dest }}"
  # Outputs: File uncompressed to /opt/myapp
```

### Working with .tar.gz Files

For `.tar.gz` files, you typically want both decompression AND extraction. Here are your options:

#### Option 1: Use ansible.builtin.unarchive (Recommended)

This is the simplest approach - `unarchive` handles both decompression and extraction in one step:

```yaml
---
- name: Download and extract tar.gz archive
  ansible.builtin.unarchive:
    src: https://example.com/myapp.tar.gz
    dest: /opt/myapp/
    remote_src: true
  # Automatically decompresses and extracts all files to /opt/myapp/
```

#### Option 2: Two-Pass Approach (Advanced)

If you need to decompress first and extract later (e.g., to inspect the tar file):

```yaml
---
- name: Step 1 - Uncompress .tar.gz to .tar
  compscidr.uncompress.uncompress:
    copy: false
    src: https://example.com/myapp.tar.gz
    dest: /tmp/
  register: uncompress_result
  # Results in /tmp/myapp.tar

- name: Step 2 - Extract the tar archive
  ansible.builtin.unarchive:
    src: "{{ uncompress_result.dest }}"
    dest: /opt/myapp/
    remote_src: true
  # Extracts all files from the tar to /opt/myapp/

- name: Step 3 - Clean up the intermediate tar file
  ansible.builtin.file:
    path: "{{ uncompress_result.dest }}"
    state: absent
```

**Note:** The two-pass approach is rarely needed. Use `ansible.builtin.unarchive` directly unless you have a specific reason to decompress and extract separately.

## Development and Testing

This collection uses [Molecule](https://molecule.readthedocs.io/) for testing with Docker containers across multiple Ubuntu versions (20.04, 22.04, and 24.04).

### Prerequisites

- Python 3.8 or later
- Docker (running daemon)
- Docker permissions for your user (or run tests as a user in the docker group)

### Setting Up the Test Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/compscidr/ansible-uncompress.git
   cd ansible-uncompress
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   # On Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install test dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install required Ansible collections:**
   ```bash
   ansible-galaxy collection install community.docker
   ```

### Running Tests

**Full test suite** (recommended for CI/CD):
```bash
molecule test
```

This runs the complete test sequence:
- Syntax validation
- Container creation
- Dependency installation
- Test playbook execution
- Idempotence check
- Verification tests
- Cleanup and destruction

**Development workflow** (faster iteration):
```bash
molecule create     # Create test containers
molecule converge   # Run the test playbook
molecule verify     # Run verification tests
molecule destroy    # Clean up containers
```

**Test a specific platform:**
```bash
molecule test --platform-name ubuntu-22.04
```

Available platforms: `ubuntu-20.04`, `ubuntu-22.04`, `ubuntu-24.04`

**Reset the test environment:**
```bash
molecule destroy    # Clean up existing containers
molecule reset      # Clear configuration
```

### What the Tests Cover

The molecule tests validate:
- Downloading and uncompressing remote `.gz` files
- Uncompressing local `.gz` files with `copy: true`
- Uncompressing `.bz2` files
- Uncompressing to directories with auto-derived filenames
- Handling `.tar.gz` files (strips `.gz`, keeps `.tar`)
- Correct `dest` return values for all scenarios
- File permissions are set correctly
- Decompressed file contents are valid
- Operations are idempotent (running twice produces the same result)

### Deactivating the Virtual Environment

When done testing:
```bash
deactivate
```
