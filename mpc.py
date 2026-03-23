import requests
import time
import re
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
from tqdm import tqdm
import json
import random

# Initialize colorama
init(autoreset=True)

# Branding & Intro
BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}============================================================
       MassProxyCheck - Professional Proxy Tester
============================================================
{Fore.YELLOW}Developed by: JakeLo.AI via Prompt Engineering
Website: https://jakelo.ai/
Email: hello@jakelo.ai
{Fore.CYAN}============================================================
"""

# Default test URLs
DEFAULT_TEST_URLS = [
    "https://httpbin.org/ip",
    "https://ifconfig.me/ip",
    "https://api.ipify.org?format=json"
]

def parse_args():
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}MassProxyCheck: A robust proxy tester for security professionals.{Style.RESET_ALL}",
        epilog="""
Example Proxy List (proxy_list.txt):
  http://192.168.1.1:8080
  socks5://user:pass@192.168.1.2:1080
  192.168.1.3:3128

Usage:
  python mpc.py -f proxy_list.txt -o working.txt
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-f", "--file", required=True, help="Proxy list file (e.g. proxy_list.txt)")
    parser.add_argument("-o", "--output", help="Output file (to save working proxies)")
    parser.add_argument("-t", "--threshold", type=int, default=1000, help="Latency threshold for fast proxies (ms, default 1000)")
    parser.add_argument("--threads", type=int, default=10, help="Maximum number of threads (default 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default 5). Retries once with double timeout.")
    parser.add_argument("--url", help="Custom test URL (if not provided, one will be chosen randomly from defaults)")
    return parser.parse_args()

def parse_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    match = re.match(r"(?:(http|https|socks4|socks5)://)?(?:([^:]+):([^@]+)@)?([^:]+):(\d+)", proxy_str)
    if not match:
        match = re.match(r"([^:]+):(\d+)", proxy_str)
        if match:
            return {"protocol": "http", "ip": match.group(1), "port": int(match.group(2)),
                    "username": None, "password": None}
        return None
    protocol, username, password, ip, port = match.groups()
    protocol = protocol or "http"
    return {"protocol": protocol, "ip": ip, "port": int(port),
            "username": username, "password": password}

def test_proxy(proxy_info, test_urls, timeout, custom_url=None):
    if not proxy_info:
        return False, None, "Invalid format"

    test_url = custom_url if custom_url else random.choice(test_urls)

    auth_part = ""
    if proxy_info["username"] and proxy_info["password"]:
        auth_part = f"{proxy_info['username']}:{proxy_info['password']}@"

    proxy_str = f"{proxy_info['protocol']}://{auth_part}{proxy_info['ip']}:{proxy_info['port']}"
    proxies = {"http": proxy_str, "https": proxy_str}

    # First attempt
    try:
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        end_time = time.time()
        if response.status_code == 200:
            latency = (end_time - start_time) * 1000
            return True, latency, None
        else:
            return False, None, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        # Retry with double timeout
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout * 2)
            end_time = time.time()
            if response.status_code == 200:
                latency = (end_time - start_time) * 1000
                return True, latency, None
            else:
                return False, None, f"HTTP {response.status_code}"
        except Exception:
            return False, None, "Timeout (after retry)"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection failed"
    except requests.exceptions.RequestException:
        return False, None, "Request error"

    return False, None, "Unknown error"

def display_result(proxy_str, is_working, latency, threshold, error=None):
    if not is_working:
        return f"{proxy_str}: {Fore.RED}not working{Style.RESET_ALL} ({error})"
    else:
        fast_cut = threshold / 2
        if latency < fast_cut:
            return f"{proxy_str}: {Fore.GREEN}working, and fast{Style.RESET_ALL} (Speed: {latency:.2f} ms)"
        elif latency < threshold:
            return f"{proxy_str}: {Fore.CYAN}working, normal speed{Style.RESET_ALL} (Speed: {latency:.2f} ms)"
        else:
            return f"{proxy_str}: {Fore.YELLOW}working, but slow{Style.RESET_ALL} (Speed: {latency:.2f} ms)"

def main():
    print(BANNER)
    args = parse_args()

    if not os.path.exists(args.file):
        print(f"{Fore.RED}Error: file {args.file} does not exist!{Style.RESET_ALL}")
        return

    with open(args.file, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

    if not proxies:
        print(f"{Fore.RED}Error: proxy list file is empty!{Style.RESET_ALL}")
        return

    print(f"Starting test of {len(proxies)} proxies...\n")
    working_proxies = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(test_proxy, parse_proxy(p), DEFAULT_TEST_URLS, args.timeout, args.url): p for p in proxies}
        with tqdm(total=len(proxies), desc="Testing Proxies", unit="proxy") as pbar:
            for future in as_completed(futures):
                proxy = futures[future]
                is_working, latency, error = future.result()
                tqdm.write(display_result(proxy, is_working, latency, args.threshold, error))
                if is_working:
                    working_proxies.append(proxy)
                pbar.update(1)

    if working_proxies:
        if args.output:
            with open(args.output, "w") as f:
                for proxy in working_proxies:
                    f.write(proxy + "\n")
            print(f"\n{Fore.GREEN}Working proxies saved to {args.output}{Style.RESET_ALL}")
        else:
            choice = input("\nDo you want to save the working proxies to a new file? (y/n): ").lower()
            if choice == "y":
                output_format = input("Choose output format (txt/json/csv): ").lower()
                new_file = input("Enter new proxy file name (e.g. working_proxies.txt): ").strip()
                if output_format == "json":
                    with open(new_file, "w") as f:
                        json.dump(working_proxies, f, indent=2)
                elif output_format == "csv":
                    with open(new_file, "w") as f:
                        f.write("proxy\n")
                        for proxy in working_proxies:
                            f.write(f"{proxy}\n")
                else:
                    with open(new_file, "w") as f:
                        for proxy in working_proxies:
                            f.write(proxy + "\n")
                print(f"{Fore.GREEN}Working proxies saved to {new_file}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No proxies saved. Program finished.{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}No working proxies found.{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}MassProxyCheck execution complete.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()