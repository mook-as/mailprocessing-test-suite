# Docker file for the test suite
# Note that this is build relative to the repository root.
FROM opensuse/leap:latest

RUN zypper --non-interactive install dovecot postfix python3-pip python3-PyYAML
RUN echo 'home_mailbox = Maildir/' >> /etc/postfix/main.cf
RUN echo 'mail_location = maildir:~/Maildir' >> /etc/dovecot/conf.d/10-mail.conf
RUN echo '!include auth-postfix.conf.ext' >> /etc/dovecot/conf.d/10-auth.conf
RUN echo '!include auth-static.conf.ext' >> /etc/dovecot/conf.d/10-auth.conf
RUN useradd --create-home user
RUN mkdir --parents /home/user/Maildir/tmp
RUN chown --recursive user:users /home/user/Maildir
RUN chmod --recursive ugo+rwx /home/user/Maildir

ADD image/auth-postfix.conf.ext image/auth-static.conf.ext /etc/dovecot/conf.d/
ADD image/entrypoint.py /
ADD tests /tests
ADD mail /mail

ENTRYPOINT ["python3", "/entrypoint.py"]
