# Changelog

## 0.0.10 (2026-08-23)
- Fixed `xz` files uncompressed into their own directory always reporting `changed: true` while never actually updating the destination (#28). `xz` is now decompressed with Python's `lzma` module instead of shelling out to the `xz` binary, which decompressed in place next to the source and whose failures were silently ignored
- Destination comparison now always compares file contents; a same-size but different-content file is no longer treated as unchanged. `deep_check` is accepted but ignored
- Temporary files now live in a per-invocation directory created with a random name and mode 0700, and are removed when the module exits (#29)
- The uncompressed file is now put in place with `atomic_move`
- Legacy `.lzma` files (reported by `file` as `application/x-lzma`) are now recognized; previously they failed with an unsupported filetype error despite the documented lzma support

## 0.0.9 (2026-03-10)
- Fixed a bug where uncompressing a file with no recognized compression extension into the same directory would silently overwrite the source file (#22)
- The module now fails with a clear error message when `src` and `dest` resolve to the same file path

## 0.0.8 (2026-01-07)
- Added support for `dest` parameter to accept a directory path, automatically deriving the uncompressed filename from the source file (similar to `ansible.builtin.copy`)
- Strips compression extensions (.gz, .bz2, .xz, .lzma) and replaces .txz/.tlz with .tar
- Handles URLs with query parameters correctly when deriving filenames

## 0.0.7 (2026-01-07)
- Added `dest` as a return value to make it easier to reference the uncompressed file path in subsequent tasks (similar to `ansible.builtin.copy`)

## Previous versions
- switched to a collection instead of a module