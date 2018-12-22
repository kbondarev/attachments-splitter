#!/usr/bin/env python3

###############################################################################
# DESCRIPTION:
###############################################################################
#
# This simple python script helps you to send multiple attachments via email.
# Most email servers have a restriction on the total size of the attachments
# accept. This script can split a folder full of files into multiple emails,
# while keeping in mind the max allowed size.
#
###############################################################################

import os
import glob
import smtplib
import sys
import getopt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def main():
    # Default option values
    host = input('Enter host [smtp.gmail.com]: ')
    if not host:
        host = 'smtp.gmail.com'  # Default to gmail

    port_str = input('Enter port [587]: ')
    port = 587
    if port_str:
        port = int(port_str)
    
    username = input('Enter username (e.g. michealscott@gmail.com): ')
    password = input('Enter password: ')
    from_address = input(f'Enter the \'from address\' [{username}]: ')
    if not from_address:
        from_address = username
    to_address = input('Enter the \'to address\': ')
    email_subject = input('Enter email subject: ')
    email_body = input('Enter the email message (optional): ')
    directory = input('Enter full path for directory containing the files: ')
    max_size_str = input('Enter max size of attachments per email (bytes): ')
    max_size = int(max_size_str)

    print(f"""\n
        host:\t{host}
        port:\t{port}
        user name:\t{username}
        password:\t{password}
        from:\t{from_address}
        to:\t{to_address}
        subject:\t{email_subject}
        message:\t{email_body}
        directory:\t{directory}
        max size:\t{max_size}
        \n""")

    confirm = input('Send emails using the info above? [y/N]: ')
    if confirm == 'y' or confirm == 'Y':
        grouped_attachments = split_files(directory, max_size)
        send_messages(host, port, username, password,
            from_address, to_address, email_subject,
            email_body, grouped_attachments)
    
    print('\nGoodbye!\n')


    
        

def split_files(directory, max_size):
    file_paths = glob.glob(f'{directory}/*')

    # The result is a 2D list, where the file paths are grouped by the max_size
    result = []

    # the inner list of result
    group = []

    group_size = 0
    for file_path in file_paths:
        file_size = os.path.getsize(file_path)
        
        if group_size + file_size < max_size:
            # The total size of files in the group will not reached the
            # max_size when this file is added, hence, add it to the group.
            group_size = group_size + file_size
            group.append(file_path)
        else:
            # The group has reached its max size limit.
            # Add the group to the result list and create new group
            if (len(group) > 0):
                result.append(group)
            else:
                print(f'WARNING! The file \'{file_path}\' will be ignored because \
                    its size ({file_size}) is larger than the max size ({max_size})!')
            group_size = 0
            group = []

    # Add the last group to the result list
    if (len(group) > 0):
        result.append(group)

    return result


def send_messages(host, port,
                  username, password,
                  from_address, to_address,
                  email_subject, email_body, email_messages):
    print(f'Connecting to host {host} (port {port})...')
    server = smtplib.SMTP(host, port)
    server.starttls()
    server.login(username, password)

    i = 1
    for msg in generate_messages(from_address, to_address,
                                 email_subject, email_body,
                                 email_messages):
        print(f'Sending email {i}/{len(email_messages)}\n')
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        i += 1
    
    server.quit()


def generate_messages(from_address, to_address,
                      email_subject, email_body,
                      email_messages):
    for i, message_attachments in enumerate(email_messages):
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = f'{email_subject} {i+1}/{len(email_messages)}'

        msg.attach(MIMEText(email_body, 'plain'))

        for part in generate_attachment_parts(message_attachments):
            msg.attach(part)     

        yield msg


def generate_attachment_parts(attachments_paths):
    for filepath in attachments_paths:
        (_filedir, filename) = os.path.split(filepath)
        file = open(filepath, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename={filename}')

        print(f'\t{filename}')
        yield part


if __name__ == '__main__':
    main()
