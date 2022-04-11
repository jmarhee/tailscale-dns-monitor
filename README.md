# Tailscale Nameserver Monitor for K3s

K3s nodes should have the `k3s.io/external-ip` annotation with your Tailscale IP address.

## K3s Node Configuration

On your master nodes, your `k3s.service` should include the following in `ExecStart`:

```yaml
ExecStart=/usr/local/bin/k3s \
    server \
    --node-external-ip ${YOUR_TAILSCALE_IP}
```

On your agent nodes, your `k3s-agent.service` should include the following in your `ExecStart`:

```yaml
ExecStart=/usr/local/bin/k3s \
    agent \
    --node-external-ip ${YOUR_TAILSCALE_IP}
    --node-ip ${NODE_IP}
```

You can find the Tailscale IP address using `tailscale ip --4`. 

## Setup

This workload requires a `ServiceAccount`:

```bash
kubectl create sa node-reader
kubectl create clusterrole node-reader --verb=get,list --resource=nodes
kubectl create clusterrolebinding node-reader --serviceaccount=default:node-reader --clusterrole=node-reader
```

Requires `Secret` resources for the following environment variables to be set in your workload:

```yaml
        env:
        - name: TAILNET_ID
          valueFrom:
            secretKeyRef:
              name: tailscale-auth
              key: tailnet-id
              optional: false
        - name: TAILSCALE_TOKEN
          valueFrom:
            secretKeyRef:
              name: tailscale-auth
              key: tailscale-token
              optional: false
        - name: FORWARDING_NAMESERVERS
          valueFrom:
            secretKeyRef:
              name: tailscale-auth
              key: tailscale-forwarding-nameservers
              optional: false
```

`FORWARDING_NAMESERVERS` should be a comma separated string (i.e. `"8.8.8.8,8.8.4.4"`), and `TAILNET_ID` should be your Tailnet name in the admin console.