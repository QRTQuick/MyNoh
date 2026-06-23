from __future__ import annotations

import flet as ft

from ui import theme


def glass_card(content: list[ft.Control], padding: int = 20) -> ft.Container:
    return ft.Container(
        content=ft.Column(content, spacing=12),
        padding=padding,
        border_radius=24,
        bgcolor=theme.GLASS,
        border=ft.border.all(1, "#FFFFFF22"),
        shadow=ft.BoxShadow(blur_radius=30, color="#00000066", offset=ft.Offset(0, 14)),
    )


def stat_card(label: str, value: str, icon: str) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=18,
        border_radius=22,
        gradient=ft.LinearGradient(colors=["#16213ECC", "#241B44CC"]),
        content=ft.Row([ft.Icon(icon, color=theme.BLUE, size=30), ft.Column([ft.Text(value, size=28, weight=ft.FontWeight.BOLD), ft.Text(label, color=theme.MUTED)])]),
    )
