import serial
import serial.tools.list_ports
import time

def test_serial_communication():
    """Testa a comunicação serial com diferentes configurações."""
    
    # Lista todas as portas disponíveis
    print("=== PORTAS SERIAIS DISPONÍVEIS ===")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("Nenhuma porta serial encontrada!")
        return
    
    for i, (port, desc, hwid) in enumerate(ports):
        print(f"{i+1}. {port}: {desc} [{hwid}]")
    
    # Permite ao usuário escolher a porta
    try:
        choice = int(input("\nEscolha o número da porta (ou 0 para testar todas): ")) - 1
        if choice == -1:
            test_ports = [port[0] for port in ports]
        else:
            test_ports = [ports[choice][0]]
    except (ValueError, IndexError):
        print("Escolha inválida!")
        return
    
    # Diferentes configurações de baud rate para testar
    baud_rates = [9600, 4800, 19200, 38400, 57600, 115200]
    
    for port in test_ports:
        print(f"\n=== TESTANDO PORTA {port} ===")
        
        for baud_rate in baud_rates:
            print(f"\nTestando {port} com baud rate {baud_rate}...")
            
            try:
                ser = serial.Serial(
                    port=port,
                    baudrate=baud_rate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=2,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False
                )
                
                # Limpa buffers
                ser.flushInput()
                ser.flushOutput()
                
                print(f"Conectado! Aguardando dados por 10 segundos...")
                
                start_time = time.time()
                data_received = False
                
                while time.time() - start_time < 10:
                    if ser.in_waiting > 0:
                        try:
                            data = ser.read(ser.in_waiting)
                            decoded_data = data.decode('utf-8', errors='ignore').strip()
                            if decoded_data:
                                print(f"DADOS RECEBIDOS: '{decoded_data}'")
                                print(f"BYTES RAW: {data}")
                                data_received = True
                        except Exception as e:
                            print(f"Erro ao decodificar: {e}")
                            print(f"BYTES RAW: {data}")
                    
                    # Também tenta readline
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(f"READLINE: '{line}'")
                            data_received = True
                    except:
                        pass
                    
                    time.sleep(0.1)
                
                ser.close()
                
                if data_received:
                    print(f"✓ SUCESSO com {port} @ {baud_rate} baud!")
                    
                    # Pergunta se quer continuar testando
                    continue_test = input("Dados recebidos! Continuar testando outras configurações? (s/n): ")
                    if continue_test.lower() != 's':
                        return
                else:
                    print(f"✗ Nenhum dado recebido com {port} @ {baud_rate} baud")
                
            except serial.SerialException as e:
                print(f"✗ Erro ao conectar: {e}")
            except Exception as e:
                print(f"✗ Erro inesperado: {e}")

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DE COMUNICAÇÃO SERIAL ===")
    print("Este script irá testar diferentes configurações para encontrar")
    print("a configuração correta da sua balança.\n")
    
    test_serial_communication()
    
    print("\n=== DICAS ===")
    print("1. Certifique-se de que a balança está ligada")
    print("2. Verifique se o cabo está conectado corretamente")
    print("3. Alguns dispositivos precisam de um comando para iniciar o envio de dados")
    print("4. Anote a porta e baud rate que funcionaram para usar no sistema principal")