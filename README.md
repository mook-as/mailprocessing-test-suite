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
`expected.yaml` | Expected output; see below.

The file `expected.yaml` should describe the desired state after processing.  It
is a dictionary keyed by (flattened) folders, each containing messages keyed by
the `Message-Id` header, and maildir-style flags as the value.

```yaml
new: # The top level directory
    some-message-id: S
deeply/nested/subfolder/cur:
    another-message-id: "" # no flags
```
