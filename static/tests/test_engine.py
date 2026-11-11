from pathlib import Path
import pytest
from chatbot.engine import ChatbotEngine, load_themes, preprocess, similarity

THEMES = load_themes(Path(__file__).resolve().parent.parent / "themes")

def test_preprocess_sholat_normalisasi():
    assert preprocess("Solat shalatnya praktek gimana sih kak?") == ["sholat", "sholat", "tata", "cara", "bagaimana"]

def test_similarity_identik():
    tokens = ["rukun", "sholat"]
    assert similarity(tokens, tokens) == 1.0

@pytest.mark.parametrize("pesan, intent_diharapkan", [
    ("assalamu'alaikum ustadz", "salam"),
    ("apa saja syarat sah sholat", "syarat_sah"),
    ("sebutkan rukun sholat", "rukun_sholat"),
    ("gimana niat sholat subuh", "niat_fardhu"),
    ("tata cara sholat yang benar", "tata_cara"),
    ("contoh sholat sunnah apa aja", "sholat_sunnah"),
    ("bagaimana cara sholat jamak", "jamak_qashar"),
    ("lupa rakaat sholat harus apa", "sujud_sahwi"),
])
def test_klasifikasi_intent_sholat(pesan, intent_diharapkan):
    engine = ChatbotEngine(THEMES["sholat"])
    tag, _ = engine.classify(pesan)
    assert tag == intent_diharapkan

def test_pertanyaan_luar_tema_fallback():
    engine = ChatbotEngine(THEMES["sholat"])
    hasil = engine.reply("siapa pemenang piala dunia")
    assert hasil["intent"] is None
    assert hasil["reply"] in THEMES["sholat"]["fallback"]