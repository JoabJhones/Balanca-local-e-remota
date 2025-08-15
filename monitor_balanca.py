import serial
import serial.tools.list_ports
import time
import re

def monitor_scale_data():
    """Monitor simples para visualizar dados da balança em tempo real."""
    
    # Lista portas disponíveis
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("Nenhuma porta serial encontrada!")
        return
    
    print("Portas disponíveis:")
    for i, (port, desc, hwid) in enumerate(ports):
        print(f"{i+1}. {port}: {desc}")
    
    # Escolhe a porta
    try:
        choice = int(input("Escolha a porta: ")) - 1
        selected_port = ports[choice][0]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        return
    
    # Escolhe o baud rate
    baud_rate = input("Digite o baud rate (padrão 9600): ").strip()
    if not baud_rate:
        baud_rate = 9600
    else:
        baud_rate = int(baud_rate)
    
    try:
        # Conecta na porta
        ser = serial.Serial(
            port=selected_port,
            baudrate=baud_rate,
            timeout=1
        )
        
        print(f"\nConectado em {selected_port} @ {baud_rate} baud")
        print("Monitorando dados... (Ctrl+C para parar)\n")
        print("-" * 50)
        
        buffer = ""
        
        while True:
            try:
                # Lê dados disponíveis
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Processa linhas completas
                    while '\n' in buffer or '\r' in buffer:
                        if '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                        else:
                            line, buffer = buffer.split('\r', 1)
                        
                        line = line.strip()
                        if line:
                            timestamp = time.strftime("%H:%M:%S")
                            print(f"[{timestamp}] RAW: '{line}'")
                            
                            # Tenta extrair peso
                            patterns = [
                                r'[-+]?\d+\.\d+',
                                r'[-+]?\d+',
                                r'\d+\.\d+',
                                r'\d+'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, line)
                                if match:
                                    try:
                                        peso = float(match.group())
                                        print(f"[{timestamp}] PESO: {peso:.2f} kg")
                                        break
                                    except ValueError:
                                        continue
                
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                print("\nParando monitoramento...")
                break
            except Exception as e:
                print(f"Erro: {e}")
                break
        
        ser.close()
        print("Conexão fechada.")
        
    except serial.SerialException as e:
        print(f"Erro de conexão: {e}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    monitor_scale_data()