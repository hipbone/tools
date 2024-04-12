import socket
import http.client
import ssl
from colorama import init, Fore

# variables
file_path = "list"
hc_path = "/check.php"
ssl_verify = False

# colorama 초기화
init(autoreset=True)


def is_ip_address(value):
    try:
        socket.inet_aton(value)
        return True
    except socket.error:
        return False


def check_dns(input_value):
    try:
        ip_address = socket.gethostbyname(input_value)
        print(Fore.GREEN + f"[Success] DNS Lookup: {input_value} / {ip_address}")
        return input_value, ip_address
    except socket.error as e:
        print(Fore.RED + f"[Error] DNS Lookup Failed: {e}")
        return None


def check_http(domain, port):
    try:
        # HTTP 연결 시도
        conn = http.client.HTTPConnection(domain, port, timeout=5)
        conn.request("GET", hc_path)
        response = conn.getresponse()

        if response.status in [200, 301, 302]:
            print(Fore.GREEN + f"[Success] HTTP Test: {response.status}")
        else:
            print(Fore.RED + f"[Error] HTTP Test Failed: {response.status}")

        conn.close()
    except Exception as e:
        print(Fore.RED + f"[Error] HTTP Test Failed: {e}")


def check_https(domain, port):
    try:
        # HTTPS 연결 시도
        context = ssl.create_default_context()
        if not ssl_verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        conn = http.client.HTTPSConnection(domain, port, context=context, timeout=5)
        conn.request("GET", hc_path)
        response = conn.getresponse()

        if response.status == 200:
            print(Fore.GREEN + f"[Success] HTTPS Test: {response.status}")
        else:
            print(Fore.RED + f"[Error] HTTPS Test Failed: {response.status}")

        conn.close()
    except Exception as e:
        print(Fore.RED + f"[Error] HTTPS Test Failed: {e}")


if __name__ == "__main__":
    try:
        with open(file_path, "r") as file:
            for line in file.readlines():
                line = line.strip()
                print(f"===== {line} check =====")
                if is_ip_address(line):
                    # 1. DNS Lookup
                    print(Fore.YELLOW + f"Skip DNS Lookup : {line}")
                else:
                    # 1. DNS Lookup
                    domain, ip_address = check_dns(line)
                # 2. HTTP 연결 테스트
                check_http(line, 80)
                # 3. HTTPS 연결 테스트
                check_https(line, 443)
                print(f"")

    except FileNotFoundError:
        print(Fore.RED + f"파일을 찾을 수 없습니다 : {file_path}")
    except Exception as e:
        print(Fore.RED + f"에러가 발생 했습니다 : {e}")
