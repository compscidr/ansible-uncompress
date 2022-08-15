# ansible-uncompress
Uncompress module for ansible

Motivated by the push-back against .gz .bz2 not being supported for compressed
files: https://github.com/ansible/ansible-modules-core/issues/3241#issuecomment-240991265

and the existance of this project: https://github.com/vadikgo/uncompress.

Updating the existing project to support installation via a `meta/requirements.yml`
file and then submitting to ansible galaxy so that it can be found and installed
easily.


## installation of the role:
Until I figure out how to get it up on ansible galaxy:

Add the following to your `requirements.yml` file:
```
# from github
- src: https://github.com/compscidr/ansible-uncompress
  name: compscidr.uncompress
```
Then run
`ansible-galaxy install -r requirements.yml`

## example use:
```
---
- name: Install some gz file:
  hosts: all
  roles:
    - compscidr.uncompress
  tasks:
  - name: install cheat # https://github.com/cheat/cheat/blob/master/INSTALLING.md
    tags: cheat
    become: true
    uncompress:
      copy: no
      src: https://github.com/cheat/cheat/releases/download/4.3.1/cheat-linux-amd64.gz
      dest: /usr/local/bin/cheat
      mode: '755'
```
