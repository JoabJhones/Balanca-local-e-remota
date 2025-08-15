import socket
import subprocess
import platform

def get_local_ip():
    """Descobre o IP local do computador."""
    try:
        # Método 1: Conecta a um endereço externo para descobrir IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Método 2: Usa hostname
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"

def get_all_ips():
    """Lista todos os IPs disponíveis."""
    ips = []
    
    try:
        if platform.system() == "Windows":
            # Windows
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'IPv4' in line or 'Endereço IPv4' in line:
                    ip = line.split(':')[-1].strip()
                    if ip and ip != '127.0.0.1':
                        ips.append(ip)
        else:
            # Linux/Mac
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'inet' and i + 1 < len(parts):
                            ip = parts[i + 1]
                            if '.' in ip:
                                ips.append(ip)
    except:
        pass
    
    return ips

def main():
    print("=" * 50)
    print("DESCOBRIR IP PARA CONFIGURAÇÃO DE REDE")
    print("=" * 50)
    
    # IP principal
    main_ip = get_local_ip()
    print(f"\n🔹 IP PRINCIPAL: {main_ip}")
    
    # Todos os IPs
    all_ips = get_all_ips()
    if all_ips:
        print(f"\n🔹 TODOS OS IPs DISPONÍVEIS:")
        for i, ip in enumerate(all_ips, 1):
            print(f"   {i}. {ip}")
    
    print(f"\n" + "=" * 50)
    print("INSTRUÇÕES:")
    print("=" * 50)
    
    print(f"\n1. COMPUTADOR COM BALANÇA (Sytembalança sem simulador de teste.py):")
    print(f"   - Clique em 'Config IP'")
    print(f"   - Digite o IP do computador receptor: {main_ip}")
    print(f"   - Porta: 8888")
    
    print(f"\n2. COMPUTADOR RECEPTOR (receptor_peso.py):")
    print(f"   - Execute o receptor_peso.py")
    print(f"   - Clique 'Iniciar Servidor'")
    print(f"   - IP será: {main_ip}")
    print(f"   - Porta será: 8888")
    
    print(f"\n3. CONEXÃO:")
    print(f"   - No sistema da balança, clique 'Conectar Terminal Remoto'")
    print(f"   - Os dados aparecerão em tempo real no receptor")
    
    print(f"\n" + "=" * 50)
    print("DICA: Se os computadores estão na mesma rede,")
    print(f"use o IP: {main_ip}")
    print("=" * 50)
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()