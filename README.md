# mailprocessing-test-suite

This is a test suite for [mailprocessing], to ensure that it does the expected
thing and doesn't damage the mailbox.

[mailprocessing]: http://mailprocessing.github.io/mailprocessing/

## Design

The testing happens inside a docker container to ensure that we have consistent
results.  Within the container, we install dovecot (as an IMAP server) plus
postfix.  We can simply send mail to `root@localhost` within the container, do
any processing, and check that the results are as expected.

We install mailprocessing as a global python package.

## Configuration

- If a `/src/` is mounted, then it is expected to be the mailprocessing package
  to test.  Otherwise, it is installed from PyPI.
- Tests are in the `tests/` directory.

## Writing Tests

Each subdirectory within the `tests/` directory is one test run.  Within that
should exist a few specific files:

File Name | Description
--- | ---
`rc` | The mailprocessing script to execute
`mail*` | Mail to process; they should contain all relevant headers.
`config.yaml` | Test configuration; see below.

The file `config.yaml` describes the test configuration; it must have a
`expected` child, describing the desired state after processing.  This is a
dictionary keyed by (flattened) folders, each containing messages keyed by
the `Message-Id` header, and maildir-style flags as the value.

The configuration may also have a `folders` key, providing a list of folders
that must be created before running the test.

Sample test configuration:
```yaml
expected:
  new: # The top level directory
    some-message-id: S
  deeply/nested/subfolder/cur:
    another-message-id: "" # no flags
folders:
  - parent
  - parent/child
```
