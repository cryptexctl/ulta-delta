import base64
import zlib
import json
import argparse
import uuid
from urllib import request, parse
from urllib.error import HTTPError

def decode_vpn_link(vpn_key_str):
    if vpn_key_str.startswith("vpn://"):
        vpn_key_str = vpn_key_str[6:]
    
    padding_needed = len(vpn_key_str) % 4
    if padding_needed:
        vpn_key_str += '=' * (4 - padding_needed)
    
    try:
        data = base64.urlsafe_b64decode(vpn_key_str)
        raw = zlib.decompress(data[4:])
        return json.loads(raw.decode())
    except (base64.binascii.Error, zlib.error, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to decode VPN link: {e}")

def fetch_config(api_key):
    if not api_key:
        raise ValueError("API key is required")

    url = f"https://api.ultvs.click/client-api/v1/download-awg-key?public_request_id={api_key}"
    headers = {
        "X-Device-Id": str(uuid.uuid4()),
        "User-Agent": "ulta-android/1.2.2.37"
    }

    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req) as resp:
            result = resp.read().decode()
            try:
                parsed = json.loads(result)
                if parsed.get("data"):
                    return parsed["data"]
                else:
                    error_msg = parsed.get('error', {}).get('localized_message', 'Unknown error')
                    raise ValueError(f"API error: {error_msg}")
            except json.JSONDecodeError:
                return result
    except HTTPError as e:
        raise RuntimeError(f"HTTP Error: {e.code} {e.reason}")

def save_config(config, filename):
    with open(filename, 'w') as f:
        f.write(config)
    return filename

def main():
    parser = argparse.ArgumentParser(description="Decode UltaVPN vpn:// key and fetch WireGuard config")
    parser.add_argument("key", help="VPN key starting with vpn://")
    parser.add_argument("-gc", "--get-conf", action="store_true", help="Fetch WG config from API")
    parser.add_argument("-o", "--output", help="Save WireGuard config to file")
    args = parser.parse_args()

    try:
        conf = decode_vpn_link(args.key)
        print("[i] Decoded VPN Key:\n", json.dumps(conf, indent=2))
        
        if args.get_conf:
            print("\n[i] Fetching .conf from API...")
            wg_conf = fetch_config(conf["api_key"])
            print("\n[+] WireGuard Config:\n", wg_conf)
            
            if args.output:
                saved_file = save_config(wg_conf, args.output)
                print(f"\n[+] Config saved to: {saved_file}")
                
    except Exception as e:
        print(f"[!] Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
