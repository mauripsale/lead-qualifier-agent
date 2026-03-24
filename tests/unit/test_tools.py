import sqlite3
import pytest
from app.tools import salva_qualificazione
import app.tools

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """
    Fixture che crea un path temporaneo per il database SQLite 
    e fa il mock della variabile DB_PATH nel modulo app.tools.
    Restituisce il percorso del db temporaneo per fare le asserzioni.
    """
    db_file = tmp_path / "test_qualificazioni.db"
    monkeypatch.setattr(app.tools, "DB_PATH", str(db_file))
    return db_file

def test_salva_qualificazione_restituisce_stringa_corretta(temp_db):
    """
    Verifica che il tool restituisca la stringa formattata correttamente.
    """
    risultato = salva_qualificazione("competitor", 50)
    assert risultato == "Qualificazione salvata con successo: competitor con volume 50."

def test_salva_qualificazione_crea_tabella_e_inserisce_dati(temp_db):
    """
    Verifica che il tool crei la tabella se non esiste e inserisca i valori corretti.
    """
    salva_qualificazione("storico", 20)
    
    # Controlliamo cosa è stato salvato nel DB temporaneo
    with sqlite3.connect(str(temp_db)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, volume FROM qualificazioni")
        righe = cursor.fetchall()
        
        assert len(righe) == 1
        assert righe[0] == ("storico", 20)

def test_salva_qualificazione_inserisce_piu_righe(temp_db):
    """
    Verifica che chiamate multiple salvino i dati consecutivamente senza sovrascriverli.
    """
    salva_qualificazione("proxy", 10)
    salva_qualificazione("competitor", 100)
    
    with sqlite3.connect(str(temp_db)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, volume FROM qualificazioni ORDER BY id")
        righe = cursor.fetchall()
        
        assert len(righe) == 2
        assert righe[0] == ("proxy", 10)
        assert righe[1] == ("competitor", 100)
