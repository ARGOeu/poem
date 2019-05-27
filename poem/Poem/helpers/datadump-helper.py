#!/usr/bin/python3.6
import argparse
import json


def extract_data(data):
    data = data.copy()
    extracted_data = []
    reversion_data = []
    pks = []
    for item in data:
        if item['model'] == 'poem.probe':
            del item['fields']['group']
            item['model'] = 'poem_super_admin.probe'
            extracted_data.append(item)
        elif item['model'] == 'reversion.version':
            if item['fields']['content_type'] == ['poem', 'probe']:
                item['fields']['content_type'] = ['poem_super_admin', 'probe']
                ser_data = json.loads(item['fields']['serialized_data'])
                for d in ser_data:
                    if d['model'] == 'poem.probe':
                        d['model'] = 'poem_super_admin.probe'
                        d['fields']['user'] = 'poem'
                        del d['fields']['group']
                item['fields']['serialized_data'] = json.dumps(ser_data)
                pks.append(item['fields']['revision'])
            reversion_data.append(item)
        elif item['model'] == 'reversion.revision':
            reversion_data.append(item)

    for rev in reversion_data:
        if rev['model'] == 'reversion.version':
            if rev['fields']['content_type'] == ['poem_super_admin', 'probe']:
                extracted_data.append(rev)
        elif rev['model'] == 'reversion.revision':
            if rev['pk'] in pks:
                rev['fields']['user'] = ['poem']
                extracted_data.append(rev)

    for item in data:
        if item['model'] == 'poem.extrevision':
            item['model'] = 'poem_super_admin.extrevision'
            extracted_data.append(item)

    return extracted_data


def create_public_data(d1, d2, d3):
    # extract only data needed in public schema
    data1 = extract_data(d1.copy())
    data2 = extract_data(d2.copy())
    data3 = extract_data(d3.copy())

    names = set()
    probe_pk = 0
    extrev_pk = 0
    revision_pk = 0
    probepks = {}
    revisionpks = {}
    for item in data1:
        if item['model'] == 'poem_super_admin.probe':
            probe_pk += 1
            probepks.update({item['pk']: probe_pk})
            item['pk'] = probe_pk
            names.add(item['fields']['name'])
        if item['model'] == 'reversion.revision':
            revision_pk += 1
            revisionpks.update({item['pk']: revision_pk})
            item['pk'] = revision_pk

    version_pk = 0
    versionpks = {}
    # update reversion.version table
    for item in data1:
        if item['model'] == 'reversion.version':
            if item['fields']['content_type'] == ['poem_super_admin', 'probe']:
                ser_data = json.loads(item['fields']['serialized_data'])
                for d in ser_data:
                    d['pk'] = probepks[int(item['fields']['object_id'])]
                item['fields']['serialized_data'] = json.dumps(ser_data)
                item['fields']['object_id'] = \
                    str(probepks[int(item['fields']['object_id'])])

            version_pk += 1
            versionpks.update({item['pk']: version_pk})
            item['pk'] = version_pk
            item['fields']['revision'] = \
                revisionpks[item['fields']['revision']]

    # update extrevision table
    for item in data1:
        if item['model'] == 'poem_super_admin.extrevision':
            extrev_pk += 1
            item['fields']['probeid'] = probepks[item['fields']['probeid']]
            item['fields']['revision'] = revisionpks[item['fields']['revision']]
            item['pk'] = extrev_pk

    data = data1.copy()

    for dat in [data2, data3]:
        # reset dicts
        probepks = {}
        versionpks = {}
        revisionpks = {}
        new_names = set()

        for item in dat:
            if item['model'] == 'poem_super_admin.probe' and \
                item['fields']['name'] not in names:
                probe_pk += 1
                probepks.update({item['pk']: probe_pk})
                item['pk'] = probe_pk
                new_names.add(item['fields']['name'])
                data.append(item)

        used_revisions = []
        for item in dat:
            if item['model'] == 'reversion.version' and \
                json.loads(
                    item['fields']['serialized_data']
                )[0]['fields']['name'] not in names:
                used_revisions.append(item['fields']['revision'])

        for item in dat:
            if item['model'] == 'reversion.revision' and \
                    item['pk'] in used_revisions:
                revision_pk += 1
                revisionpks.update({item['pk']: revision_pk})
                item['pk'] = revision_pk
                data.append(item)

        for item in dat:
            if item['model'] == 'reversion.version' and \
                json.loads(
                    item['fields']['serialized_data'])[0]['fields']['name'] \
                    not in names:
                if item['fields']['content_type'] == \
                        ['poem_super_admin', 'probe']:
                    ser_data = json.loads(item['fields']['serialized_data'])
                    for d in ser_data:
                        d['pk'] = probepks[int(item['fields']['object_id'])]
                    item['fields']['serialized_data'] = json.dumps(ser_data)
                    item['fields']['object_id'] = \
                        str(probepks[int(item['fields']['object_id'])])

                version_pk += 1
                versionpks.update({item['pk']: version_pk})
                item['pk'] = version_pk
                item['fields']['revision'] = \
                    revisionpks[item['fields']['revision']]
                data.append(item)

        for item in dat:
            if item['model'] == 'poem_super_admin.extrevision' and \
                item['fields']['revision'] in used_revisions:
                item['fields']['probeid'] = \
                    probepks[item['fields']['probeid']]
                item['fields']['revision'] = \
                    revisionpks[item['fields']['revision']]
                extrev_pk += 1
                item['pk'] = extrev_pk
                data.append(item)

        names = names.union(new_names)

    return data


def users_data(inputdata):
    data = inputdata.copy()
    for item in data:
        if item['model'] == 'poem.custuser':
            item['model'] = 'users.custuser'

    perms = {}
    for item in data:
        if item['model'] == 'users.custuser':
            try:
                perms.update(
                    {
                        item['fields']['username']: {
                            'groupsofprofiles': item['fields'][
                                'groupsofprofiles'],
                            'groupsofmetrics': item['fields'][
                                'groupsofmetrics'],
                            'groupsofaggregations': item['fields'][
                                'groupsofaggregations']
                        }
                    }
                )
                del item['fields']['groupsofaggregations']
            except KeyError:
                perms.update(
                    {
                        item['fields']['username']: {
                            'groupsofprofiles': item['fields'][
                                'groupsofprofiles'],
                            'groupsofmetrics': item['fields'][
                                'groupsofmetrics']
                        }
                    }
                )
            del item['fields']['groupsofprofiles']
            del item['fields']['groupsofmetrics']
            del item['fields']['groupsofprobes']
    for key, value in perms.items():
        for item in data:
            if item['model'] == 'poem.userprofile' and \
                item['fields']['user'] == [key]:
                item['fields'].update(value)
    return data


def adapt_tenant_data(data):
    tenant_data = data.copy()
    new_data = []

    for item in tenant_data:
        if item['model'] == 'poem.probe' or \
                item['model'] == 'poem.extrevision' or \
                item['model'] == 'poem.groupofprobes':
            pass
        elif item['model'] == 'reversion.version':
            if item['fields']['content_type'] == ['poem', 'probe']:
                item['fields']['content_type'] = ['poem_super_admin', 'probe']
                ser_data = json.loads(item['fields']['serialized_data'])
                for d in ser_data:
                    if d['model'] == 'poem.probe':
                        d['model'] = 'poem_super_admin.probe'
                        d['fields']['user'] = 'poem'
                        del d['fields']['group']
                item['fields']['serialized_data'] = json.dumps(ser_data)
            new_data.append(item)
        else:
            new_data.append(item)

    return new_data


def create_tenant_data(tenant_data, public_data):
    pub_data = public_data.copy()
    data = adapt_tenant_data(tenant_data.copy())
    new_data = []

    probe_dict = {}
    for item in pub_data:
        if item['model'] == 'poem_super_admin.probe':
            probe_dict.update({item['fields']['name']: item['pk']})

    for item in data:
        if item['model'] == 'reversion.version' and \
                item['fields']['content_type'] == ['poem_super_admin', 'probe']:
            ser_data = json.loads(item['fields']['serialized_data'])
            for d in ser_data:
                d['pk'] = probe_dict[d['fields']['name']]
                item['fields']['object_id'] = \
                    str(probe_dict[d['fields']['name']])
            item['fields']['serialized_data'] = json.dumps(ser_data)
        new_data.append(item)

    return new_data


def append_missing_revisions_to_tenant(tenant_data, public_data):
    data = tenant_data.copy()
    reversion_data = public_data.copy()

    probe_dict = {}
    for item in reversion_data:
        if item['model'] == 'poem_super_admin.probe':
            probe_dict.update({item['fields']['name']: item['pk']})

    object_ids = []
    versions = []
    revisions = []
    for item in data:
        if item['model'] == 'reversion.version':
            if item['fields']['content_type'] == ['poem_super_admin', 'probe']:
                object_ids.append(item['fields']['object_id'])
            versions.append(item['pk'])
        if item['model'] == 'reversion.revision':
            revisions.append(item['pk'])
    version_pk = max(versions)
    revision_pk = max(revisions)

    rev_ids = {}
    for item in reversion_data:
        if item['model'] == 'reversion.version' and \
            item['fields']['object_id'] not in object_ids:
            version_pk += 1
            revision_pk += 1
            rev_ids.update({item['fields']['revision']: revision_pk})
            item['pk'] = version_pk
            ser_data = json.loads(item['fields']['serialized_data'])
            for d in ser_data:
                item['fields']['object_id'] = \
                    str(probe_dict[d['fields']['name']])
                d['pk'] = probe_dict[d['fields']['name']]
            item['fields']['serialized_data'] = json.dumps(ser_data)
            item['fields']['revision'] = revision_pk
            data.append(item)

    for item in reversion_data:
        if item['model'] == 'reversion.revision':
            if item['pk'] in rev_ids:
                item['pk'] = rev_ids[item['pk']]
                data.append(item)

    return data


def main():
    parser = argparse.ArgumentParser('Helper tool that converts .json files '
                                     'containing old db data into .json file '
                                     'which reflects changes in the db')
    parser.add_argument('--egi', dest='egi', help='input file for EGI tenant',
                        type=str, required=True)
    parser.add_argument('--eudat', dest='eudat', type=str, required=True,
                        help='input file for EUDAT tenant')
    parser.add_argument('--sdc', dest='sdc', help='input file for SDC tenant',
                        type=str, required=True)
    args = parser.parse_args()

    # load data
    with open(args.eudat, 'r') as f:
        data1 = json.load(f)

    with open(args.egi, 'r') as f:
        data2 = json.load(f)

    with open(args.sdc, 'r') as f:
        data3 = json.load(f)

    # fix poem.custuser to users.custuser and remove groupsofprobes
    data1 = users_data(data1)
    data2 = users_data(data2)
    data3 = users_data(data3)

    data = create_public_data(data1, data2, data3)

    with open('new-datadump-public.json', 'w') as f:
        json.dump(data, f, indent=2)

    # reload tenant data:
    with open(args.eudat, 'r') as f:
        data1 = json.load(f)

    with open(args.egi, 'r') as f:
        data2 = json.load(f)

    with open(args.sdc, 'r') as f:
        data3 = json.load(f)

    data1 = users_data(data1)
    data2 = users_data(data2)
    data3 = users_data(data3)

    tenant_data_initial1 = create_tenant_data(data1, data)
    tenant_data_initial2 = create_tenant_data(data2, data)
    tenant_data_initial3 = create_tenant_data(data3, data)

    # reload public schema data:
    with open('new-datadump-public.json', 'r') as f:
        data = json.load(f)

    tenant_data1 = append_missing_revisions_to_tenant(tenant_data_initial1,
                                                      data)
    tenant_data2 = append_missing_revisions_to_tenant(tenant_data_initial2,
                                                      data)
    tenant_data3 = append_missing_revisions_to_tenant(tenant_data_initial3,
                                                      data)

    with open('new-' + args.eudat, 'w') as f:
        json.dump(tenant_data1, f, indent=2)

    with open('new-' + args.egi, 'w') as f:
        json.dump(tenant_data2, f, indent=2)

    with open('new-' + args.sdc, 'w') as f:
        json.dump(tenant_data3, f, indent=2)


main()
