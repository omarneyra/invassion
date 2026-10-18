"""
Módulo de guardado y carga del estado del juego (Save / Load).
Estilo procedimental puro: funciones independientes y estructuras de datos serializables en JSON.
"""

import json
import os


SAVE_SCHEMA_VERSION = 1


def serialize_game_state(world_state, economy_state, wave_state):
    """
    Empaqueta los diccionarios planos del juego en una estructura 100% serializable en JSON.
    """
    # Convertir claves de nodos a string para compatibilidad JSON estándar
    nodes_serialized = {}
    for nid, ndata in world_state.get("nodes", {}).items():
        nodes_serialized[str(nid)] = {
            "controller": ndata.get("controller", "neutral"),
            "building": dict(ndata["building"]) if ndata.get("building") else None,
            "is_crater": bool(ndata.get("is_crater", False)),
            "is_base": bool(ndata.get("is_base", False)),
        }

    craters_serialized = {}
    for cid, cdata in world_state.get("craters", {}).items():
        craters_serialized[str(cid)] = {
            "hp": float(cdata.get("hp", 100.0)),
            "max_hp": float(cdata.get("max_hp", 100.0)),
            "is_sealed": bool(cdata.get("is_sealed", False)),
        }

    return {
        "version": SAVE_SCHEMA_VERSION,
        "world": {
            "nodes": nodes_serialized,
            "base_node_id": int(world_state.get("base_node_id", 0)),
            "crater_node_ids": [int(cid) for cid in world_state.get("crater_node_ids", [])],
            "craters": craters_serialized,
            "game_status": world_state.get("game_status", "in_progress"),
        },
        "economy": {
            "energy": float(economy_state.get("energy", 100.0)),
            "base_income_rate": float(economy_state.get("base_income_rate", 5.0)),
        },
        "wave": {
            "current_wave": int(wave_state.get("current_wave", 1)),
            "wave_countdown": float(wave_state.get("wave_countdown", 20.0)),
            "is_wave_active": bool(wave_state.get("is_wave_active", False)),
            "invader_counter": int(wave_state.get("invader_counter", 0)),
            "active_invaders": [dict(inv) for inv in wave_state.get("active_invaders", [])],
        },
    }


def deserialize_game_state(save_data):
    """
    Reconstruye las estructuras nativas a partir del diccionario de guardado.
    Convierte las claves numéricas de vuelta a 'int'.
    Retorna (es_valido, estado_deserializado, mensaje_error).
    """
    if not isinstance(save_data, dict):
        return False, {}, "Los datos de guardado no son un diccionario válido"

    if "world" not in save_data or "economy" not in save_data or "wave" not in save_data:
        return False, {}, "Estructura de guardado incompleta (faltan claves principales)"

    world_raw = save_data["world"]
    nodes_restored = {}
    for str_nid, ndata in world_raw.get("nodes", {}).items():
        try:
            nid = int(str_nid)
            nodes_restored[nid] = {
                "controller": ndata.get("controller", "neutral"),
                "building": ndata.get("building"),
                "is_crater": ndata.get("is_crater", False),
                "is_base": ndata.get("is_base", False),
            }
        except ValueError:
            continue

    craters_restored = {}
    for str_cid, cdata in world_raw.get("craters", {}).items():
        try:
            cid = int(str_cid)
            craters_restored[cid] = {
                "hp": float(cdata.get("hp", 100.0)),
                "max_hp": float(cdata.get("max_hp", 100.0)),
                "is_sealed": bool(cdata.get("is_sealed", False)),
            }
        except ValueError:
            continue

    restored_world = {
        "nodes": nodes_restored,
        "base_node_id": int(world_raw.get("base_node_id", 0)),
        "crater_node_ids": [int(cid) for cid in world_raw.get("crater_node_ids", [])],
        "craters": craters_restored,
        "game_status": world_raw.get("game_status", "in_progress"),
    }

    econ_raw = save_data["economy"]
    restored_econ = {
        "energy": float(econ_raw.get("energy", 100.0)),
        "base_income_rate": float(econ_raw.get("base_income_rate", 5.0)),
    }

    wave_raw = save_data["wave"]
    restored_wave = {
        "current_wave": int(wave_raw.get("current_wave", 1)),
        "wave_countdown": float(wave_raw.get("wave_countdown", 20.0)),
        "is_wave_active": bool(wave_raw.get("is_wave_active", False)),
        "invader_counter": int(wave_raw.get("invader_counter", 0)),
        "active_invaders": wave_raw.get("active_invaders", []),
    }

    return True, {
        "world": restored_world,
        "economy": restored_econ,
        "wave": restored_wave,
    }, ""


def save_state_to_file(filepath, save_data):
    """
    Escribe el diccionario de guardado como archivo JSON en disco.
    """
    try:
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)
        return True
    except Exception:
        return False


def load_state_from_file(filepath):
    """
    Lee un archivo JSON de disco y lo deserializa.
    Retorna (exito, estado_deserializado, mensaje).
    """
    if not os.path.exists(filepath):
        return False, {}, "El archivo no existe"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        return deserialize_game_state(raw_data)
    except Exception as e:
        return False, {}, f"Error al leer archivo JSON: {e}"
