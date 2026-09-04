from .models import CenterSettings

def center_settings_processor(request):
    try:
        settings_obj = CenterSettings.get_settings()
    except Exception:
        settings_obj = None

    return {
        'center_settings': settings_obj
    }
