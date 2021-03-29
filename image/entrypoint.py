#!/usr/bin/env python3

import contextlib
import email.parser
import email.policy
import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


class MaildirTestCase(unittest.TestCase):
    def __init__(self, test_file:str):
        test_name, _ = os.path.splitext(test_file)
        setattr(self, f"test_{test_name}", self.test_item)
        super(MaildirTestCase, self).__init__(f"test_{test_name}")
        self.test_name = test_name
        self.test_file = os.path.join("/tests", test_file)

    def setUp(self):
        try:
            shutil.rmtree("/home/user/Maildir/")
        except FileNotFoundError:
            pass
        subprocess.run(["postfix", "start"], check=True)
        subprocess.run(["dovecot"], check=True)

        with open(self.test_file) as input:
            self.config = yaml.load(input, Loader=yaml.SafeLoader)

        self.send_mail()

        self.log_file = tempfile.NamedTemporaryFile("w+",
                prefix=f"mailprocessing-test-{self.test_name}-",
                suffix=".log")

    def tearDown(self):
        subprocess.run(["dovecot", "stop"])
        subprocess.run(["postfix", "stop"])
        try:
            shutil.rmtree("/home/user/Maildir/")
        except FileNotFoundError:
            pass

        self.log_file.close()

    def send_mail(self):
        if "mail" in self.config:
            files = [os.path.join("/mail/", m) for m in self.config["mail"]]
        else:
            files = ["/mail/simple.txt"]
        for file in files:
            with open(file) as input:
                subprocess.run(["sendmail", "-t"], stdin=input, check=True)
        subprocess.run(["postfix", "flush"], check=True)

    def open_message(self, path:str):
        parser = email.parser.Parser(policy=email.policy.default)
        with open(path, encoding="latin1") as mail_file:
            return parser.parse(mail_file, headersonly=True)

    def check_result(self):
        actual = {}
        for dirpath, dirnames, filenames in os.walk("/home/user/Maildir"):
            relpath = os.path.relpath(dirpath, "/home/user/Maildir")
            actual[relpath] = dict()
            for dir in ["cur", "new"]:
                if not dir in dirnames:
                    continue
                for file in os.scandir(os.path.join(dirpath, dir)):
                    if not file.is_file():
                        continue
                    mail = self.open_message(file.path)
                    flags = ""
                    _, sep, end = file.name.rpartition(":2,")
                    if sep == ":2,":
                        flags = end
                    actual[relpath][mail["Message-ID"]] = flags
            if len(actual[relpath]) == 0:
                del actual[relpath]
        self.assertEqual(self.config["expected"], actual)

    def run_processor(self, index, script):
        args = [
            "maildirproc",
            "--once",
            "--maildir-base=/home/user/Maildir",
            "--logfile=-",
            "--log-level=99",
        ]
        if "folder" in script:
            args.append("--maildir={0}".format(script["folder"]))
        else:
            args.append("--maildir=.")
        with contextlib.ExitStack() as context_stack:
            script_file = tempfile.NamedTemporaryFile("w", 
                prefix=f"mailprocessing-test-{self.test_name}-",
                suffix=".py")
            context_stack.push(script_file)
            script_file.write(script["script"])
            script_file.flush()
            args.append("--rcfile={0}".format(script_file.name))

            self.log_file.write(f"==>  Running script #{index} with {args}\n")
            try:
                subprocess.run(args, check=True,
                               stdout=self.log_file, stderr=subprocess.STDOUT)
            except:
                self.log_file.seek(0, os.SEEK_SET)
                sys.stderr.writelines(self.log_file.readlines())
                raise

    def test_item(self):
        for index, script in enumerate(self.config["scripts"]):
            self.run_processor(index, script)

        try:
            self.check_result()
        except:
            self.log_file.seek(0, os.SEEK_SET)
            sys.stderr.writelines(self.log_file.readlines())
            raise


class IMAPTestCase(MaildirTestCase):
    def run_processor(self, index, script):
        with contextlib.ExitStack() as context_stack:
            args = [
                "imapproc",
                "--once",
                "--logfile=-",
                "--log-level=99",
                "--host=localhost",
                "--user=user",
                "--password=password",
                "--folder-separator=/",
            ]
            if "folder" in script:
                args.append(f"--folder=INBOX{script['folder']}")
            else:
                args.append("--folder=INBOX")
            cache_file = tempfile.NamedTemporaryFile("w",
                prefix=f"mailprocessing-cache-{self.test_name}-")
            context_stack.push(cache_file)
            args.append(f"--cache-file={cache_file.name}")
            script_file = tempfile.NamedTemporaryFile("w", 
                prefix=f"mailprocessing-test-{self.test_name}-",
                suffix=".py")
            context_stack.push(script_file)
            script_file.write(script["script"])
            script_file.flush()
            args.append("--rcfile={0}".format(script_file.name))

            self.log_file.write(f"==> Running script #{index} with {args}\n")
            try:
                subprocess.run(args, check=True,
                               stdout=self.log_file, stderr=subprocess.STDOUT)
            except:
                self.log_file.seek(0, os.SEEK_SET)
                sys.stderr.writelines(self.log_file.readlines())
                raise


def main():

    # Install mailprocessing
    try:
        os.stat("/src/setup.py")
    except FileNotFoundError:
        subprocess.run(["pip", "install", "mailprocessing"], check=True)
    else:
        # Assume that the source is read-only
        shutil.copytree("/src", "/build")
        subprocess.run(["./setup.py", "build"], check=True, cwd="/build")
        subprocess.run(["./setup.py", "install"], check=True, cwd="/build")

    suite = unittest.TestSuite()
    for test_name in os.listdir("/tests"):
        suite.addTest(MaildirTestCase(test_name))
        suite.addTest(IMAPTestCase(test_name))
    result = unittest.TextTestRunner(buffer=True).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
