"""
Language Support Module
Manages multilingual text-to-speech and translations
"""

# ============================================
# LANGUAGE CONSTANTS
# ============================================
LANG_ENGLISH = "en_US"
LANG_HINDI = "hi_IN"

# Available languages for GUI selection
AVAILABLE_LANGUAGES = {
    LANG_ENGLISH: "English (US)",
    LANG_HINDI: "हिंदी (Hindi)",
}

# Default language
DEFAULT_LANGUAGE = LANG_ENGLISH

# ============================================
# PIPER TTS MODEL PATHS
# ============================================
MODEL_PATHS = {
    LANG_ENGLISH: {
        "model": "./piper_models/en_US-lessac-medium.onnx",
        "config": "./piper_models/en_US-lessac-medium.onnx.json"
    },
    LANG_HINDI: {
        "model": "./piper_models/hi_IN-priyamvada-medium.onnx",
        "config": "./piper_models/hi_IN-priyamvada-medium.onnx.json"
    }
}

# ============================================
# TRANSLATION STRINGS
# ============================================

# Navigation guidance messages
TRANSLATIONS = {
    # System status messages
    'system_ready': {
        LANG_ENGLISH: "Navigation system ready",
        LANG_HINDI: "तैयार है",
    },
    'detection_started': {
        LANG_ENGLISH: "Detection started",
        LANG_HINDI: "शुरू",
    },
    'detection_stopped': {
        LANG_ENGLISH: "Detection stopped",
        LANG_HINDI: "बंद",
    },
    'audio_enabled': {
        LANG_ENGLISH: "Audio enabled",
        LANG_HINDI: "आवाज़ चालू",
    },
    'audio_disabled': {
        LANG_ENGLISH: "Audio disabled",
        LANG_HINDI: "आवाज़ बंद",
    },
    'audio_test': {
        LANG_ENGLISH: "Audio test. Navigation system working correctly.",
        LANG_HINDI: "सुनाई दे रहा है। सब ठीक है।",
    },
    'loading_language': {
        LANG_ENGLISH: "Loading language",
        LANG_HINDI: "लोड हो रहा है",
    },

    # Path status
    'path_clear': {
        LANG_ENGLISH: "Path clear",
        LANG_HINDI: "सब साफ है",
    },

    # Direction words
    'left': {
        LANG_ENGLISH: "left",
        LANG_HINDI: "बायीं ओर",
    },
    'right': {
        LANG_ENGLISH: "right",
        LANG_HINDI: "दायीं ओर",
    },
    'ahead': {
        LANG_ENGLISH: "ahead",
        LANG_HINDI: "आगे",
    },
    'stop': {
        LANG_ENGLISH: "stop",
        LANG_HINDI: "रुको",
    },

    # ============================================
    # CENTER-FIRST NAVIGATION MESSAGES
    # ============================================

    # When CENTER is clear but sides have objects (low urgency)
    'object_left_side_keep': {
        LANG_ENGLISH: "Object on left side, keep {direction}",
        LANG_HINDI: "बायीं तरफ कुछ है, {direction} चलो",
    },
    'object_right_side_keep': {
        LANG_ENGLISH: "Object on right side, keep {direction}",
        LANG_HINDI: "दायीं तरफ कुछ है, {direction} चलो",
    },

    # When CENTER is blocked (high urgency)
    'object_ahead': {
        LANG_ENGLISH: "Object ahead, move {direction} by {angle} degrees",
        LANG_HINDI: "आगे कुछ है, {direction} मुड़ो",
    },
    'object_ahead_left': {
        LANG_ENGLISH: "Object ahead and slightly left, move {direction} by {angle} degrees",
        LANG_HINDI: "आगे बायीं ओर कुछ है, {direction} घूमो",
    },
    'object_ahead_right': {
        LANG_ENGLISH: "Object ahead and slightly right, move {direction} by {angle} degrees",
        LANG_HINDI: "आगे दायीं ओर कुछ है, {direction} घूमो",
    },
    'object_ahead_both': {
        LANG_ENGLISH: "Objects ahead and on sides, move {direction} by {angle} degrees",
        LANG_HINDI: "आगे और दोनों तरफ कुछ है, {direction} मुड़ो",
    },

    # Critical: Everything blocked
    'object_ahead_stop': {
        LANG_ENGLISH: "Warning! Objects ahead on all sides, stop and turn {angle} degrees",
        LANG_HINDI: "खतरा! हर तरफ कुछ है, रुको और पीछे हटो",
    },

    # ============================================
    # LEGACY MESSAGES (kept for compatibility)
    # ============================================
    'object_left': {
        LANG_ENGLISH: "Object detected on left, move right by {angle} degrees",
        LANG_HINDI: "बायीं ओर कुछ है, दायें मुड़ो",
    },
    'object_right': {
        LANG_ENGLISH: "Object detected on right, move left by {angle} degrees",
        LANG_HINDI: "दायीं ओर कुछ है, बायें मुड़ो",
    },
    'object_left_side': {
        LANG_ENGLISH: "Object detected on left side, move right by {angle} degrees",
        LANG_HINDI: "बायीं तरफ कुछ है, दायें घूमो",
    },
    'object_right_side': {
        LANG_ENGLISH: "Object detected on right side, move left by {angle} degrees",
        LANG_HINDI: "दायीं तरफ कुछ है, बायें घूमो",
    },

    # Urgency prefixes
    'warning': {
        LANG_ENGLISH: "Warning!",
        LANG_HINDI: "सावधान!",
    },
    'caution': {
        LANG_ENGLISH: "Caution.",
        LANG_HINDI: "ध्यान से!",
    },
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_translation(language_code, key, **kwargs):
    """
    Get translated string for a given key

    Args:
        language_code: Language code (e.g., LANG_ENGLISH)
        key: Translation key from TRANSLATIONS dict
        **kwargs: Format arguments for string interpolation

    Returns:
        Translated string with formatting applied

    Example:
        get_translation(LANG_HINDI, 'object_ahead', direction='बाएं', angle=30)
        Returns: "सामने वस्तु है, 30 डिग्री बाएं मुड़ें"
    """
    # Get translation dict for this key
    translations = TRANSLATIONS.get(key)

    if not translations:
        print(f"⚠️  Warning: Translation key '{key}' not found")
        return f"[Missing: {key}]"

    # Get translation for specific language
    text = translations.get(language_code)

    if not text:
        # Fallback to English if translation missing
        print(f"⚠️  Warning: Translation for '{key}' not found in {language_code}, using English")
        text = translations.get(LANG_ENGLISH, f"[Missing: {key}]")

    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            print(f"⚠️  Warning: Missing format key {e} for '{key}'")

    return text


def get_available_languages():
    """
    Get list of available languages

    Returns:
        Dictionary mapping language codes to display names
    """
    return AVAILABLE_LANGUAGES.copy()


def is_language_supported(language_code):
    """
    Check if a language is supported

    Args:
        language_code: Language code to check

    Returns:
        True if language is supported
    """
    return language_code in AVAILABLE_LANGUAGES


def get_model_path(language_code):
    """
    Get Piper model path for a language

    Args:
        language_code: Language code

    Returns:
        Dictionary with 'model' and 'config' paths, or None if not found
    """
    return MODEL_PATHS.get(language_code)


# ============================================
# VALIDATION
# ============================================

def validate_translations():
    """
    Validate that all translation keys have entries for all languages
    Returns list of issues found
    """
    issues = []

    for key, translations in TRANSLATIONS.items():
        for lang_code in AVAILABLE_LANGUAGES.keys():
            if lang_code not in translations:
                issues.append(f"Missing translation: {key} -> {lang_code}")

    return issues


# Run validation on import (optional - comment out in production)
if __name__ == "__main__":
    print("Validating translations...")
    issues = validate_translations()

    if issues:
        print(f"\n⚠️  Found {len(issues)} translation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All translations complete!")

    # Test examples
    print("\n" + "="*60)
    print("Translation Examples:")
    print("="*60)

    print("\nEnglish:")
    print(f"  System Ready: {get_translation(LANG_ENGLISH, 'system_ready')}")
    print(f"  Object Ahead: {get_translation(LANG_ENGLISH, 'object_ahead', direction='right', angle=30)}")
    print(f"  Keep Right: {get_translation(LANG_ENGLISH, 'object_left_side_keep', direction='right')}")

    print("\nHindi:")
    print(f"  System Ready: {get_translation(LANG_HINDI, 'system_ready')}")
    print(f"  Object Ahead: {get_translation(LANG_HINDI, 'object_ahead', direction='दाएं', angle=30)}")
    print(f"  Keep Right: {get_translation(LANG_HINDI, 'object_left_side_keep', direction='दाएं')}")