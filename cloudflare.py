import os
import CloudFlare
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
CF_API_TOKEN = os.getenv(('CF_API_TOKEN'))
EMAIL = os.getenv('EMAIL')

cloud_flare = CloudFlare.CloudFlare(email=EMAIL, token=CF_API_TOKEN)

def add_dns_to_cloudflare(domain, name, content, proxied=False, dns_type='CNAME', ssl_setting='full'):
    if len(domain.split('.')) > 2:
        zone_name = '.'.join(domain.split('.')[1:])
    else:
        zone_name = domain
    params = {'name': zone_name, 'per_page': 1}
    zones = cloud_flare.zones.get(params=params)
    zone_id = zones[0]['id']

    dns_records = cloud_flare.zones.dns_records.get(zone_id)
    updated = False

    for dns_record in dns_records:
        old_ip_address = dns_record['content']
        old_ip_address_type = dns_record['type']
        old_name = dns_record['name']
        dns_record_id = dns_record['id']

        if old_ip_address_type not in ['A', 'AAAA', 'CNAME']:
            continue

        if old_ip_address_type != dns_type:
            if old_name == zone_name:
                try:
                    print(f'Deleting record {dns_record}')
                    r = cloud_flare.zones.dns_records.delete(
                        zone_id, dns_record_id)
                except:
                    print(f'Could Not Delete {zone_name} {dns_record_id}')
            continue
        if old_ip_address == content:
            continue
        if old_name != name:
            continue

        proxied_state = dns_record['proxied']
        updated_record = {
            'name': name,
            'type': dns_type,
            'content': content,
            'proxied': proxied_state
        }
        try:
            r = cloud_flare.zones.dns_records.put(
                zone_id, dns_record_id, data=updated_record)
        except Exception as e:
            print(e)
            print(zone_id)
            print(dns_record)
        print(f"SUCCESS ----- Updated {updated_record} to cloudflare")
        updated = True

    if updated:
        return

    dns_record = {'name': name, 'type': dns_type,
                  'content': content, 'proxied': proxied}
    print(f"Adding {dns_record} to cloudflare")
    try:
        r = cloud_flare.zones.dns_records.post(zone_id, data=dns_record)
    except Exception as e:
        print(e)
        print(zone_id)
        print(dns_record)
    try:
        settings_ssl = cloud_flare.zones.settings.ssl.patch(
            zone_id, data={'value': ssl_setting})
    except:
        print('SSL Not Set')
    print(f"SUCCESS ----- Adding {dns_record} to cloudflare")
    return


def add_page_rule(zone_name):

    zones = cloud_flare.zones.get(params={'name': zone_name, 'per_page': 1})
    zone_id = zones[0]['id']
    data = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"www.{zone_name}/*"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://{zone_name}/$1",
                'status_code': 302
            }
        }],
        "priority": 1,
        "status": 'active'
    }
    data2 = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"{zone_name}/"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://{zone_name}/index.html",
                'status_code': 302
            }
        }],
        "priority": 2,
        "status": 'active'
    }
    data3 = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"*.{zone_name}/"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://$1.{zone_name}/index.html",
                'status_code': 302
            }
        }],
        "priority": 3,
        "status": 'active'
    }
    try:
        r = cloud_flare.zones.pagerules.post(zone_id, data=data)
        r2 = cloud_flare.zones.pagerules.post(zone_id, data=data2)
        r3 = cloud_flare.zones.pagerules.post(zone_id, data=data3)
    except Exception as e:
        print(e)

    return

def add_domain_to_cloudflare(zone_name):
    """
        Attempts to create a new zone
        If Zone already exists this will return False
    """
    try:
        zone_info = cloud_flare.zones.post(
            data={'jump_start': False, 'name': zone_name})
        zone_id = zone_info['id']
        r = cloud_flare.zones.settings.always_use_https.patch(
            zone_id, data={'value': 'on'})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print('/zones.post %s - %d %s' % (zone_name, e, e))
        return False
    except Exception as e:
        print('/zones.post %s - %s' % (zone_name, e))
        return False

    print('Finished creating zone %s ...' % (zone_name))
    return zone_info


def add_page_rule(zone_name):

    zones = cloud_flare.zones.get(params={'name': zone_name, 'per_page': 1})
    zone_id = zones[0]['id']
    data = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"www.{zone_name}/*"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://{zone_name}/$1",
                'status_code': 302
            }
        }],
        "priority": 1,
        "status": 'active'
    }
    data2 = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"{zone_name}/"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://{zone_name}/index.html",
                'status_code': 302
            }
        }],
        "priority": 2,
        "status": 'active'
    }
    data3 = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"*.{zone_name}/"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://$1.{zone_name}/index.html",
                'status_code': 302
            }
        }],
        "priority": 3,
        "status": 'active'
    }
    try:
        r = cloud_flare.zones.pagerules.post(zone_id, data=data)
        r2 = cloud_flare.zones.pagerules.post(zone_id, data=data2)
        r3 = cloud_flare.zones.pagerules.post(zone_id, data=data3)
    except Exception as e:
        print(e)

    return


def edit_page_rule(zone_name):
    zones = cloud_flare.zones.get(params={'name': zone_name, 'per_page': 1})
    zone_id = zones[0]['id']
    r = cloud_flare.zones.pagerules.get(zone_id)
    print(r)
    rule_id = r[0]['id']
    tid = zone_name.replace('-', '').replace('.', '').replace('/', '')
    print(tid)
    data = {
        "targets": [
            {
                "target": 'url',
                "constraint": {
                    "operator": "matches",
                    "value": f"{zone_name}/"
                }

            }
        ],
        "actions": [{
            'id': 'forwarding_url',
            'value': {
                'url': f"https://{zone_name}/index.html",
                'status_code': 302
            }
        }],
        "priority": 2,
        "status": 'active'
    }
    p = cloud_flare.zones.pagerules.patch(zone_id, rule_id, data=data)
    return


def delete_dns_records(zone_name, record_type='', content=''):
    """
    TODO Make passing in record type and content available to delete only the record that I want to replace
    """
    zones = cloud_flare.zones.get(params={'name': zone_name, 'per_page': 1})
    zone_id = zones[0]['id']
    dns_records = cloud_flare.zones.dns_records.get(zone_id)
    for record in dns_records:
        if 'google-site' in record['content'] or 'verify.bing' in record['content']:
            continue
        print(f"Deleting {record['name']}")
        print(f"Deleting {record['type']}")
        print(f"Deleting {record['content']}")
        record_id = record['id']
        r = cloud_flare.zones.dns_records.delete(zone_id, record_id)


def get_name_servers(zone_name):
    zones = cloud_flare.zones.get(params={'name': zone_name, 'per_page': 1})
    if zones:
        return zones[0]['name_servers']
    return False


def add_site_to_cloudflare(domain):
    try:
        zone = add_domain_to_cloudflare(domain)
    except:
        return False
    return zone


if __name__ == '__main__':

    pass
