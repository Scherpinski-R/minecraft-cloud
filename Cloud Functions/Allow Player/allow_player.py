from typing import Optional
import functions_framework
#from markupsafe import escape
from google.cloud import compute_v1
import time
import re

def get_ip_version(ip: str):
    match_ipv4 = re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)
    if match_ipv4:
        return "ipv4"
    else:
        return "ipv6"

def create_ip_cidr(user_ip: str):
    if get_ip_version(user_ip) == "ipv4":
        user_ip_cidr = f"{user_ip}/32"
    else:
        user_ip_cidr = f"{user_ip}/128"
    
    return user_ip_cidr

def is_user_whitelisted(project_id: str, user_ip: str) -> bool:
    client = compute_v1.FirewallsClient()
    request = compute_v1.ListFirewallsRequest(project=project_id)
    page_result = client.list(request=request)

    for result in page_result:
        if create_ip_cidr(user_ip) in result.source_ranges and 'minecraft-server' in result.target_tags:
            return True
        
    return False

def add_firewall_rule(
    project_id: str,
    network_name: str,
    user_ip: str,
    port: int = 25565,
    target_tags: Optional[list] = None,
    rule_description: str = "Allow user IP to Minecraft server"
):
    client = compute_v1.FirewallsClient()

    allowed_connection = compute_v1.Allowed(
        I_p_protocol="tcp",
        ports=[str(port)]
    )

    user_ip_cidr = create_ip_cidr(user_ip)

    timestamp = time.strftime("%Y%m%d")
    rule_name = f"ap-mc-{timestamp}-{user_ip.replace('.', '-').replace(':', '-').replace('/', '-')}"

    firewall_rule_body = compute_v1.Firewall(
        name=rule_name,
        network=f"projects/{project_id}/global/networks/{network_name}",
        direction="INGRESS",
        priority=1000,
        allowed=[allowed_connection],
        source_ranges=[user_ip_cidr],
        description=rule_description
    )

    if target_tags:
        firewall_rule_body.target_tags = target_tags

    print(f"Attempting to add firewall rule '{rule_name}' for IP: {user_ip_cidr}...")

    
    operation = client.insert(project=project_id, firewall_resource=firewall_rule_body)
    return True

http_status_internal_error = 500
http_status_malformed = 400
http_status_ok = 200

@functions_framework.http
def allow_player(request):

    x_forwarded_for = request.headers.get('X-Forwarded-For')

    if x_forwarded_for == None:
        return "Could not determine your IP address from X-Forwarded-For header.", http_status_malformed
        
    user_ip = x_forwarded_for.split(',')[0].strip()
    project_id = "minecraft-host-465119"
    network = "default"
    vm_tags = ['minecraft-server'] 

    if is_user_whitelisted(project_id, user_ip):
        return f"User already whitelisted! Have fun!", http_status_ok

    if add_firewall_rule(project_id, network, user_ip, target_tags=vm_tags):
        return f"Firewall rule added for {user_ip}. User should now be able to connect.", http_status_ok
    
    return f"Could not add firewall rule for {user_ip}.", http_status_internal_error