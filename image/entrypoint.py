#!/usr/bin/env python3

import contextlib
import email
import email.policy
import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


class MailProcessingTestCase(unittest.TestCase):
    def __init__(self, dir):
        super(MailProcessingTestCase, self).__init__("test_item")
        self.dir = dir

    def setUp(self):
        try:
            shutil.rmtree("/root/Maildir")
        except FileNotFoundError:
            pass
        subprocess.run(["postfix", "start"], check=True)
        subprocess.run(["dovecot"], check=True)

        with open(os.path.join(self.dir.path, "config.yaml")) as input:
            self.config = yaml.load(input, Loader=yaml.SafeLoader)

        self.send_mail()

    def tearDown(self):
        subprocess.run(["dovecot", "stop"])
        subprocess.run(["postfix", "stop"])
        try:
            shutil.rmtree("/root/Maildir")
        except FileNotFoundError:
            pass

    def send_mail(self):
        files = os.scandir(self.dir)
        for file in files:
            if file.name.startswith("mail"):
                with open(file.path) as input:
                    subprocess.run(["sendmail", "-t"], stdin=input, check=True)

    def test_item(self):
        # Run the mailprocessing script
        args = [
            "--once",
            "--maildir-base=/root/Maildir",
            "--logfile={0}".format(os.path.join(self.dir.path,
                                   "maildirproc.log")),
            "--log-level=99",
            "--folder-separator=/",
        ]

        if "folders" in self.config:
            for folder in self.config["folders"]:
                for child in ["cur", "new", "tmp"]:
                    os.makedirs(
                        os.path.join("/root/Maildir", folder, child),
                        exist_ok=True)

        for script in self.config["scripts"]:
            script_args = args.copy()
            if "folder" in script:
                script_args.append(
                    "--maildir={0}".format(script["folder"]))
            else:
                script_args.append("--maildir=.")
            with contextlib.ExitStack() as context_stack:
                script_file = tempfile.NamedTemporaryFile("w")
                context_stack.push(script_file)
                script_file.writelines(script["script"].split("\n"))
                script_file.flush()
                script_args.append("--rcfile={0}".format(script_file.name))

                log_file = tempfile.NamedTemporaryFile("w+")
                context_stack.push(log_file)
                try:
                    subprocess.run(["maildirproc"] + script_args, check=True,
                                   stdout=log_file, stderr=subprocess.STDOUT)
                except:
                    log_file.seek(0, os.SEEK_SET)
                    sys.stderr.writelines(log_file.readlines())
                    raise
        actual = {}
        for dirpath, dirnames, filenames in os.walk("/root/Maildir"):
            relpath = os.path.relpath(dirpath, "/root/Maildir")
            if len(filenames) < 1:
                continue
            actual[relpath] = dict()
            for filename in filenames:
                with open(os.path.join(dirpath, filename)) as mail_file:
                    mail = email.message_from_file(
                        mail_file, policy=email.policy.default)
                flags = ""
                _, sep, end = filename.rpartition(":2,")
                if sep == ":2,":
                    flags = end
                actual[relpath][mail["Message-ID"]] = flags
                self.assertEqual(self.config["expected"], actual,
                                 "Unexpected result in {0}".format(self.dir.name))


def main():
    # Install mailprocessing
    try:
        os.stat("/src/setup.py")
    except FileNotFoundError:
        subprocess.run(["pip", "install", "mailprocessing"], check=True)
    else:
        subprocess.run(["/src/setup.py", "install", "--verbose"])

    suite = unittest.TestSuite()
    for dir in os.scandir("/tests"):
        suite.addTest(MailProcessingTestCase(dir))
    result = unittest.TextTestRunner(buffer=True).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
