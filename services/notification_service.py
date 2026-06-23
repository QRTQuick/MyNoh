from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class NotificationService:
    def notify(self, title: str, body: str) -> None:
        try:
            from plyer import notification
            notification.notify(title=title, message=body, app_name="Mynoh", timeout=8)
        except Exception as exc:
            log.info("Notification fallback: %s - %s (%s)", title, body, exc)
