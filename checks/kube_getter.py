#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

import requests

f = open("/run/secrets/kubernetes.io/serviceaccount/token")
t = f.readline()
t = t.replace('\n', '')
nodes_route = "/api/v1/nodes"
componentstatuses_route = "/api/v1/componentstatuses"
endpoints_route = "/api/v1/endpoints"
# will be kubernetes.default.svc.k8
api_server = 'kubernetes.default.svc.k8:443'
####
headers = {"Authorization": "Bearer %s" %
           t, 'Content-Type': 'application/json'}
###


def dump_route(route, logger):
    try:
        r = requests.get('https://%s%s' % (api_server, route),
                         verify=False, headers=headers)

        logger.debug('https://%s%s returned %s' %
                     (api_server, route, str(r.status_code)))

        return json.loads(r.content)

    except:
        logger.error('Failed to dump results from https://%s%s' %
                     (api_server, route))
        raise


def get_nodes(logger):
    nodes = dump_route(nodes_route, logger)
    nodes_ret = []

    for node in nodes['items']:
        nodes_ret.append(node['metadata']['name'])

    return nodes_ret


def get_api_servers(logger):

    api_servers = dump_route(endpoints_route, logger)
    api_ret = []

    for node in api_servers['items']:

        if node['metadata']['name'] == 'kubernetes':

            for ip in node['subsets'][0]['addresses']:
                api_ret.append(ip['ip'])

    return api_ret


def get_componentstatuses(logger):
    try:

        components_res = {}
        components = dump_route(componentstatuses_route, logger)

        for component in components['items']:
            if component['metadata']['name'] not in components_res:
                components_res[component['metadata']['name']
                               ] = component['conditions'][0]['type']
            else:
                logger.error('Component more than once: %s' %
                             component['metadata']['name'])
                pass

        return components_res

    except:
        logger.error('Failed to retrieve componentstatuses.', exc_info=True)
        return False


if __name__ == "__main__":
    import testing_logger_config
    logger = testing_logger_config.get_logger()
    base_url = 'kubernetes.default.svc.k8'
    logger.info('Starting test for %s...' % __file__)
    logger.debug(get_nodes(logger))
    logger.debug(get_componentstatuses(logger))
    logger.debug(get_api_servers(logger))
