import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import re
import time
import socket
import json

# Configura o tema do CustomTkinter
ctk.set_appearance_mode("dark")  # Pode ser "Light", "Dark", "System"
ctk.set_default_color_theme("blue")  # Pode ser "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurações da Janela ---
        self.title("Sistema de Pesagem de Veículos")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Variáveis de Controle ---
        self.ser = None
        self.running = False
        self.thread = None
        self.current_mode = 1  # 1 = Pesagem contínua, 2 = Captura impressão
        
        # --- Variáveis de Rede ---
        self.client_socket = None
        self.network_enabled = False
        self.host = '127.0.0.1'
        self.port = 8888
        self.auto_print = ctk.BooleanVar(value=False)  # Controle de impressão automática
        
        # --- Interface ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=280)  # Painel esquerdo fixo e menor
        self.main_frame.grid_columnconfigure(1, weight=1)  # Painel direito expansível
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Título
        self.label_titulo = ctk.CTkLabel(self.main_frame, text="SISTEMA DE PESAGEM DE VEÍCULOS", font=("Arial", 28, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Painel esquerdo - Controles (menor)
        self.left_panel = ctk.CTkFrame(self.main_frame, width=280)
        self.left_panel.grid(row=1, column=0, padx=(0, 10), sticky="ns")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_propagate(False)  # Mantém tamanho fixo

        # Seletor de modo
        self.mode_frame = ctk.CTkFrame(self.left_panel)
        self.mode_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.mode_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.mode_frame, text="MODO DE OPERAÇÃO", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(8, 3))
        
        self.button_modo1 = ctk.CTkButton(self.mode_frame, text="Pesagem Contínua", command=self.set_mode1, font=("Arial", 11), height=30)
        self.button_modo1.grid(row=1, column=0, padx=8, pady=2, sticky="ew")
        
        self.button_modo2 = ctk.CTkButton(self.mode_frame, text="Captura Impressão", command=self.set_mode2, font=("Arial", 11), height=30)
        self.button_modo2.grid(row=2, column=0, padx=8, pady=(2, 8), sticky="ew")
        
        # Botões de rede
        self.network_frame = ctk.CTkFrame(self.left_panel)
        self.network_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.network_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.network_frame, text="TERMINAL REMOTO", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(8, 3))
        
        self.button_config_rede = ctk.CTkButton(self.network_frame, text="Config IP", command=self.config_network, font=("Arial", 11), height=30)
        self.button_config_rede.grid(row=1, column=0, padx=8, pady=(2, 8), sticky="ew")
        
        # Status
        self.status_frame = ctk.CTkFrame(self.left_panel)
        self.status_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.status_frame, text="STATUS", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(10, 5))
        
        self.label_status = ctk.CTkLabel(self.status_frame, text="Desconectado", font=("Arial", 10), text_color="red", wraplength=250, justify="left")
        self.label_status.grid(row=1, column=0, pady=2, sticky="ew", padx=10)
        
        self.label_network_status = ctk.CTkLabel(self.status_frame, text="Terminal: Desconectado", font=("Arial", 10), text_color="gray", wraplength=250, justify="left")
        self.label_network_status.grid(row=2, column=0, pady=(2, 10), sticky="ew", padx=10)
        
        # Opção de impressão automática
        self.print_frame = ctk.CTkFrame(self.left_panel)
        self.print_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.print_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.print_frame, text="CONFIGURAÇÃO DE IMPRESSÃO", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(10, 5))
        
        self.checkbox_auto_print = ctk.CTkCheckBox(self.print_frame, text="Impressão Automática", variable=self.auto_print, font=("Arial", 12))
        self.checkbox_auto_print.grid(row=1, column=0, pady=(5, 10), sticky="w", padx=10)

        # Painel direito - Área de exibição
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # Área de exibição (muda conforme o modo)
        self.display_frame = self.right_panel

        # Widgets do Modo 1 (Pesagem)
        self.label_peso = ctk.CTkLabel(self.display_frame, text="0.00 kg", font=("Arial", 90, "bold"))
        
        # Widgets do Modo 2 (Impressão) - Layout similar ao receptor_peso.py
        # Cabeçalho do log de impressão
        self.impressao_header = ctk.CTkFrame(self.display_frame)
        self.impressao_header.grid_columnconfigure(1, weight=1)
        
        # Área de texto grande para impressões
        self.text_impressao = ctk.CTkTextbox(self.display_frame, font=("Courier", 12))
        self.label_aguardando = ctk.CTkLabel(self.display_frame, text="Aguardando impressão...\nAperte a tecla 'I' na balança", font=("Arial", 20), text_color="orange")

        # Botão limpar (só no modo 2) - será criado no set_mode2
        

        


        # Inicializa no modo 1
        self.set_mode1()
        
        # Lidar com o fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- Funções de Modo ---
    def set_mode1(self):
        """Configura o modo 1 - Pesagem contínua."""
        if self.running:
            self.stop_reading()
        
        self.current_mode = 1
        self.button_modo1.configure(fg_color=("#1f538d", "#14375e"))  # Azul escuro (ativo)
        self.button_modo2.configure(fg_color=("#3a7ebf", "#1f538d"))  # Azul claro (inativo)
        
        # Esconde widgets do modo 2
        self.impressao_header.grid_remove()
        self.text_impressao.grid_remove()
        self.label_aguardando.grid_remove()
        
        # Mostra widgets do modo 1 - centralizado
        self.label_peso.grid(row=1, column=0, sticky="")
        
        # Inicia automaticamente a pesagem
        self.start_reading()
        
    def set_mode2(self):
        """Configura o modo 2 - Captura de impressão."""
        if self.running:
            self.stop_reading()
        
        self.current_mode = 2
        self.button_modo2.configure(fg_color=("#1f538d", "#14375e"))  # Azul escuro (ativo)
        self.button_modo1.configure(fg_color=("#3a7ebf", "#1f538d"))  # Azul claro (inativo)
        
        # Esconde widgets do modo 1
        self.label_peso.grid_remove()
        
        # Mostra widgets do modo 2 com layout similar ao receptor_peso.py
        # Cabeçalho com título e botão limpar
        self.impressao_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        ctk.CTkLabel(self.impressao_header, text="DADOS DE IMPRESSÃO CAPTURADOS", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10, padx=10)
        
        # Frame para os botões
        buttons_frame = ctk.CTkFrame(self.impressao_header)
        buttons_frame.grid(row=0, column=1, pady=10, padx=10, sticky="e")
        
        self.button_print_impressao = ctk.CTkButton(buttons_frame, text="Imprimir", command=self.print_impressao, font=("Arial", 12), height=30, width=80, fg_color="green")
        self.button_print_impressao.pack(side="left", padx=(0, 5))
        
        self.button_limpar = ctk.CTkButton(buttons_frame, text="Limpar Dados", command=self.clear_print_data, font=("Arial", 12), height=30, width=100)
        self.button_limpar.pack(side="left")
        
        # Área de texto grande
        self.text_impressao.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        # Label de status na parte inferior
        self.label_aguardando.grid(row=2, column=0, pady=10)
        
        # Inicia automaticamente a captura
        self.start_reading()
        
    def clear_print_data(self):
        """Limpa os dados de impressão."""
        self.text_impressao.delete("1.0", "end")
        self.label_aguardando.configure(text="Aguardando impressão...\nAperte a tecla 'I' na balança", text_color="orange")
    
    def print_impressao(self):
        """Imprime os dados de impressão na impressora fiscal."""
        try:
            import tempfile
            import os
            
            # Obtém o conteúdo do log
            log_content = self.text_impressao.get("1.0", "end-1c")
            
            if not log_content.strip():
                # Mostra mensagem se não há dados para imprimir
                error_window = ctk.CTkToplevel(self)
                error_window.title("Aviso")
                error_window.geometry("300x120")
                error_window.transient(self)
                error_window.grab_set()
                
                # Centraliza em relação à janela principal
                self.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() // 2) - (300 // 2)
                y = self.winfo_y() + (self.winfo_height() // 2) - (120 // 2)
                error_window.geometry(f"300x120+{x}+{y}")
                
                ctk.CTkLabel(error_window, text="Não há dados para imprimir!", font=("Arial", 14)).pack(pady=20)
                ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
                return
            
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                # Cabeçalho do relatório
                header = f"RELATÓRIO DE IMPRESSÕES CAPTURADAS\n"
                header += f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
                header += "=" * 60 + "\n\n"
                
                temp_file.write(header)
                temp_file.write(log_content)
                temp_file_path = temp_file.name
            
            # Envia para impressora padrão do Windows
            os.startfile(temp_file_path, "print")
            
            # Mostra confirmação centralizada na janela principal
            success_window = ctk.CTkToplevel(self)
            success_window.title("Sucesso")
            success_window.geometry("300x120")
            success_window.transient(self)
            success_window.grab_set()
            
            # Centraliza em relação à janela principal
            self.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (300 // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (120 // 2)
            success_window.geometry(f"300x120+{x}+{y}")
            
            ctk.CTkLabel(success_window, text="Documento enviado para impressão!", font=("Arial", 14), text_color="green").pack(pady=20)
            ctk.CTkButton(success_window, text="OK", command=success_window.destroy).pack(pady=10)
            
            # Remove arquivo temporário após 10 segundos
            self.after(10000, lambda: self.remove_temp_file(temp_file_path))
            
        except Exception as e:
            # Mostra erro
            error_window = ctk.CTkToplevel(self)
            error_window.title("Erro")
            error_window.geometry("400x150")
            error_window.transient(self)
            error_window.grab_set()
            
            # Centraliza em relação à janela principal
            self.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (400 // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (150 // 2)
            error_window.geometry(f"400x150+{x}+{y}")
            
            ctk.CTkLabel(error_window, text=f"Erro ao imprimir:\n{str(e)}", font=("Arial", 12), text_color="red").pack(pady=20)
            ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
    
    def auto_print_data(self, print_data, time_str):
        """Imprime automaticamente os dados recebidos."""
        try:
            import tempfile
            import os
            
            # Cria arquivo temporário para impressão automática
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                header = f"IMPRESSÃO AUTOMÁTICA\n"
                header += f"Data/Hora: {time_str}\n"
                header += "=" * 50 + "\n\n"
                
                temp_file.write(header)
                temp_file.write(print_data)
                temp_file_path = temp_file.name
            
            # Envia para impressora
            os.startfile(temp_file_path, "print")
            
            # Remove arquivo após 5 segundos
            self.after(5000, lambda: self.remove_temp_file(temp_file_path))
            
        except Exception as e:
            print(f"Erro na impressão automática: {e}")
    
    def remove_temp_file(self, file_path):
        """Remove arquivo temporário."""
        try:
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    
    # --- Funções de Rede ---
    def connect_network(self):
        """Conecta ao terminal remoto."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.network_enabled = True
            
            self.label_network_status.configure(text=f"Terminal Remoto: Conectado ({self.host}:{self.port})", text_color="green")
            
            print(f"Conectado ao terminal remoto {self.host}:{self.port}")
            
        except Exception as e:
            self.label_network_status.configure(text=f"Erro de conexão: {e}", text_color="red")
            print(f"Erro ao conectar terminal remoto: {e}")
            self.client_socket = None
    
    def disconnect_network(self):
        """Desconecta do terminal remoto."""
        self.network_enabled = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        self.label_network_status.configure(text=f"Terminal Remoto: Desconectado ({self.host}:{self.port})", text_color="gray")
        
        print("Desconectado do terminal remoto")
    
    def send_weight_data(self, peso, mode_info=""):
        """Envia dados de peso para o terminal remoto."""
        if not self.network_enabled or not self.client_socket:
            return
        
        try:
            data = {
                'peso': peso,
                'timestamp': time.time(),
                'unidade': 'kg',
                'modo': self.current_mode,
                'info': mode_info
            }
            
            message = json.dumps(data) + '\n'
            self.client_socket.send(message.encode('utf-8'))
            
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")
            self.disconnect_network()
    
    def send_print_data(self, print_data):
        """Envia dados de impressão para o terminal remoto."""
        if not self.network_enabled or not self.client_socket:
            return
        
        try:
            data = {
                'tipo': 'impressao',
                'dados': print_data,
                'timestamp': time.time(),
                'modo': 2
            }
            
            message = json.dumps(data) + '\n'
            self.client_socket.send(message.encode('utf-8'))
            
        except Exception as e:
            print(f"Erro ao enviar dados de impressão: {e}")
            self.disconnect_network()
    
    def config_network(self):
        """Abre janela para configurar IP e porta do terminal remoto."""
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configuração de Rede")
        config_window.geometry("550x550")
        config_window.resizable(False, False)
        config_window.transient(self)
        config_window.grab_set()
        
        config_window.after(100, lambda: config_window.lift())
        
        main_frame = ctk.CTkFrame(config_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="CONFIGURAÇÃO DO TERMINAL REMOTO", font=("Arial", 18, "bold")).pack(pady=(10, 20))
        
        ctk.CTkLabel(main_frame, text="IP do computador com receptor_peso.py:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0, 5))
        entry_host = ctk.CTkEntry(main_frame, font=("Arial", 12), height=35)
        entry_host.insert(0, self.host)
        entry_host.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(main_frame, text="Porta (padrão 8888):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0, 5))
        entry_port = ctk.CTkEntry(main_frame, font=("Arial", 12), height=35)
        entry_port.insert(0, str(self.port))
        entry_port.pack(fill="x", padx=10, pady=(0, 20))
        
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        info_text = "COMO DESCOBRIR O IP:\n\n"
        info_text += "1. No computador com receptor_peso.py:\n"
        info_text += "   - Abra o Prompt de Comando (cmd)\n"
        info_text += "   - Digite: ipconfig\n"
        info_text += "   - Procure por 'Endereço IPv4'\n\n"
        info_text += "2. Exemplo: 192.168.1.100\n"
        info_text += "3. Use a mesma porta (8888) nos dois sistemas\n\n"
        info_text += "DICA: Use o botão 'IP Local' para preencher\n"
        info_text += "automaticamente com o IP deste computador."
        
        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 11), justify="left").pack(padx=15, pady=15)
        
        def save_config():
            try:
                self.host = entry_host.get().strip()
                self.port = int(entry_port.get().strip())
                
                if not self.host:
                    self.host = '127.0.0.1'
                
                self.label_network_status.configure(
                    text=f"Terminal Remoto: Configurado para {self.host}:{self.port}", 
                    text_color="blue"
                )
                
                config_window.destroy()
                print(f"Configuração salva: {self.host}:{self.port}")
                
            except ValueError:
                error_window = ctk.CTkToplevel(config_window)
                error_window.title("Erro")
                error_window.geometry("300x100")
                error_window.transient(config_window)
                ctk.CTkLabel(error_window, text="Porta deve ser um número!", text_color="red").pack(pady=20)
                ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
        
        def get_local_ip():
            try:
                import socket as sock
                s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                entry_host.delete(0, "end")
                entry_host.insert(0, local_ip)
            except:
                entry_host.delete(0, "end")
                entry_host.insert(0, "192.168.1.100")
        
        def connect_and_close():
            save_config()
            self.connect_network()
        
        def disconnect_and_close():
            self.disconnect_network()
            config_window.destroy()
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        btn_ip_local = ctk.CTkButton(button_frame, text="IP Local", command=get_local_ip, font=("Arial", 11), height=40, width=120)
        btn_ip_local.grid(row=0, column=0, padx=2, pady=5, sticky="ew")
        
        btn_salvar = ctk.CTkButton(button_frame, text="Salvar", command=save_config, font=("Arial", 11), height=40, width=120)
        btn_salvar.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        
        btn_conectar = ctk.CTkButton(button_frame, text="Conectar", command=connect_and_close, font=("Arial", 11), height=40, width=120, fg_color="green")
        btn_conectar.grid(row=0, column=2, padx=2, pady=5, sticky="ew")
        
        btn_desconectar = ctk.CTkButton(button_frame, text="Desconectar", command=disconnect_and_close, font=("Arial", 11), height=40, width=120, fg_color="red")
        btn_desconectar.grid(row=0, column=3, padx=2, pady=5, sticky="ew")

    # --- Funções de Lógica ---
    def find_serial_port(self):
        """Tenta encontrar a porta serial correta da balança."""
        ports = serial.tools.list_ports.comports()
        print("Portas disponíveis:")
        
        for port, desc, hwid in sorted(ports):
            print(f"  {port}: {desc} [{hwid}]")
            
        # Prioriza portas USB e Serial
        for port, desc, hwid in sorted(ports):
            if any(keyword in desc.upper() for keyword in ["USB", "SERIAL", "COM", "UART"]):
                print(f"Selecionada porta: {port} - {desc}")
                return port
        
        # Se não encontrar, retorna a primeira porta disponível
        if ports:
            port = ports[0][0]
            print(f"Usando primeira porta disponível: {port}")
            return port
            
        return None

    def start_reading(self):
        """Inicia a leitura dos dados da balança em uma thread separada."""
        if self.running:
            return

        port = self.find_serial_port()
        if not port:
            self.label_status.configure(text="Balança não encontrada!", text_color="orange")
            return

        try:
            # Configurações mais robustas para a porta serial
            self.ser = serial.Serial(
                port=port,
                baudrate=9600,  # Teste também: 4800, 19200, 38400
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Limpa buffers
            self.ser.flushInput()
            self.ser.flushOutput()
            
            self.running = True
            self.thread = threading.Thread(target=self.read_scale_data, daemon=True)
            self.thread.start()
            
            self.label_status.configure(text=f"Conectado: {port}", text_color="green")
            
            # Atualiza indicador do modo 2
            if self.current_mode == 2:
                self.label_aguardando.configure(
                    text="Conectado! Aguardando impressão...\nAperte a tecla 'I' na balança", 
                    text_color="orange"
                )
            
            print(f"Conectado na porta {port} com sucesso! Modo: {self.current_mode}")
            
        except serial.SerialException as e:
            self.label_status.configure(text=f"Erro: {e}", text_color="red")
            print(f"Erro de conexão: {e}")
            self.ser = None

    def stop_reading(self):
        """Para a leitura e fecha a conexão."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
        
        self.label_status.configure(text="Desconectado", text_color="red")
        
        # Reseta indicador do modo 2
        if self.current_mode == 2:
            self.label_aguardando.configure(
                text="Aguardando impressão...\nAperte a tecla 'I' na balança", 
                text_color="orange"
            )

    def read_scale_data(self):
        """Loop que lê os dados da balança conforme o modo selecionado."""
        buffer = ""
        print_buffer = ""
        last_data_time = time.time()
        
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    # Lê dados disponíveis
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                        buffer += data
                        last_data_time = time.time()
                        
                        if self.current_mode == 1:
                            # Modo 1: Pesagem contínua
                            while '\n' in buffer or '\r' in buffer:
                                if '\n' in buffer:
                                    line, buffer = buffer.split('\n', 1)
                                else:
                                    line, buffer = buffer.split('\r', 1)
                                
                                line = line.strip()
                                if line:
                                    print(f"Modo 1 - Dados: '{line}'")  # Debug
                                    self.process_weight_data(line)
                        
                        elif self.current_mode == 2:
                            # Modo 2: Captura de impressão
                            print_buffer += data
                            
                            # Atualiza indicador de recebimento
                            if data.strip():
                                self.after(0, lambda: self.label_aguardando.configure(
                                    text="Recebendo dados...\nNão aperte 'I' novamente", 
                                    text_color="green"
                                ))
                    
                    # No modo 2, verifica se parou de receber dados (fim da impressão)
                    elif self.current_mode == 2 and print_buffer and (time.time() - last_data_time > 2):
                        # Processa dados completos da impressão
                        self.process_print_data(print_buffer)
                        print_buffer = ""
                        
                    # Fallback readline para modo 1
                    elif self.current_mode == 1:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            print(f"Modo 1 - Readline: '{line}'")  # Debug
                            self.process_weight_data(line)
                            
                except serial.SerialException as e:
                    print(f"Erro de leitura serial: {e}")
                    self.after(0, lambda: self.label_status.configure(text=f"Erro de leitura: {e}", text_color="red"))
                    self.stop_reading()
                    break
                except Exception as e:
                    print(f"Erro inesperado: {e}")
                    
            time.sleep(0.05)
    
    def process_weight_data(self, line):
        """Processa os dados de peso recebidos (Modo 1)."""
        try:
            patterns = [
                r'[-+]?\d+\.\d+',
                r'[-+]?\d+',
                r'\d+\.\d+',
                r'\d+',
            ]
            
            peso = None
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        peso = float(match.group())
                        break
                    except ValueError:
                        continue
            
            if peso is not None:
                self.after(0, lambda p=peso: self.update_label(f"{p:.2f} kg"))
                # Envia dados para terminal remoto
                self.send_weight_data(peso, "pesagem_continua")
                print(f"Peso processado: {peso:.2f} kg")
            else:
                print(f"Não foi possível extrair peso de: '{line}'")
                
        except Exception as e:
            print(f"Erro ao processar dados: {e}")
    
    def process_print_data(self, data):
        """Processa os dados completos da impressão (Modo 2)."""
        try:
            # Limpa e formata os dados
            formatted_data = data.replace('\r\n', '\n').replace('\r', '\n')
            
            # Adiciona timestamp
            timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
            header = f"\n{'='*50}\nIMPRESSÃO RECEBIDA - {timestamp}\n{'='*50}\n"
            
            full_data = header + formatted_data + "\n" + "="*50 + "\n"
            
            # Atualiza a interface
            self.after(0, lambda: self.update_print_display(full_data))
            
            # Envia dados de impressão para terminal remoto
            self.send_print_data(formatted_data)
            
            print(f"Dados de impressão processados ({len(data)} bytes)")
            print(f"Conteúdo: {repr(data[:200])}...")  # Debug
            
        except Exception as e:
            print(f"Erro ao processar dados de impressão: {e}")
    
    def update_print_display(self, data):
        """Atualiza a exibição dos dados de impressão."""
        try:
            self.text_impressao.insert("end", data)
            self.text_impressao.see("end")
            self.label_aguardando.configure(
                text="Dados recebidos!\nAperte 'I' novamente para nova captura", 
                text_color="blue"
            )
            
            # Impressão automática se habilitada
            if self.auto_print.get():
                time_str = time.strftime("%d/%m/%Y %H:%M:%S")
                self.auto_print_data(data, time_str)
                
        except Exception as e:
            print(f"Erro ao atualizar display: {e}")

    def update_label(self, text):
        """Atualiza o rótulo do peso na interface principal."""
        try:
            self.label_peso.configure(text=text)
        except Exception as e:
            print(f"Erro ao atualizar label: {e}")

    def on_closing(self):
        """Função chamada ao fechar a janela para garantir que a thread seja encerrada."""
        self.stop_reading()
        self.disconnect_network()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()