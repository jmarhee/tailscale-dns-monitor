import requests
import os, sys
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if os.environ.get("TAILNET_ID") is None:
    sys.exit("TAILNET_ID must be set.")
else:
    TAILNET_ID = os.environ['TAILNET_ID']

if os.environ.get("TAILSCALE_TOKEN") is None:
    sys.exit("TAILSCALE_TOKEN must be set.")
else:
    TAILSCALE_TOKEN = os.environ['TAILSCALE_TOKEN']

def serviceAccountToken():
    if os.environ.get("SERVICE_ACCOUNT_TOKEN") is None:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
            data = file.read().rstrip()
    else:
        data = os.environ['SERVICE_ACCOUNT_TOKEN']
    return data

def nodeData(token):
    # curl -k -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
    #  https://kubernetes.default.svc:443/api/v1/namespaces/{namespace}/endpoints/my-service
    headers = {"Authorization": "Bearer %s" % (token)}
    if os.environ.get("DEBUG") is None:
        url = "https://kubernetes.default.svc:443/api/v1/nodes"
    else:
        url = "http://localhost:8001/api/v1/nodes"
    request = requests.get(url,headers=headers,verify=False)
    return request.text

def returnNodeTailscaleIp(nodes):
    node_ips = []
    nodes_in = json.loads(nodes)
    for node in nodes_in['items']:
        node_ips.append(node['metadata']['annotations']['k3s.io/external-ip'])
    return node_ips

def getCurrentDns():
    # GET /api/v2/tailnet/example.com/dns/nameservers
    # curl 'https://api.tailscale.com/api/v2/tailnet/example.com/dns/nameservers' \
    #  -u "tskey-yourapikey123:"
    url = "https://api.tailscale.com/api/v2/tailnet/%s/dns/nameservers" % (TAILNET_ID)
    auth=('%s' % (TAILSCALE_TOKEN), '')
    request = requests.get(url, auth=auth)
    return request.json()['dns']

def updateDns(ips):
    # POST /api/v2/tailnet/example.com/dns/nameservers
    # curl -X POST 'https://api.tailscale.com/api/v2/tailnet/example.com/dns/nameservers' \
    #   -u "tskey-yourapikey123:" \
    #   --data-binary '{"dns": ["8.8.8.8"]}'
    in_node_ips = []
    for ip in FORWARDING_NAMESERVERS.split(","):
        in_node_ips.append(ip)
    for ip in ips:
        in_node_ips.append(ip)
    url = "https://api.tailscale.com/api/v2/tailnet/%s/dns/nameservers" % (TAILNET_ID)
    auth=('%s' % (TAILSCALE_TOKEN), '')
    in_node_ips.sort()
    data = json.dumps({"dns": node_ips})
    request = requests.post(url, auth=auth,data=data)
    return request.json()

def compareDnsIps(node_ips,current_dns):
    changes = []
    for ip in current_dns:
        if ip in node_ips:
            continue
        else:
            changes.append(ip)
    if len(changes) > 0:
        updateDns(node_ips)
    else:
        pass
    return changes

if __name__ == '__main__':
    token = serviceAccountToken()
    nodes = nodeData(token)
    node_ips = returnNodeTailscaleIp(nodes)
    current_dns = getCurrentDns()
    print(compareDnsIps(node_ips,current_dns))
    print("current: %s" % (getCurrentDns()))