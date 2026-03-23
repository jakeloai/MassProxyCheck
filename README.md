# MassProxyCheck - Proxy Testing Tool

**MassProxyCheck** is a robust command-line tool for testing proxy servers, designed for pentesters, ethical hackers, developers, and network administrators. It verifies proxy functionality, measures latency, and supports HTTP, HTTPS, SOCKS4, and SOCKS5 protocols. Developed by **JakeLo.AI**, MassProxyCheck ensures reliable and efficient proxy testing.

## Features

* **Multi-Protocol Support**: Tests HTTP, HTTPS, SOCKS4, and SOCKS5 proxies.
* **Concurrent Testing**: Uses multi-threading for faster testing (default: 10 threads).
* **Latency Measurement**: Classifies proxies as fast (< 500ms), normal (500ms–1000ms), or slow (> 1000ms) based on a customizable threshold.
* **Retry Mechanism**: Retries failed requests with doubled timeout for reliability.
* **Flexible Output**: Saves working proxies in TXT, JSON, or CSV formats.
* **Progress Tracking**: Displays a progress bar using `tqdm`.
* **Color-Coded Results**: Uses `colorama` for clear, color-coded output (green for fast, cyan for normal, yellow for slow, red for non-working).
* **Custom Test URLs**: Supports default test URLs or a user-specified URL.

---

## Installation

### Prerequisites
* Python 3.6+
* Required packages:
    ```bash
    pip install 'requests[socks]' colorama tqdm
    ```

### Setup
1.  Clone or download the repository from **JakeLo.AI** at [https://jakelo.ai/](https://jakelo.ai/).
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

MassProxyCheck tests proxies listed in a file, with one proxy per line in formats like:
```text
http://192.168.1.1:8080
socks5://user:pass@192.168.1.2:1080
192.168.1.3:3128
```

### Command-Line Arguments
```bash
python mpc.py -f proxy_list.txt [options]
```

| Option | Description |
| :--- | :--- |
| `-f`, `--file` | **Required**. Path to the proxy list file (e.g., `proxy_list.txt`). |
| `-o`, `--output` | Path to save working proxies (e.g., `working_proxies.txt`). |
| `-t`, `--threshold` | Latency threshold for fast proxies in milliseconds (default: 1000). |
| `--threads` | Maximum number of threads for concurrent testing (default: 10). |
| `--timeout` | Request timeout in seconds (default: 5). Retries once with double timeout. |
| `--url` | Custom test URL (overrides default test URLs). |

---

## Example Proxy List File
Create `proxy_list.txt` with:
```text
http://192.168.1.1:8080
socks5://user:pass@192.168.1.2:1080
192.168.1.3:3128
```

## Notes
* **Default Test URLs**: `https://httpbin.org/ip`, `https://ifconfig.me/ip`, `https://api.ipify.org?format=json`.
* **Authentication**: Authenticated proxies use the format `protocol://username:password@ip:port`.
* **Reliability**: The tool retries failed requests once with double the timeout to account for temporary network fluctuations.
* **Naming**: For convenience, it is recommended to save the script as `mpc.py`.

---

## Contact
* **Developer**: JakeLo.AI
* **Email**: [hello@jakelo.ai](mailto:hello@jakelo.ai)
* **Website**: [https://jakelo.ai/](https://jakelo.ai/)

## Disclaimer
**MassProxyCheck** is for ethical hacking and penetration testing only. Ensure you have explicit permission to test proxies and comply with all applicable local and international laws.
