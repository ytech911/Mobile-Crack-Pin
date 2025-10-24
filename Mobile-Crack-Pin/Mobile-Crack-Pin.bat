:: =============================================================================
::               MOBILE-CRACK-PIN - INJECTEUR DE SEQUENCES
:: =============================================================================
@ECHO OFF
TITLE Console d'Injection - Mobile-Crack-Pin

:: On s'assure de travailler dans le bon dossier et d'activer les accents
cd /d "%~dp0"
CHCP 65001 > NUL
CLS

:: --- ECRAN DE BIENVENUE ---
COLOR 0B
ECHO.
ECHO    ╔═════════════════════════════════════════════════════════════════════╗
ECHO    ║                                                                     ║
ECHO    ║                       MOBILE-CRACK-PIN                              ║
ECHO    ║                                                                     ║
ECHO    ║               - INJECTEUR DE SEQUENCES AUTOMATISE -                 ║
ECHO    ║                                                                     ║
ECHO    ╚═════════════════════════════════════════════════════════════════════╝
ECHO.
ECHO    Ce script va etablir une liaison ADB pour injecter des sequences numeriques.
ECHO.
ECHO    Protocole :
ECHO    1. Activez le mode DEBUGGING USB sur le terminal cible.
ECHO    2. Etablissez la liaison physique (USB) et autorisez le handshake.
ECHO.
PAUSE
CLS

:: --- BOUCLE DE CONFIGURATION ---
:CONFIG
COLOR 0A
ECHO.
ECHO   ╔════════════════════════════════════════════════╗
ECHO   ║          PARAMETRES DE L'INJECTION               ║
ECHO   ╚════════════════════════════════════════════════╝
ECHO.

:: Question 1: Longueur du code
SET /P CODE_LENGTH="  1> Profondeur de la sequence (nb de chiffres) : "
ECHO.

:: Question 2: Nombre de depart
SET /P START_NUMBER="  2> Vecteur d'initialisation (nombre de depart) : "
ECHO.

:: Question 3: Activer la detection de blocage
SET /P DETECT_LOCKOUT="  3> Activer l'analyse des contre-mesures ? (O/N) : "
ECHO.
CLS

:: --- ECRAN DE CONFIRMATION ---
COLOR 0E
ECHO.
ECHO   ╔════════════════════════════════════════════════╗
ECHO   ║              VERIFICATION DES PARAMETRES         ║
ECHO   ╚════════════════════════════════════════════════╝
ECHO.
ECHO    Briefing de la mission :
ECHO.
ECHO      - Profondeur de sequence....: %CODE_LENGTH% chiffres
ECHO      - Vecteur initial...........: %START_NUMBER%
ECHO      - Analyse contre-mesures....: %DETECT_LOCKOUT%
ECHO.
ECHO   ----------------------------------------------------
ECHO.
SET /P CONFIRM="  >> Lancer le protocole d'injection ? (O/N) : "
IF /I NOT "%CONFIRM%"=="O" (
    CLS
    GOTO CONFIG
)
CLS

:: --- ECRAN D'EXECUTION ---
COLOR 0A
ECHO.
ECHO   ╔════════════════════════════════════════════════╗
ECHO   ║             INITIALISATION DU PAYLOAD...         ║
ECHO   ╚════════════════════════════════════════════════╝
ECHO.
PAUSE
CLS
ECHO.
ECHO   --- [PHASE 1/3] Activation du pont de debogage Android...
.\platform-tools\adb.exe start-server
ECHO.
ECHO.
ECHO   --- [PHASE 2/3] Execution du script d'injection...
ECHO   (L'injection de la sequence commence maintenant)
ECHO.
python Script.py %CODE_LENGTH% %DETECT_LOCKOUT% %START_NUMBER%
ECHO.
ECHO.
ECHO   --- [PHASE 3/3] Fermeture du pont de debogage...
.\platform-tools\adb.exe kill-server
ECHO.

:: --- ECRAN FINAL ---
COLOR 0B
ECHO.
ECHO    ╔═════════════════════════════════════════════════════════════════════╗
ECHO    ║                                                                     ║
ECHO    ║               * * * FIN DE LA SEQUENCE D'INJECTION * * *            ║
ECHO    ║                                                                     ║
ECHO    ╚═════════════════════════════════════════════════════════════════════╝
ECHO.
ECHO    La console reste active pour analyse post-operation.
ECHO.
ECHO    Appuyez sur n'importe quelle touche pour terminer la session.
PAUSE > NUL
EXIT