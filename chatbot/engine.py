import json
import random
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

# Kamus normalisasi kata tidak baku (termasuk istilah sholat)
NORMALISASI = {
    "solat": "sholat",
    "shalat": "sholat",
    "shalatnya": "sholat",
    "praktek": "tata cara",
    "gimana": "bagaimana",
    "gmn": "bagaimana",
    "bgmn": "bagaimana",
    "brp": "berapa",
    "yg": "yang",
    "utk": "untuk",
    "sy": "saya",
    "kak": "",
    "min": "",
    "dong": "",
    "sih": "",
    "makasih": "terima kasih",
    "thx": "terima kasih",
    "hai": "halo",
    "hi": "halo",
    "niatnya": "niat",
    "tahiyyat": "tasyahud",
    "batalin": "membatalkan",
    "ngomong": "berbicara",
    "syaratnya": "syarat",
}

STOPWORDS = [
    "yang", "di", "ke", "dari", "dan", "atau", "itu", "ini", "untuk", "dengan",
    "adalah", "apa", "saya", "mau", "ingin", "tolong", "pada", "akan", "juga",
    "ada", "tentang", "mohon", "bisa", "boleh", "kah", "info", "informasi"
]

BOBOT_JACCARD, BOBOT_FUZZY, BOBOT_CAKUPAN = 0.4, 0.3, 0.3
KUNCI_WAJIB_TEMA = ["id", "name", "bot_name", "avatar", "color", "description", "greeting", "suggestions", "fallback", "intents"]

def preprocess(teks: str) -> list[str]:
    teks = teks.lower()
    teks = re.sub(r"[^a-z0-9\s]", "", teks)
    tokens = []
    for kata in teks.split():
        kata_norm = NORMALISASI.get(kata, kata)
        for k in kata_norm.split():
            if k and k not in STOPWORDS:
                tokens.append(k)
    return tokens

def similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    set_a, set_b = set(tokens_a), set(tokens_b)
    jaccard = len(set_a & set_b) / len(set_a | set_b)
    fuzzy = SequenceMatcher(None, "".join(tokens_a), "".join(tokens_b)).ratio()
    cakupan = len(set_a & set_b) / len(set_b)
    return round(BOBOT_JACCARD * jaccard + BOBOT_FUZZY * fuzzy + BOBOT_CAKUPAN * cakupan, 4)

def validate_theme(theme: dict) -> list[str]:
    masalah = [f"kunci '{k}' tidak ada" for k in KUNCI_WAJIB_TEMA if k not in theme]
    if masalah:
        return masalah
    if not theme["fallback"]:
        masalah.append("daftar 'fallback' kosong")
    tags, pola_milik = set(), {}
    for i, intent in enumerate(theme["intents"]):
        for k in ("tag", "patterns", "responses"):
            if k not in intent:
                masalah.append(f"intent ke-{i+1}: kunci '{k}' tidak ada")
        tag = intent.get("tag", f"#{i+1}")
        if tag in tags:
            masalah.append(f"tag '{tag}' dipakai lebih dari sekali")
        tags.add(tag)
        if not intent.get("patterns"):
            masalah.append(f"intent '{tag}': patterns kosong")
        if not intent.get("responses"):
            masalah.append(f"intent '{tag}': responses kosong")
        for pola in intent.get("patterns", []):
            kunci = " ".join(preprocess(pola))
            if not kunci:
                masalah.append(f"intent '{tag}': pola '{pola}' kosong setelah praproses")
            elif kunci in pola_milik and pola_milik[kunci] != tag:
                masalah.append(f"pola '{pola}' ada di intent '{pola_milik[kunci]}' dan '{tag}'")
            pola_milik.setdefault(kunci, tag)
    return masalah

def load_themes(folder: str | Path) -> dict[str, dict]:
    themes = {}
    for path in sorted(Path(folder).glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        masalah = validate_theme(data)
        if masalah:
            raise ValueError(f"File tema {path.name} tidak valid:\n- " + "\n- ".join(masalah))
        themes[data["id"]] = data
    return themes

class ChatbotEngine:
    def __init__(self, theme: dict, threshold: float = 0.45):
        self.theme = theme
        self.threshold = threshold
        self.patterns = [
            (intent["tag"], pola, preprocess(pola))
            for intent in theme["intents"]
            for pola in intent["patterns"]
        ]
        self._responses = {i["tag"]: i["responses"] for i in theme["intents"]}

    def explain(self, pesan: str, top: int = 3) -> list[dict]:
        tokens = preprocess(pesan)
        terbaik = {}
        for tag, pola, pt in self.patterns:
            skor = similarity(tokens, pt)
            if tag not in terbaik or skor > terbaik[tag]["score"]:
                terbaik[tag] = {"intent": tag, "pattern": pola, "score": skor}
        return sorted(terbaik.values(), key=lambda x: x["score"], reverse=True)[:top]

    def classify(self, pesan: str) -> tuple[str | None, float]:
        kandidat = self.explain(pesan, top=1)
        if not kandidat or kandidat[0]["score"] < self.threshold:
            return None, (kandidat[0]["score"] if kandidat else 0.0)
        return kandidat[0]["intent"], kandidat[0]["score"]

    def _isi_placeholder(self, teks: str) -> str:
        now = datetime.now()
        return (teks.replace("{waktu}", now.strftime("%H:%M"))
                    .replace("{tanggal}", now.strftime("%d-%m-%Y"))
                    .replace("{nama_bot}", self.theme["bot_name"]))

    def reply(self, pesan: str) -> dict:
        if not pesan or not pesan.strip():
            return {"reply": "Pesannya masih kosong. Silakan ketik pertanyaan Anda.", "intent": None, "score": 0.0}
        tag, skor = self.classify(pesan)
        if tag is None:
            teks = random.choice(self.theme["fallback"])
        else:
            teks = random.choice(self._responses[tag])
        return {"reply": self._isi_placeholder(teks), "intent": tag, "score": skor}