#!/usr/bin/env python3

# Email finder using Python
# (1) Create list of possible addresses given name and domain
# (2) Verify whether email addresses exist
# (3) Return valid addresses

import re
import sys
import socket
import smtplib
import pyperclip
import dns.resolver
import json

# Regex for names
name_regex = re.compile(r'([a-zA-Z])')

# Regex for domain
domain_regex = re.compile(r'''(
[a-zA-Z0-9.-]+         # second-level domain
(\.[a-zA-Z]{2,})       # top-level domain
)''', re.VERBOSE)

def formats(first, last, domain):
    """
    Create a list of 20 possible email formats combining:
    - First name:          [empty] | Full | Initial |
    - Delimitator:         [empty] |   .  |    _    |    -
    - Last name:           [empty] | Full | Initial |
    """
    list = []

    list.append(first[0] + '@' + domain)                 # f@example.com
    list.append(first[0] + last + '@' + domain)          # flast@example.com
    list.append(first[0] + '.' + last + '@' + domain)    # f.last@example.com
    list.append(first[0] + '_' + last + '@' + domain)    # f_last@example.com
    list.append(first[0] + '-' + last + '@' + domain)    # f-last@example.com
    list.append(first + '@' + domain)                    # first@example.com
    list.append(first + last + '@' + domain)             # firstlast@example.com
    list.append(first + '.' + last + '@' + domain)       # first.last@example.com
    list.append(first + '_' + last + '@' + domain)       # first_last@example.com
    list.append(first + '-' + last + '@' + domain)       # first-last@example.com
    list.append(first[0] + last[0] + '@' + domain)       # fl@example.com
    list.append(first[0] + '.' + last[0] + '@' + domain) # f.l@example.com
    list.append(first[0] + '-' + last[0] + '@' + domain) # f_l@example.com
    list.append(first[0] + '-' + last[0] + '@' + domain) # f-l@example.com
    list.append(first + last[0] + '@' + domain)          # fistl@example.com
    list.append(first + '.' + last[0] + '@' + domain)    # first.l@example.com
    list.append(first + '_' + last[0] + '@' + domain)    # fist_l@example.com
    list.append(first + '-' + last[0] + '@' + domain)    # fist-l@example.com
    list.append(last + '@' + domain)                     # last@example.com
    list.append(last[0] + '@' + domain)                  # l@example.com

    return(list)

def verify(list, domain):
    """
    Create a list of all valid addresses out of a list of emails.
    """

    valid = []
    for email in list:
        try:
            records = dns.resolver.resolve(domain, 'MX')
            print('DNS query performed successfully.', json.dumps(str(records)))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            print('DNS query could not be performed.')
            print('DNS query could not be performed.')
            quit()

        # Get MX record for the domain
        mx_record = records[0].exchange
        mx = str(mx_record)

        # Get local server hostname
        local_host = socket.gethostname()

        # Connect to SMTP
        smtp_server = smtplib.SMTP()
        smtp_server.connect(mx)
        smtp_server.helo(local_host)
        smtp_server.mail(email)
        code, message = smtp_server.rcpt(email)
        print('SMTP response code:', code)
        print('SMTP response message:', message)
        print('SMTP response for email:', email)

        try:
            smtp_server.quit()
        except smtplib.SMTPServerDisconnected:
            print('Server disconnected. Verification could not be performed.')
            quit()

        # Add to valid addresses list if SMTP response is positive
        if code == 250:
            valid.append(email)
        else:
            continue

    return(valid)

def return_valid():
    """
    Return final output comparing list of valid addresses to the possible ones:
    1. No valid  > Return message
    2. One valid > Copy to clipboard
    3. All valid > Catch-all server
    4. Multiple  > List addresses
    """
    first_name = 'jaanbaaz'
    last_name = 'akhtar'
    domain_name = 'taazaa.com' # Example name, can be replaced with actual first and last names

    if not re.match(name_regex, first_name):
        print('%s is not a valid first name.' % first_name)
        return []
    if not re.match(name_regex, last_name):
        print('%s is not a valid last name.' % last_name)
        return []
    if not re.match(domain_regex, domain_name):
        print('%s is not a valid domain name.' % domain_name)
        return []

    emails_list = formats(first_name, last_name, domain_name)
    print('Possible email addresses:', emails_list)
    valid_list = verify(emails_list, domain_name)
    return valid_list

