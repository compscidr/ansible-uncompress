# Changelog

## 0.0.8 (2026-01-07)
- Added support for `dest` parameter to accept a directory path, automatically deriving the uncompressed filename from the source file (similar to `ansible.builtin.copy`)
- Strips compression extensions (.gz, .bz2, .xz, .lzma) and replaces .txz/.tlz with .tar
- Handles URLs with query parameters correctly when deriving filenames

## 0.0.7 (2026-01-07)
- Added `dest` as a return value to make it easier to reference the uncompressed file path in subsequent tasks (similar to `ansible.builtin.copy`)

## Previous versions
- switched to a collection instead of a module