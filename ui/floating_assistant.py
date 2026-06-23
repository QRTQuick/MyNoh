from __future__ import annotations

import flet as ft

from ui import theme


class FloatingAssistant:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.banner = ft.Container(
            left=24,
            top=-180,
            opacity=0,
            animate_position=ft.Animation(550, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_opacity=ft.Animation(350, ft.AnimationCurve.EASE_IN_OUT),
            width=460,
            padding=22,
            border_radius=28,
            bgcolor="#111827DD",
            blur=ft.Blur(18, 18),
            border=ft.border.all(1, "#FFFFFF26"),
            shadow=ft.BoxShadow(blur_radius=36, color="#00000088", offset=ft.Offset(0, 16)),
        )

    def mount(self) -> None:
        if self.banner not in self.page.overlay:
            self.page.overlay.append(self.banner)

    async def show_push_prompt(self, on_yes, on_no=None, on_later=None) -> None:
        self.mount()
        self.banner.content = ft.Column([
            ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color=theme.PURPLE), ft.Text("Mynoh Memory Check", size=18, weight=ft.FontWeight.BOLD)]),
            ft.Text("Did you encounter any bugs while building this feature?", size=15, color=theme.TEXT),
            ft.Row([
                ft.FilledButton("Yes", icon=ft.Icons.BUG_REPORT, on_click=on_yes),
                ft.OutlinedButton("No", on_click=on_no),
                ft.TextButton("Remind Me Later", on_click=on_later),
            ]),
        ])
        await self._animate_in()

    async def show_inactivity_prompt(self, on_still, on_solved, on_help) -> None:
        self.mount()
        self.banner.content = ft.Column([
            ft.Row([ft.Icon(ft.Icons.PSYCHOLOGY, color=theme.BLUE), ft.Text("Still coding?", size=18, weight=ft.FontWeight.BOLD)]),
            ft.Text("What challenge are you currently working on?", size=15, color=theme.TEXT),
            ft.Row([
                ft.FilledButton("Still Working", on_click=on_still),
                ft.OutlinedButton("Solved It", on_click=on_solved),
                ft.TextButton("Need Help", on_click=on_help),
            ]),
        ])
        await self._animate_in()

    async def _animate_in(self) -> None:
        self.banner.top = 24
        self.banner.opacity = 1
        self.page.update()

    def hide(self) -> None:
        self.banner.top = -180
        self.banner.opacity = 0
        self.page.update()
