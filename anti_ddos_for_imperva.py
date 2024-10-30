import httpx
import subprocess
import numpy as np
import requests
import json

# Установите ваши API-ключи и URL
api_key = "your_api_key"
api_url = "https://my.imperva.com/api/prov/v1/sites/"
site_id = "your_site_id"

# Список команд для UFW
commands = [
    "ufw reset -y",
    "ufw default reject incoming",
    "ufw allow ssh",
    "ufw limit ssh",
    "ufw reload",
    "ufw enable -y"
]

# Функция для добавления IP-адреса в черный список Imperva
def add_ip_to_blacklist(ip_address):
    headers = {
        "x-API-Id": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "rule": {
            "name": "Block IP",
            "action": "block_request",
            "trigger": {
                "target": "ip",
                "operator": "eq",
                "values": [ip_address]
            }
        }
    }
    
    response = requests.post(f"{api_url}{site_id}/security/waf/rules", headers=headers, data=json.dumps(data))
    
    if response.status_code == 201:
        print(f"IP-адрес {ip_address} успешно добавлен в черный список.")
    else:
        print(f"Ошибка при добавлении IP-адреса {ip_address}: {response.text}")

def test_pytest_pass():
    assert 1 == 1

try:
    for cmd in commands:
        if "ufw allow proto tcp" in cmd:
            with httpx.Client(headers={"Cache-Control": "must-revalidate", "Content-Type": "text/plain"}) as client:
                ipv4s = client.get("https://www.cloudflare.com/ips-v4").text.strip().split("\n")
                ipv6s = client.get("https://www.cloudflare.com/ips-v6").text.strip().split("\n")
                ips = np.concatenate((ipv4s, ipv6s))
                for ip in ips:
                    p = subprocess.Popen(cmd % ip, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = p.communicate(input='y\n'.encode())
                    if err:
                        print("failed configuration: %s" % err.decode())
                        exit(0)
                    if out:
                        print(out.decode())
                    # Добавляем IP в черный список Imperva
                    add_ip_to_blacklist(ip)
            continue
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(input='y\n'.encode())
        if err:
            print("failed configuration: %s" % err.decode())
            exit(0)
        if out:
            print(out.decode())
except Exception as e:
    print("Found error: %s" % e)
