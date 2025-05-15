# core/utils/cache_utils.py

import os
import pickle
from config.settings import CACHE_PATH

def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"[캐시 로드 실패] {e}")
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cache, f)
