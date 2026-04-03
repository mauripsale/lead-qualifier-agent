# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Questo modulo definisce gli strumenti (Tools) a disposizione dell'agente.
Include strumenti per la ricerca di informazioni e per il salvataggio dei risultati su Firestore.
"""

import datetime
import os

from google.adk.tools.google_search_tool import google_search
from google.adk.tools.load_memory_tool import load_memory as adk_load_memory
from google.cloud import firestore
from app.app_utils.config import config

# Inizializza il client Firestore utilizzando il database specificato nella configurazione YAML
DATABASE_ID = config.get("firestore.database_id", "lead-qualifier-db-dev")
db = firestore.Client(database=DATABASE_ID)

# Esportiamo google_search per renderlo disponibile all'agente
google_search_tool = google_search

async def ricerca_in_memoria(query: str) -> str:
    """
    Cerca informazioni rilevanti nelle conversazioni passate dell'utente.
    Da usare quando l'utente fa riferimento a fatti o preferenze discussi in precedenza.

    Args:
        query: La stringa di ricerca per trovare fatti o preferenze passate.

    Returns:
        Un riassunto testuale delle memorie trovate, o un messaggio di 'nessun ricordo trovato'.
    """
    try:
        # Chiamata al tool originale di ADK
        response = await adk_load_memory(query=query)
        
        if not response or not response.memories:
            return "Nessun ricordo pertinente trovato nelle conversazioni passate."
        
        results = []
        for memory in response.memories:
            if memory.content and memory.content.parts:
                text = " ".join(part.text for part in memory.content.parts if part.text)
                results.append(f"- {text}")
        
        if not results:
            return "Ho trovato delle sessioni passate ma nessun dettaglio testuale utile."
            
        return "Ecco cosa ricordo dalle conversazioni precedenti:\n" + "\n".join(results)
        
    except Exception as e:
        return f"Spiacente, si è verificato un errore tecnico nel recupero della memoria: {e}"

def salva_qualificazione(nome_azienda: str, descrizione_azienda: str, tipo: str, volume: int) -> str:
    """
    Salva la qualificazione commerciale estratta nel database Firestore, includendo i dettagli dell'azienda.
    Da chiamare SOLO quando l'utente ha fornito chiaramente il nome dell'azienda, il tipo di potenziale
    (competitor, storico, proxy) e il numero esatto associato.

    Args:
        nome_azienda: Il nome dell'azienda identificata.
        descrizione_azienda: Una breve descrizione dell'azienda ottenuta tramite ricerca.
        tipo: Il tipo di qualificazione. Valori ammessi: 'competitor', 'storico', 'proxy'.
        volume: Il numero di lavoratori stimato o effettivo (intero).

    Returns:
        Stringa di conferma dell'avvenuto salvataggio.
    """
    try:
        # Crea un riferimento alla collection 'qualificazioni'
        doc_ref = db.collection("qualificazioni").document()

        # Dati da salvare
        data = {
            "nome_azienda": nome_azienda,
            "descrizione_azienda": descrizione_azienda,
            "tipo": tipo,
            "volume": volume,
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc)
        }

        # Salva i dati su Firestore
        doc_ref.set(data)

        return f"Qualificazione salvata con successo per {nome_azienda} su Firestore: {tipo} con volume {volume}."
    except Exception as e:
        return f"Errore durante il salvataggio su Firestore: {e!s}"
