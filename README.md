# mailprocessing-test-suite

This is a test suite for [mailprocessing], to ensure that it does the expected
thing and doesn't damage the mailbox.

[mailprocessing]: http://mailprocessing.github.io/mailprocessing/

## Design

The testing happens inside a docker container to ensure that we have consistent
results.  Within the container, we install dovecot (as an IMAP server) plus
postfix.  We can simply send mail to `user@localhost` within the container, do
any processing, and check that the results are as expected.

We install mailprocessing as a global python package.

## Configuration

- If a `/src/` is mounted, then it is expected to be the mailprocessing package
  to test.  Otherwise, it is installed from PyPI.
- Tests are in the `tests/` directory.
- Sample mail are in the `mail/` directory.

## Writing Tests

Each test lives in one `*.yaml` file within the `tests/` directory.  Each test
is expected to have the following top-level keys:

### `mail`

A sequence where each value is the file name in the `mail/` directory.  If this
key is missing, then `simple.txt` is sent by default.

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
(as expected by maildir).  Do not specify the `new/`, `cur/` etc. subdirectory
name in the key.

### Sample test configuration:
```yaml
mail:
- simple.txt  # This is the default; the `mail` key can be omitted in this case.
expected:
  .: # The top level directory
    some-message-id: S # This message should be marked as Seen
  .deeply.nested.subfolder:
    another-message-id: "" # no flags
scripts:
- script: |-
    for mail in processor:
      pass
```
