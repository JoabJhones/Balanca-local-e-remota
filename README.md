# Sistema de Pesagem de Veículos - Local e Remoto

Sistema completo para pesagem de veículos com interface gráfica moderna, suportando operação local e remota.

## 🚀 Funcionalidades

### Modos de Operação
- **Pesagem Contínua**: Exibe o peso da balança em tempo real com fonte grande e centralizada
- **Captura de Impressão**: Captura e armazena dados de impressão da balança

### Recursos Principais
- Interface gráfica moderna com CustomTkinter
- Conexão automática com balança via porta serial
- Terminal remoto para monitoramento à distância
- Impressão automática opcional
- Status detalhado de conexões
- Suporte a múltiplas configurações de porta serial

## 📋 Requisitos

### Dependências Python
```bash
pip install customtkinter
pip install pyserial
```

### Hardware
- Balança com saída serial/USB
- Cabo de conexão adequado

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/JoabJhones/Balanca-local-e-remota.git
cd Balanca-local-e-remota
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o sistema:
```bash
python "Sytembalança sem simulador de teste.py"
```

## 📖 Como Usar

### Modo Pesagem Contínua
1. Conecte a balança ao computador
2. Execute o programa
3. O sistema detectará automaticamente a porta serial
4. O peso será exibido centralizado na tela

### Modo Captura de Impressão
1. Selecione "Captura Impressão"
2. Pressione a tecla 'I' na balança para imprimir
3. Os dados serão capturados e exibidos
4. Use "Imprimir" para enviar à impressora

### Terminal Remoto
1. Configure o IP do computador receptor
2. Execute o receptor_peso.py no computador de destino
3. Clique em "Conectar" para estabelecer conexão
4. Os dados serão enviados automaticamente

## ⚙️ Configurações

### Porta Serial
- Detecção automática de portas USB/Serial
- Configuração: 9600 baud, 8 bits, sem paridade
- Suporte a múltiplas velocidades de transmissão

### Rede
- IP padrão: 127.0.0.1
- Porta padrão: 8888
- Configuração através da interface gráfica

## 🎨 Interface

- **Tema escuro** moderno e profissional
- **Painel lateral compacto** (280px) para controles
- **Área principal expandida** para exibição do peso
- **Status detalhado** com quebra de linha automática
- **Peso centralizado** com fonte grande (90pt)

## 📁 Estrutura do Projeto

```
Balanca-local-e-remota/
├── Sytembalança sem simulador de teste.py  # Sistema principal
├── receptor_peso.py                        # Terminal remoto (se disponível)
├── requirements.txt                        # Dependências
└── README.md                              # Documentação
```

## 🔍 Solução de Problemas

### Balança não conecta
- Verifique se a balança está ligada
- Confirme o cabo de conexão
- Teste diferentes portas USB

### Erro de porta serial
- Feche outros programas que usam a porta
- Reinicie a balança
- Verifique drivers USB

### Terminal remoto não conecta
- Confirme o IP do computador receptor
- Verifique se a porta 8888 está liberada
- Teste conectividade de rede

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

**Joab Jhones**
- GitHub: [@JoabJhones](https://github.com/JoabJhones)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!