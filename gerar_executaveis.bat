@echo off
echo ========================================
echo EMPACOTAMENTO DO SISTEMA DE BALANCA
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
echo GERANDO EXECUTAVEL DO SISTEMA PRINCIPAL
echo ========================================
echo.

pyinstaller --clean sistema_balanca.spec

echo.
echo ========================================
echo GERANDO EXECUTAVEL DO RECEPTOR
echo ========================================
echo.

pyinstaller --clean receptor_peso.spec

echo.
echo ========================================
echo EMPACOTAMENTO CONCLUIDO!
echo ========================================
echo.
echo Os executaveis foram criados em:
echo - dist\Sistema_Balanca.exe (Sistema principal com balanca)
echo - dist\Receptor_Peso.exe (Terminal remoto)
echo.
echo INSTRUCOES DE USO:
echo 1. Copie Sistema_Balanca.exe para o computador com a balanca
echo 2. Copie Receptor_Peso.exe para o computador que vai receber os dados
echo 3. Execute primeiro o Receptor_Peso.exe e clique "Iniciar Servidor"
echo 4. Execute Sistema_Balanca.exe, configure o IP e conecte
echo.
pause