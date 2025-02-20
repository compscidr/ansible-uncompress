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
```
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
