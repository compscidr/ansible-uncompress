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

## example use in task file:
```yaml
---
- name: install cheat # https://github.com/cheat/cheat/blob/master/INSTALLING.md
  tags: cheat
  become: true
  compscidr.uncompress:
    copy: no
    src: https://github.com/cheat/cheat/releases/download/4.3.1/cheat-linux-amd64.gz
    dest: /usr/local/bin/cheat
    mode: '755'
```

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
- File permissions are set correctly
- Decompressed file contents are valid
- Operations are idempotent (running twice produces the same result)

### Deactivating the Virtual Environment

When done testing:
```bash
deactivate
```
