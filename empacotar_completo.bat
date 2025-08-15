@echo off
echo ========================================
echo EMPACOTAMENTO COMPLETO DO SISTEMA
echo ========================================
echo.

echo Verificando se PyInstaller esta instalado...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ========================================
echo GERANDO TODOS OS EXECUTAVEIS
echo ========================================
echo.

echo Gerando Sistema Principal...
pyinstaller --clean sistema_balanca.spec

echo.
echo Gerando Receptor...
pyinstaller --clean receptor_peso.spec

echo.
echo Gerando Utilitario Descobrir IP...
pyinstaller --clean descobrir_ip.spec

echo.
echo ========================================
echo CRIANDO PACOTE DE DISTRIBUICAO
echo ========================================
echo.

if not exist "Pacote_Sistema_Balanca" mkdir "Pacote_Sistema_Balanca"
if not exist "Pacote_Sistema_Balanca\Sistema_Principal" mkdir "Pacote_Sistema_Balanca\Sistema_Principal"
if not exist "Pacote_Sistema_Balanca\Terminal_Remoto" mkdir "Pacote_Sistema_Balanca\Terminal_Remoto"
if not exist "Pacote_Sistema_Balanca\Utilitarios" mkdir "Pacote_Sistema_Balanca\Utilitarios"

echo Copiando arquivos...
copy "dist\Sistema_Balanca.exe" "Pacote_Sistema_Balanca\Sistema_Principal\"
copy "dist\Receptor_Peso.exe" "Pacote_Sistema_Balanca\Terminal_Remoto\"
copy "dist\Descobrir_IP.exe" "Pacote_Sistema_Balanca\Utilitarios\"

echo.
echo Criando arquivo de instrucoes...
(
echo SISTEMA DE PESAGEM DE VEICULOS
echo ==============================
echo.
echo CONTEUDO DO PACOTE:
echo.
echo 1. Sistema_Principal\
echo    - Sistema_Balanca.exe ^(Computador com balanca^)
echo.
echo 2. Terminal_Remoto\
echo    - Receptor_Peso.exe ^(Computador que recebe dados^)
echo.
echo 3. Utilitarios\
echo    - Descobrir_IP.exe ^(Para descobrir IP da rede^)
echo.
echo INSTRUCOES DE INSTALACAO:
echo.
echo 1. COMPUTADOR COM BALANCA:
echo    - Copie Sistema_Balanca.exe
echo    - Execute o programa
echo    - Conecte a balanca na porta serial/USB
echo.
echo 2. COMPUTADOR RECEPTOR:
echo    - Copie Receptor_Peso.exe
echo    - Execute o programa
echo    - Clique "Iniciar Servidor"
echo    - Anote o IP deste computador
echo.
echo 3. CONFIGURACAO DE REDE:
echo    - No Sistema_Balanca.exe, clique "Config IP"
echo    - Digite o IP do computador receptor
echo    - Clique "Conectar Terminal Remoto"
echo.
echo 4. USO:
echo    - Modo 1: Pesagem continua em tempo real
echo    - Modo 2: Captura dados quando apertar "I" na balanca
echo.
echo SUPORTE:
echo - Use Descobrir_IP.exe para encontrar IPs da rede
echo - Porta padrao: 8888
echo - Ambos computadores devem estar na mesma rede
echo.
echo Versao: 1.0
echo Data: %date%
) > "Pacote_Sistema_Balanca\LEIA-ME.txt"

echo.
echo ========================================
echo EMPACOTAMENTO CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Pacote criado em: Pacote_Sistema_Balanca\
echo.
echo CONTEUDO:
echo - Sistema_Principal\Sistema_Balanca.exe
echo - Terminal_Remoto\Receptor_Peso.exe  
echo - Utilitarios\Descobrir_IP.exe
echo - LEIA-ME.txt
echo.
echo PRONTO PARA DISTRIBUICAO!
echo.
pause