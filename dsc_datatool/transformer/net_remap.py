"""
    dsc_datatool
    ~~~~~~~~~~~~

    DSC datatool

    :copyright: 2020 OARC, Inc.
"""

import ipaddress

from dsc_datatool import Transformer, args


class NetRemap(Transformer):
    v4net = None
    v6net = None

    def __init__(self, opts):
        net = opts.get('net', None)
        self.v4net = opts.get('v4net', net)
        self.v6net = opts.get('v6net', net)

        if not self.v4net:
            raise Exception('v4net (or net) must be given')
        if not self.v6net:
            raise Exception('v6net (or net) must be given')


    def _process(self, dimension):
        if not dimension.values:
            for d2 in dimension.dimensions:
                self._process(d2)
            return

        values = dimension.values
        dimension.values = {}

        for k, v in values.items():
            if k == args.skipped_key:
                continue
            elif k == args.skipped_sum_key:
                dimension.values['0'] = v
                continue

            ip = ipaddress.ip_address(k)
            if ip.version == 4:
                nkey = str(ipaddress.IPv4Network('%s/%s' % (ip, self.v4net), strict=False).network_address)
            else:
                nkey = str(ipaddress.IPv6Network('%s/%s' % (ip, self.v6net), strict=False).network_address)

            if not nkey in dimension.values:
                dimension.values[nkey] = v
            else:
                dimension.values[nkey] += v


    def process(self, datasets):
        for dataset in datasets:
            for dimension in dataset.dimensions:
                self._process(dimension)