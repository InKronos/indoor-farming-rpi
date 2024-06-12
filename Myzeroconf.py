from zeroconf import Zeroconf, ServiceInfo
import time
import socket



def get_local_ip():
    # Tworzymy połączenie do adresu zewnętrznego (nie musi być osiągalny, chodzi tylko o uzyskanie lokalnego IP)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

local_ip = get_local_ip()

def create_service_info():
    service_info = ServiceInfo(
        "_http._tcp.local.",
        "Raspberry Pi Device 1 Server._http._tcp.local.",  # Human-readable service name
        addresses=[socket.inet_aton(local_ip)],  # Replace with your server's local IP address
        port=8080,
        properties={},
    )
    return service_info

def main():
    zeroconf = Zeroconf()
    info = create_service_info()

    print("Registering service...")
    zeroconf.register_service(info)

    try:
        while True:
            # Refresh the service periodically to keep it alive
            time.sleep(20)  # Refresh every 60 seconds
            zeroconf.unregister_service(info)
            zeroconf.register_service(info)
            print("Service refreshed")
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering service...")
        zeroconf.unregister_service(info)
        zeroconf.close()

if __name__ == "__main__":
    main()
