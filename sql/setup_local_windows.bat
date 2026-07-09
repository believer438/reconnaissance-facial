@echo off
:: =============================================================================
:: UniPresence — Script d'installation locale (Windows)
:: Double-cliquer sur ce fichier ou l'exécuter depuis l'invite de commandes
:: =============================================================================

cd /d "%~dp0.."

echo.
echo ====================================================
echo   UniPresence - Installation locale (Windows)
echo ====================================================
echo.

:: ── 1. Vérifier Python
echo [1/5] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERREUR : Python n'est pas installe ou n'est pas dans le PATH.
    echo   Telechargez Python 3.10+ depuis https://www.python.org/
    echo   IMPORTANT : Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   OK : %%i

:: ── 2. Environnement virtuel
echo.
echo [2/5] Creation de l'environnement virtuel...
if not exist "venv\" (
    python -m venv venv
    echo   OK : venv cree
) else (
    echo   OK : venv deja existant
)
call venv\Scripts\activate.bat

:: ── 3. Dépendances
echo.
echo [3/5] Installation des dependances Python...
pip install --upgrade pip -q
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo   ERREUR lors de l'installation des dependances.
    pause
    exit /b 1
)
echo   OK : dependances installees

:: ── 4. Base de données
echo.
echo [4/5] Initialisation de la base de donnees...
if exist "db.sqlite3" (
    echo   INFO : db.sqlite3 deja present - migrations seulement
    python manage.py migrate --run-syncdb
) else (
    echo   Creation d'une nouvelle base...
    python manage.py migrate --run-syncdb
    echo   Application des donnees initiales...
    python sql\restore_db.py --config-only
)
if %errorlevel% neq 0 (
    echo   ERREUR lors de la migration.
    pause
    exit /b 1
)
echo   OK : base de donnees prete

:: ── 5. Statiques
echo.
echo [5/5] Collecte des fichiers statiques...
python manage.py collectstatic --noinput -v 0 2>nul
echo   OK

:: ── Résumé
echo.
echo ====================================================
echo   Installation terminee avec succes !
echo ====================================================
echo.
echo   Pour lancer le serveur :
echo     venv\Scripts\activate
echo     python manage.py runserver 0.0.0.0:8008
echo.
echo   Acces : http://localhost:8008/facial/
echo   Admin : admin / admin123
echo.
pause
