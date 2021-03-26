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
directory, all files with names starting with `mail` are first inserted into the
mailbox (by actually mailing to `root@localhost`).  There must also be a
`config.yaml` file to describe the test case.  It is expected to have the
following top-level keys:

### `folders`

This is an optional key; if it exists, the values is a list of folders that must
be created before running the test case.  This is required as `mailprocessing`
currently does not create folders before moving.

### `scripts`

A mapping containing the following:

Key | Optional | Description
--- | --- | ---
`script` | Required | The literal script to run.
`folder` | Optional | The folder to run the script in; defaults to the root.

### `expected`

A mapping describing the expected final state.  Each key is an expected folder,
which in turns contains a mapping describing the messages in that folder.  The
messages use their `Message-Id` header as the key, and the value is the flags
(as expected by maildir).

### Sample test configuration:
```yaml
expected:
  new: # The top level directory
    some-message-id: S # This message should be marked as Seen
  deeply/nested/subfolder/cur:
    another-message-id: "" # no flags
scripts:
- script: |-
    for mail in processor:
      pass
folders:
  - parent
  - parent/child
```
