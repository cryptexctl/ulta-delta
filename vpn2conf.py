import base64, zlib, json, argparse, uuid
from urllib import request, parse
from urllib.error import HTTPError

def decode_vpn_link(vpn_key_str):
    if vpn_key_str.startswith("vpn://"):
        vpn_key_str = vpn_key_str[6:]
    padded = vpn_key_str + '=='
    data = base64.urlsafe_b64decode(padded)
    raw = zlib.decompress(data[4:])
    return json.loads(raw.decode())

def fetch_config(api_key):
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
                    return f"[!] Error: {parsed.get('error', {}).get('localized_message', 'Unknown error')}"
            except json.JSONDecodeError:
                return result
    except HTTPError as e:
        return f"[!] HTTP Error: {e.code} {e.reason}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode UltaVPN vpn:// key and fetch WireGuard config")
    parser.add_argument("key", help="VPN key starting with vpn://")
    parser.add_argument("-gc", "--get-conf", action="store_true", help="Fetch WG config from API")
    args = parser.parse_args()

    try:
        conf = decode_vpn_link(args.key)
        print("[i] Decoded VPN Key:\n", json.dumps(conf, indent=2))
        if args.get_conf:
            print("\n[i] Fetching .conf from API...")
            wg_conf = fetch_config(conf["api_key"])
            print("\n[+] WireGuard Config:\n", wg_conf)
    except Exception as e:
        print("[!] Error:", e)
