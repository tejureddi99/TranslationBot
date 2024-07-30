from enum import Enum

class TranslationSettings(str, Enum):
    default_language = "en"
    english_english = "en"
    english_hindi = "hi"
    hindi_english = "en"
    hindi_hindi = "hi"
