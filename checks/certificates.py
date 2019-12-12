#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import re
import ssl
import subprocess
import tempfile

spaces = re.compile(r'\s+')

beg = re.compile('BEGIN CERTIFICATE')
end = re.compile('END CERTIFICATE')


def get_certificate(base_url, logger, port=443):
    ret = {'url': base_url, 'cert': '', 'status': False, 'days_left': 0}

    try:

        r = subprocess.Popen('timeout 2 openssl s_client -connect %s:%i' % (
            base_url, port), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        temp = r.communicate()[0].decode()
        cert = []
        logger.debug('Successfully retrieved certificate from %s' % base_url)
        found = False

        for line in temp.split('\n'):
            if beg.search(line):
                found = True
            if end.search(line):
                cert.append(line)
                found = False
            if found:
                cert.append(line)
            c = '\n'.join(cert)

        ret['cert'] = c
        ret['status'] = True
        logger.debug('Cert is : %s' % c)

        return ret

    except:

        logger.error('Failed to retrieve certificate from %s.' %
                     base_url, exc_info=True)
        return ret


def check_expiry(data, logger):
    try:

        # Append certificate in a NamedTemporaryFile to use ssl lib to extract info

        t = tempfile.NamedTemporaryFile(delete=False, suffix='.pem')
        t.write(data['cert'].encode())
        t.close()
        cert_dict = ssl._ssl._test_decode_cert(t.name)


        d = cert_dict['notAfter']
        d = re.sub(spaces, ':', d)

        fmt = "%b:%d:%H:%M:%S:%Y:%Z"
        logger.debug('Non formatted retrieved date is %s' % str(d))
        date_ob = datetime.datetime.strptime(d, fmt)
        today = datetime.datetime.today()
        logger.debug('Observed date is %s' % str(date_ob))

        diff = date_ob - today
        data['days_left'] = diff.days
        logger.debug('Observed days left is %s' % str(data['days_left']))

        return data

    except:

        data['status'] = False
        logger.error('Failed to retrieve date from certificate', exc_info=True)

        return data
