"""
Optional Firebase Cloud Messaging (FCM) push notifications.

Activates only when FCM credentials are configured (settings.FCM_ENABLED). Every
helper is safe to call unconditionally: when FCM is off they no-op and return a
small result dict, so app code never has to check first.

Send helpers:
    fcm.send_to_user(user, title, body, data=None)
    fcm.send_to_users(users, title, body, data=None)
    fcm.send_to_all(title, body, data=None)
    fcm.send_to_tokens(tokens, title, body, data=None)

Each returns e.g. {"sent": 3, "failed": 0, "enabled": True}.
"""
import json

from django.conf import settings

_app = None


def notifications_enabled() -> bool:
    return bool(getattr(settings, "FCM_ENABLED", False))


def _get_app():
    """Lazily initialise (and cache) the Firebase app. None when disabled."""
    global _app
    if _app is not None:
        return _app
    if not notifications_enabled():
        return None
    import firebase_admin
    from firebase_admin import credentials

    if settings.FCM_CREDENTIALS_JSON:
        cred = credentials.Certificate(json.loads(settings.FCM_CREDENTIALS_JSON))
    else:
        cred = credentials.Certificate(settings.FCM_CREDENTIALS_FILE)
    try:
        _app = firebase_admin.get_app()
    except ValueError:
        _app = firebase_admin.initialize_app(cred)
    return _app


def _send(tokens, title, body, data=None):
    tokens = [t for t in dict.fromkeys(tokens) if t]  # de-dupe, drop blanks
    if not tokens:
        return {"sent": 0, "enabled": notifications_enabled(), "detail": "no active tokens"}
    if _get_app() is None:
        return {"sent": 0, "enabled": False, "detail": "FCM not configured"}

    from firebase_admin import messaging

    sent = failed = 0
    dead = []
    for i in range(0, len(tokens), 500):  # FCM multicast caps at 500
        chunk = tokens[i : i + 500]
        message = messaging.MulticastMessage(
            tokens=chunk,
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
        )
        resp = messaging.send_each_for_multicast(message)
        sent += resp.success_count
        failed += resp.failure_count
        for tok, r in zip(chunk, resp.responses):
            if not r.success and isinstance(r.exception, messaging.UnregisteredError):
                dead.append(tok)

    if dead:
        from .models import DeviceToken

        DeviceToken.objects.filter(token__in=dead).update(is_active=False)

    return {"sent": sent, "failed": failed, "enabled": True}


def send_to_tokens(tokens, title, body, data=None):
    return _send(list(tokens), title, body, data)


def send_to_user(user, title, body, data=None):
    from .models import DeviceToken

    tokens = DeviceToken.objects.filter(user=user, is_active=True).values_list("token", flat=True)
    return _send(list(tokens), title, body, data)


def send_to_users(users, title, body, data=None):
    from .models import DeviceToken

    tokens = DeviceToken.objects.filter(user__in=users, is_active=True).values_list("token", flat=True)
    return _send(list(tokens), title, body, data)


def send_to_all(title, body, data=None):
    from .models import DeviceToken

    tokens = DeviceToken.objects.filter(is_active=True).values_list("token", flat=True)
    return _send(list(tokens), title, body, data)
