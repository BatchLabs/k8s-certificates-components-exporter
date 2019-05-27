#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from prometheus_client import Gauge, start_http_server

from checks import certificates, kube_getter, logger_config

base_url = 'kubernetes.default.svc.k8'

if __name__ == "__main__":

    start_http_server(port=7000, addr='0.0.0.0')
    certs_metrics = Gauge('kubernetes_ceritifiate_days_left',
                          'Days left before nodes/apiservers certificates will be invalid', ['node'])
    components_metrics = Gauge('kubernetes_components_statuses',
                               'This will be set to 0 if components are OK, and 1 if they are not.', ['component'])

    logger = logger_config.get_logger()

    while True:

        try:
            api_servers = kube_getter.get_api_servers(logger)
            logger.debug('APIservers Found: %s' % str(api_servers))

            for server in api_servers:
                
                api_server_cert_expiry = certificates.check_expiry(
                    certificates.get_certificate(server, logger, port=6443), logger)
                
                logger.debug('Apiserver replied: %s' % api_server_cert_expiry)
                
                if api_server_cert_expiry['status'] == True:
                    certs_metrics.labels(api_server_cert_expiry['url']).set(
                        api_server_cert_expiry['days_left'])

            components = kube_getter.get_componentstatuses(logger)
            logger.debug("Components call replied: %s" % components)

            for component, status in components.items():
                
                if status == 'Healthy':
                    components_metrics.labels(component).set(0)
                else:
                    components_metrics.labels(component).set(1)

            nodes = kube_getter.get_nodes(logger)
            for node in nodes:
                
                node_res = certificates.check_expiry(
                    certificates.get_certificate(node, logger, port=10250), logger)
                
                logger.debug('Node %s replied: %s' % (node, node_res))
                
                if node_res['status'] == True:
                    certs_metrics.labels(node_res['url']).set(
                        node_res['days_left'])

            try:

                ETCD = os.getenv('ETCD')

                if ETCD == None:
                    logger.debug(
                        'Avoid checking etcd nodes since environment var `ETCD` is not set.')

                else:
                    logger.debug('I will poll those etcd: %s.' % ETCD)

                    for etcd in ETCD.split(','):
                    
                        etcd_expiry = certificates.check_expiry(
                            certificates.get_certificate(etcd, logger, port=2379), logger)
                
                        logger.debug('Etcd node replied: %s' % etcd_expiry)
                    
                        if etcd_expiry['status'] == True:
                            certs_metrics.labels(etcd_expiry['url']+'_etcd').set(
                                etcd_expiry['days_left'])
            except:
                logger.error(
                    'Failed to retrieve ETCD certificates.', exc_info=True)

            time.sleep(900)

        except KeyboardInterrupt:
            logger.info('Quitting...')
            os._exit(0)
