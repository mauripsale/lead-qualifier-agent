import sqlite3

DB_PATH = "qualificazioni.db"

def salva_qualificazione(tipo: str, volume: int) -> str:
    """
    Salva la qualificazione commerciale estratta nel database locale.
    Da chiamare SOLO quando l'utente ha fornito chiaramente sia il tipo di potenziale 
    (competitor, storico, proxy) sia il numero esatto associato.

    Args:
        tipo: Il tipo di qualificazione. Valori ammessi: 'competitor', 'storico', 'proxy'.
        volume: Il numero di lavoratori stimato o effettivo (intero).

    Returns:
        Stringa di conferma dell'avvenuto salvataggio.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Crea la tabella se non esiste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qualificazioni (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                volume INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Inserisci il dato raccolto
        cursor.execute(
            'INSERT INTO qualificazioni (tipo, volume) VALUES (?, ?)',
            (tipo, volume)
        )
        conn.commit()
        
    return f"Qualificazione salvata con successo: {tipo} con volume {volume}."
