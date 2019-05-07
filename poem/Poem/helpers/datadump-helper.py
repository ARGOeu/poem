#!/usr/bin/env python
import argparse
import json


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


def main():
    parser = argparse.ArgumentParser('Helper tool that converts .json '
                                     'files containing old db data into .json '
                                     'file which reflects changes in the db')
    parser.add_argument('-i', dest='input', help='input file', type=str,
                        required=True)
    parser.add_argument('-o', dest='output', help='output file', type=str,
                        required=True)
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        data = json.load(f)

    final_data = users_data(data)

    with open(args.output, 'w') as f:
        json.dump(final_data, f, indent=2)


main()
