import base64, zlib, json, sys

def decode_vpn_link(vpn_key_str):
    if vpn_key_str.startswith("vpn://"):
        vpn_key_str = vpn_key_str[6:]
    padded = vpn_key_str + '=='  # padding fix
    data = base64.urlsafe_b64decode(padded)
    raw = zlib.decompress(data[4:])  # skip 4-byte prefix
    return json.loads(raw.decode())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Decode UltaVPN vpn:// key")
    parser.add_argument("key", help="VPN key starting with vpn://")
    args = parser.parse_args()

    try:
        conf = decode_vpn_link(args.key)
        print(json.dumps(conf, indent=2))
    except Exception as e:
        print("[!] Error:", e)
