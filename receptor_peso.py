import socket
import json
import threading
import customtkinter as ctk
import time
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ReceptorPeso(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Receptor de Peso - Sistema Remoto")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Variáveis de controle
        self.server_socket = None
        self.client_socket = None
        self.running = False
        self.server_thread = None
        
        # Configurações de rede
        self.host = '0.0.0.0'  # Aceita conexões de qualquer IP
        self.port = 8888
        
        # Variáveis de controle
        self.total_received = 0
        self.peso_min = None
        self.peso_max = None
        self.total_impressoes = 0
        self.total_pesagens = 0
        self.auto_print = ctk.BooleanVar(value=False)  # Controle de impressão automática
        
        # Interface
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(self.main_frame, text="RECEPTOR DE PESO - SISTEMA REMOTO", font=("Arial", 28, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=2, pady=(10, 20))
        
        # Painel esquerdo - Informações principais
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.grid(row=1, column=0, padx=(0, 10), sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Peso atual
        self.peso_frame = ctk.CTkFrame(self.left_panel)
        self.peso_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.peso_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.peso_frame, text="PESO ATUAL", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(10, 5))
        self.label_peso = ctk.CTkLabel(self.peso_frame, text="Aguardando...", font=("Arial", 48, "bold"), text_color="#00ff00")
        self.label_peso.grid(row=1, column=0, pady=(5, 10))
        
        # Informações de conexão
        self.info_frame = ctk.CTkFrame(self.left_panel)
        self.info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.info_frame, text="INFORMAÇÕES DE CONEXÃO", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(10, 5))
        
        self.label_timestamp = ctk.CTkLabel(self.info_frame, text="Última atualização: --", font=("Arial", 12))
        self.label_timestamp.grid(row=1, column=0, pady=2, sticky="w", padx=10)
        
        self.label_mode = ctk.CTkLabel(self.info_frame, text="Modo: --", font=("Arial", 12))
        self.label_mode.grid(row=2, column=0, pady=2, sticky="w", padx=10)
        
        self.label_client_info = ctk.CTkLabel(self.info_frame, text="Cliente: Desconectado", font=("Arial", 12))
        self.label_client_info.grid(row=3, column=0, pady=2, sticky="w", padx=10)
        
        self.label_total_received = ctk.CTkLabel(self.info_frame, text="Total recebido: 0 dados", font=("Arial", 12))
        self.label_total_received.grid(row=4, column=0, pady=(2, 10), sticky="w", padx=10)
        
        # Estatísticas
        self.stats_frame = ctk.CTkFrame(self.left_panel)
        self.stats_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(self.stats_frame, text="ESTATÍSTICAS", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5))
        
        self.label_peso_min = ctk.CTkLabel(self.stats_frame, text="Mín: --", font=("Arial", 11))
        self.label_peso_min.grid(row=1, column=0, pady=2, sticky="w", padx=10)
        
        self.label_peso_max = ctk.CTkLabel(self.stats_frame, text="Máx: --", font=("Arial", 11))
        self.label_peso_max.grid(row=1, column=1, pady=2, sticky="w", padx=10)
        
        self.label_impressoes = ctk.CTkLabel(self.stats_frame, text="Impressões: 0", font=("Arial", 11))
        self.label_impressoes.grid(row=2, column=0, pady=(2, 10), sticky="w", padx=10)
        
        self.label_pesagens = ctk.CTkLabel(self.stats_frame, text="Pesagens: 0", font=("Arial", 11))
        self.label_pesagens.grid(row=2, column=1, pady=(2, 10), sticky="w", padx=10)
        
        # Opção de impressão automática
        self.print_frame = ctk.CTkFrame(self.left_panel)
        self.print_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.print_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.print_frame, text="CONFIGURAÇÃO DE IMPRESSÃO", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(10, 5))
        
        self.checkbox_auto_print = ctk.CTkCheckBox(self.print_frame, text="Impressão Automática", variable=self.auto_print, font=("Arial", 12))
        self.checkbox_auto_print.grid(row=1, column=0, pady=(5, 10), sticky="w", padx=10)
        
        # Painel direito - Log de dados
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho do log
        self.log_header = ctk.CTkFrame(self.right_panel)
        self.log_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.log_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.log_header, text="LOG DE DADOS RECEBIDOS", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10, padx=10)
        
        # Frame para os botões
        buttons_frame = ctk.CTkFrame(self.log_header)
        buttons_frame.grid(row=0, column=1, pady=10, padx=10, sticky="e")
        
        self.button_print = ctk.CTkButton(buttons_frame, text="Imprimir", command=self.print_log, font=("Arial", 12), height=30, width=80, fg_color="green")
        self.button_print.pack(side="left", padx=(0, 5))
        
        self.button_clear_log = ctk.CTkButton(buttons_frame, text="Limpar Log", command=self.clear_log, font=("Arial", 12), height=30, width=100)
        self.button_clear_log.pack(side="left")
        
        # Área de log
        self.text_log = ctk.CTkTextbox(self.right_panel, font=("Courier", 11))
        self.text_log.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        self.button_iniciar = ctk.CTkButton(self.main_frame, text="Iniciar Servidor", command=self.start_server, font=("Arial", 16), height=40)
        # Botões de controle
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        self.control_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.button_iniciar = ctk.CTkButton(self.control_frame, text="Iniciar Servidor", command=self.start_server, font=("Arial", 16), height=40)
        self.button_iniciar.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.button_parar = ctk.CTkButton(self.control_frame, text="Parar Servidor", command=self.stop_server, font=("Arial", 16), height=40, state="disabled")
        self.button_parar.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.button_config = ctk.CTkButton(self.control_frame, text="Configurar Rede", command=self.open_config, font=("Arial", 16), height=40)
        self.button_config.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        # Status
        self.label_status = ctk.CTkLabel(self.main_frame, text="Status: Servidor parado", font=("Arial", 14), text_color="red")
        self.label_status.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_server(self):
        """Inicia o servidor para receber dados."""
        if self.running:
            return
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            
            self.running = True
            self.server_thread = threading.Thread(target=self.accept_connections)
            self.server_thread.start()
            
            self.label_status.configure(text=f"Status: Servidor ativo em {self.host}:{self.port}", text_color="green")
            self.button_iniciar.configure(state="disabled")
            self.button_parar.configure(state="normal")
            
        except Exception as e:
            self.label_status.configure(text=f"Erro: {e}", text_color="red")
    
    def accept_connections(self):
        """Aceita conexões de clientes."""
        while self.running:
            try:
                self.client_socket, addr = self.server_socket.accept()
                self.after(0, lambda a=addr: self.update_client_info(f"Conectado: {a[0]}:{a[1]}"))
                self.after(0, lambda: self.label_status.configure(text=f"Status: Cliente conectado", text_color="blue"))
                self.handle_client()
            except Exception as e:
                if self.running:
                    print(f"Erro ao aceitar conexão: {e}")
                break
    
    def handle_client(self):
        """Processa dados do cliente."""
        buffer = ""
        while self.running and self.client_socket:
            try:
                # Timeout menor para melhor responsividade
                self.client_socket.settimeout(0.1)
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                # Processa IMEDIATAMENTE cada linha recebida
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        # Processa dados em tempo real
                        self.process_weight_data(line.strip())
                        
            except socket.timeout:
                # Timeout normal, continua o loop
                continue
            except Exception as e:
                print(f"Erro ao receber dados: {e}")
                break
        
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.after(0, lambda: self.update_client_info("Desconectado"))
    
    def process_weight_data(self, data):
        """Processa os dados recebidos."""
        try:
            received_data = json.loads(data)
            self.total_received += 1
            
            if received_data.get('tipo') == 'impressao':
                # Dados de impressão
                print_data = received_data.get('dados', '')
                timestamp = received_data.get('timestamp', time.time())
                self.total_impressoes += 1
                # Atualiza IMEDIATAMENTE na thread principal
                self.after(0, lambda pd=print_data, t=timestamp: self.update_print_display(pd, t))
                
            else:
                # Dados de peso
                peso = received_data.get('peso', 0)
                timestamp = received_data.get('timestamp', time.time())
                unidade = received_data.get('unidade', 'kg')
                modo = received_data.get('modo', 1)
                info = received_data.get('info', '')
                self.total_pesagens += 1
                
                # Atualiza estatísticas
                if self.peso_min is None or peso < self.peso_min:
                    self.peso_min = peso
                if self.peso_max is None or peso > self.peso_max:
                    self.peso_max = peso
                
                # Atualiza IMEDIATAMENTE na thread principal
                self.after(0, lambda p=peso, t=timestamp, u=unidade, m=modo, i=info: self.update_weight_display(p, t, u, m, i))
            
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON: {data}")
    
    def update_client_info(self, info):
        """Atualiza informações do cliente."""
        self.label_client_info.configure(text=f"Cliente: {info}")
    
    def update_weight_display(self, peso, timestamp, unidade, modo, info):
        """Atualiza a exibição com os dados de peso."""
        # Atualiza peso principal
        self.label_peso.configure(text=f"{peso:.2f} {unidade}")
        
        # Atualiza informações
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S - %d/%m/%Y")
        self.label_timestamp.configure(text=f"Última atualização: {time_str}")
        
        mode_text = f"Modo {modo}: {'Pesagem Contínua' if modo == 1 else 'Captura Impressão'}"
        if info:
            mode_text += f" ({info})"
        self.label_mode.configure(text=mode_text)
        
        # Atualiza estatísticas
        self.update_statistics()
        
        # Adiciona ao log
        log_entry = f"[{time_str}] PESO: {peso:.2f} {unidade} (Modo {modo})\n"
        self.text_log.insert("end", log_entry)
        self.text_log.see("end")
    
    def update_print_display(self, print_data, timestamp):
        """Atualiza a exibição com os dados de impressão."""
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%d/%m/%Y %H:%M:%S")
        
        # Adiciona ao log
        log_entry = f"\n[{time_str}] IMPRESSÃO RECEBIDA:\n"
        log_entry += "-" * 50 + "\n"
        log_entry += print_data + "\n"
        log_entry += "-" * 50 + "\n\n"
        
        self.text_log.insert("end", log_entry)
        self.text_log.see("end")
        
        # Atualiza estatísticas
        self.update_statistics()
        
        # Impressão automática se habilitada
        if self.auto_print.get():
            self.auto_print_data(print_data, time_str)
    
    def update_statistics(self):
        """Atualiza as estatísticas exibidas."""
        self.label_total_received.configure(text=f"Total recebido: {self.total_received} dados")
        
        if self.peso_min is not None:
            self.label_peso_min.configure(text=f"Mín: {self.peso_min:.2f} kg")
        if self.peso_max is not None:
            self.label_peso_max.configure(text=f"Máx: {self.peso_max:.2f} kg")
            
        self.label_impressoes.configure(text=f"Impressões: {self.total_impressoes}")
        self.label_pesagens.configure(text=f"Pesagens: {self.total_pesagens}")
    
    def clear_log(self):
        """Limpa o log de dados."""
        self.text_log.delete("1.0", "end")
        self.text_log.insert("1.0", "Log limpo.\n\n")
    
    def print_log(self):
        """Imprime o log na impressora fiscal."""
        try:
            import tempfile
            import os
            
            # Obtém o conteúdo do log
            log_content = self.text_log.get("1.0", "end-1c")
            
            if not log_content.strip() or log_content.strip() == "Log limpo.":
                # Mostra mensagem se não há dados para imprimir
                error_window = ctk.CTkToplevel(self)
                error_window.title("Aviso")
                error_window.geometry("300x120")
                error_window.transient(self)
                error_window.grab_set()
                ctk.CTkLabel(error_window, text="Não há dados para imprimir!", font=("Arial", 14)).pack(pady=20)
                ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
                return
            
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                # Cabeçalho do relatório
                header = f"RELATÓRIO DE DADOS RECEBIDOS\n"
                header += f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                header += f"Total de dados recebidos: {self.total_received}\n"
                header += f"Impressões: {self.total_impressoes} | Pesagens: {self.total_pesagens}\n"
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
            ctk.CTkLabel(error_window, text=f"Erro ao imprimir:\n{str(e)}", font=("Arial", 12), text_color="red").pack(pady=20)
            ctk.CTkButton(error_window, text="OK", command=error_window.destroy).pack(pady=10)
    
    def remove_temp_file(self, file_path):
        """Remove arquivo temporário."""
        try:
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    
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
    
    def open_config(self):
        """Abre janela de configurações de rede."""
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configurações de Rede - Receptor")
        config_window.geometry("550x550")
        config_window.resizable(False, False)
        config_window.transient(self)
        config_window.grab_set()
        
        config_window.after(100, lambda: config_window.lift())
        
        main_frame = ctk.CTkFrame(config_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="CONFIGURAÇÃO DO SERVIDOR RECEPTOR", font=("Arial", 18, "bold")).pack(pady=(10, 20))
        
        ctk.CTkLabel(main_frame, text="IP do servidor (este computador):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0, 5))
        entry_host = ctk.CTkEntry(main_frame, font=("Arial", 12), height=35)
        entry_host.insert(0, self.host)
        entry_host.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(main_frame, text="Porta do servidor:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(0, 5))
        entry_port = ctk.CTkEntry(main_frame, font=("Arial", 12), height=35)
        entry_port.insert(0, str(self.port))
        entry_port.pack(fill="x", padx=10, pady=(0, 20))
        
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        info_text = "INFORMAÇÕES IMPORTANTES:\n\n"
        info_text += "1. IP do Servidor (este computador):\n"
        info_text += "   - Use 0.0.0.0 para aceitar de qualquer IP\n"
        info_text += "   - Use IP específico para restringir acesso\n\n"
        info_text += "2. Porta:\n"
        info_text += "   - Deve ser a mesma nos dois sistemas\n"
        info_text += "   - Padrão: 8888\n\n"
        info_text += "3. Configure o IP no sistema da balança:\n"
        info_text += "   - Use o IP REAL deste computador\n"
        info_text += "   - Não use 0.0.0.0 no sistema da balança"
        
        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 11), justify="left").pack(padx=15, pady=15)
        
        def save_config():
            try:
                new_host = entry_host.get().strip()
                new_port = int(entry_port.get().strip())
                
                if not new_host:
                    new_host = '0.0.0.0'
                
                was_running = self.running
                if self.running:
                    self.stop_server()
                    time.sleep(1)
                
                self.host = new_host
                self.port = new_port
                
                self.label_status.configure(
                    text=f"Status: Configurado para {self.host}:{self.port}", 
                    text_color="blue"
                )
                
                config_window.destroy()
                
                if was_running:
                    self.after(500, self.start_server)
                
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
        
        def set_any_ip():
            entry_host.delete(0, "end")
            entry_host.insert(0, "0.0.0.0")
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_ip_local = ctk.CTkButton(button_frame, text="IP Local", command=get_local_ip, font=("Arial", 12), height=40)
        btn_ip_local.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        btn_qualquer_ip = ctk.CTkButton(button_frame, text="Qualquer IP", command=set_any_ip, font=("Arial", 12), height=40)
        btn_qualquer_ip.pack(side="left", fill="x", expand=True, padx=(3, 3))
        
        btn_salvar = ctk.CTkButton(button_frame, text="Salvar", command=save_config, font=("Arial", 12), height=40)
        btn_salvar.pack(side="right", fill="x", expand=True, padx=(3, 0))
    
    def stop_server(self):
        """Para o servidor."""
        self.running = False
        
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()
        
        self.label_status.configure(text="Status: Servidor parado", text_color="red")
        self.label_peso.configure(text="Aguardando...")
        self.label_timestamp.configure(text="Última atualização: --")
        self.label_mode.configure(text="Modo: --")
        self.label_client_info.configure(text="Cliente: Desconectado")
        self.button_iniciar.configure(state="normal")
        self.button_parar.configure(state="disabled")
    

    
    def on_closing(self):
        """Fecha a aplicação."""
        self.stop_server()
        self.destroy()

if __name__ == "__main__":
    app = ReceptorPeso()
    app.mainloop()