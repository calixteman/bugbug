# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import dateutil.parser
import pickle
import pytz

def pacific_date_str_to_utc_date_str(date_str):
    if date_str == '':
        return ''

    date = pytz.timezone('US/Pacific').localize(dateutil.parser.parse(date_str)).astimezone(pytz.utc)
    return date.isoformat(timespec='seconds').replace('+00:00', 'Z')
    

FIELD_TYPES = {
    'depends_on': int,
    'cf_last_resolved': pacific_date_str_to_utc_date_str,
    'is_confirmed': bool,
}

def rollback(bug, when):
    for history in reversed(bug['history']):
        for change in history['changes']:
            if 'attachment_id' in change:
                # TODO: Ignore changes to attachments for now.
                continue

            field = change['field_name']
            if field == 'flagtypes.name':
                # TODO: Ignore this for now, but need to support it!!!
                continue
            assert field in bug, '{} is not in bug'.format(field)
            print('Remove {} and add {} from {} - {}'.format(change['added'], change['removed'], field, bug[field]))
            if isinstance(bug[field], list):
                if change['added']:
                    for to_remove in change['added'].split(', '):
                        if field in FIELD_TYPES:
                            to_remove = FIELD_TYPES[field](to_remove)

                        if to_remove not in bug[field] and field == 'cc':
                            # Strange, but it happens unfortunately.
                            continue

                        bug[field].remove(to_remove)

                if change['removed']:
                    for to_add in change['removed'].split(', '):
                        if field in FIELD_TYPES:
                            to_add = FIELD_TYPES[field](to_add)
                        bug[field].append(to_add)
            else:
                if field in FIELD_TYPES:
                    old_value = FIELD_TYPES[field](change['removed'])
                    new_value = FIELD_TYPES[field](change['added'])
                else:
                    old_value = change['removed']
                    new_value = change['added']
                assert bug[field] == new_value, '{} is different from {}'.format(bug[field], new_value)
                bug[field] = old_value


# WIP CODE TO REMOVE.
bug = pickle.load(open('bugtotryhistory.pickle', 'rb'))
rollback(bug[0], None)

bug = pickle.load(open('bugtotryhistory_with_needinfo.pickle', 'rb'))
rollback(bug[0][1], None)
