# Docker file for the test suite
# Note that this is build relative to the repository root.
FROM opensuse/leap:latest

RUN zypper --non-interactive install dovecot postfix python3-pip python3-PyYAML
RUN echo 'home_mailbox = Maildir/' >> /etc/postfix/main.cf
RUN echo 'mail_location = maildir:~/Maildir' >> /etc/dovecot/conf.d/10-mail.conf
RUN echo '!include auth-postfix.conf.ext' >> /etc/dovecot/conf.d/10-auth.conf

ADD "image/auth-postfix.conf.ext" "/etc/dovecot/conf.d/"
ADD "image/entrypoint.py" "/"
ADD "tests" "/tests"

ENTRYPOINT ["python3", "/entrypoint.py"]
