from flask import Flask, render_template, jsonify
import sqlite3
import serial
import threading
import time
from datetime import datetime

app = Flask(__name__)

# =============================================
# CONFIGURARE - modifica COM5 daca e altul
# =============================================
SERIAL_PORT = "COM5"
BAUD_RATE = 115200
DB_PATH = "iv_data.db"

PATIENT = {
    "nume": "Popescu Ion",
    "cnp": "1810101123456",
    "varsta": "45 ani",
    "oras": "Timișoara",
    "salon": "C ATI"
}

# =============================================
# DATE CURENTE - actualizate din thread serial
# =============================================
current_data = {
    "setpoint": "-",
    "flux": "-",
    "debit": "-",
    "stare": "-",
    "pompa": "-",
    "buzzer": "-",
    "ultima_actualizare": "-"
}

last_stare = None  # retine ultima stare pentru a detecta schimbari

# =============================================
# BAZA DE DATE
# =============================================
def init_db():
    """Creaza tabela events daca nu exista."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            time    TEXT,
            patient TEXT,
            setpoint TEXT,
            debit   TEXT,
            flux    TEXT,
            stare   TEXT,
            pompa   TEXT,
            buzzer  TEXT
        )
    """);
    conn.commit()
    conn.close()

def save_event(data):
    """Insereaza un eveniment in baza de date."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (time, patient, setpoint, debit, flux, stare, pompa, buzzer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["ultima_actualizare"],
        PATIENT["nume"],
        data["setpoint"],
        data["debit"],
        data["flux"],
        data["stare"],
        data["pompa"],
        data["buzzer"]
    ))
    conn.commit()
    conn.close()

def get_events():
    """Returneaza ultimele 20 de evenimente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, time, patient, setpoint, debit, flux, stare, pompa, buzzer
        FROM events
        ORDER BY id DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats():
    """Returneaza statistici simple."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    stats = {"total": total}
    for stare in ["NOFLOW", "LOW", "PESTE", "DANGER"]:
        cursor.execute("SELECT COUNT(*) FROM events WHERE stare = ?", (stare,))
        stats[stare] = cursor.fetchone()[0]
    conn.close()
    return stats

# =============================================
# PARSARE LINIE SERIALA
# =============================================
def parse_serial_line(line):
    """
    Parseaza linia:
    Setpoint: 50 pm | Flux: 8/10s | Debit: 48 pm | Stare: OK | Pompa: OFF | Buzzer: OFF
    """
    try:
        parts = line.split("|")
        result = {}
        for part in parts:
            part = part.strip()
            if part.startswith("Setpoint:"):
                result["setpoint"] = part.replace("Setpoint:", "").strip().replace(" pm", "")
            elif part.startswith("Flux:"):
                result["flux"] = part.replace("Flux:", "").strip()
            elif part.startswith("Debit:"):
                result["debit"] = part.replace("Debit:", "").strip().replace(" pm", "")
            elif part.startswith("Stare:"):
                result["stare"] = part.replace("Stare:", "").strip()
            elif part.startswith("Pompa:"):
                result["pompa"] = part.replace("Pompa:", "").strip()
            elif part.startswith("Buzzer:"):
                result["buzzer"] = part.replace("Buzzer:", "").strip()
        return result if len(result) == 6 else None
    except Exception:
        return None

# =============================================
# THREAD SERIAL - citeste Arduino in fundal
# =============================================
def read_serial():
    global current_data, last_stare
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
            print(f"[OK] Conectat la {SERIAL_PORT}")
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                parsed = parse_serial_line(line)
                if parsed:
                    parsed["ultima_actualizare"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    current_data.update(parsed)
                    # Salveaza in DB doar cand se schimba starea
                    if parsed["stare"] != last_stare:
                        last_stare = parsed["stare"]
                        save_event(current_data)
        except serial.SerialException as e:
            print(f"[EROARE SERIAL] {e} - reincerc in 5 secunde...")
            time.sleep(5)
        except Exception as e:
            print(f"[EROARE] {e}")
            time.sleep(5)

# =============================================
# RUTE FLASK
# =============================================
@app.route("/")
def index():
    events = get_events()
    stats = get_stats()
    return render_template("index.html",
                           patient=PATIENT,
                           data=current_data,
                           events=events,
                           stats=stats)

@app.route("/api/data")
def api_data():
    """Endpoint JSON pentru refresh automat."""
    return jsonify(current_data)

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

# =============================================
# PORNIRE
# =============================================
if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=read_serial, daemon=True)
    t.start()
    print("[OK] Server pornit: http://127.0.0.1:5000")
    app.run(debug=False, use_reloader=False)
