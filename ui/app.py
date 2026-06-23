from __future__ import annotations

import asyncio
from typing import Any

import flet as ft

from database.connection import Database
from database.repositories import IssueRepository, SettingsRepository
from services.dashboard_service import DashboardService
from services.export_service import ExportService
from services.knowledge_service import KnowledgeService
from services.search_service import SearchService
from settings.config import AppConfig
from ui import theme
from ui.components import glass_card, stat_card
from ui.floating_assistant import FloatingAssistant
from utils.security import SecretStore


class MynohApp:
    def __init__(self, page: ft.Page, config: AppConfig) -> None:
        self.page = page
        self.config = config
        self.db = Database(config.database_path)
        self.db.initialize()
        self.issue_repo = IssueRepository(self.db)
        self.settings_repo = SettingsRepository(self.db)
        self.knowledge = KnowledgeService(self.issue_repo)
        self.search_service = SearchService(self.knowledge)
        self.dashboard = DashboardService(self.db)
        self.exporter = ExportService(config.export_dir)
        self.secrets = SecretStore(config.data_dir / "secrets" / "fallback.key")
        self.assistant = FloatingAssistant(page)
        self.search_box = ft.TextField(hint_text="Search bugs, snippets, repositories…", prefix_icon=ft.Icons.SEARCH, expand=True, on_submit=self.on_search)
        self.results = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.timeline = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.stats_row = ft.Row(spacing=14)

    def setup(self) -> None:
        p = self.page
        p.title = "Mynoh — Developer Memory Assistant"
        p.theme_mode = ft.ThemeMode.DARK
        p.bgcolor = theme.DARK_BG
        p.window.min_width = 1100
        p.window.min_height = 760
        p.padding = 0
        p.on_keyboard_event = self.on_key
        p.add(self.layout())
        self.refresh_dashboard()
        self.refresh_timeline()
        self.assistant.mount()

    def layout(self) -> ft.Control:
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            bgcolor="#090D18",
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.Icons.SEARCH, label="Search"),
                ft.NavigationRailDestination(icon=ft.Icons.TIMELINE, label="Timeline"),
                ft.NavigationRailDestination(icon=ft.Icons.ADD_CIRCLE, label="Capture"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            on_change=lambda e: self.switch_tab(e.control.selected_index),
        )
        self.stack = ft.Stack([self.dashboard_view()], expand=True)
        return ft.Row([rail, ft.VerticalDivider(width=1), self.stack], expand=True)

    def switch_tab(self, idx: int) -> None:
        views = [self.dashboard_view, self.search_view, self.timeline_view, self.capture_view, self.settings_view]
        self.stack.controls = [views[idx]()] 
        self.page.update()

    def header(self, title: str, subtitle: str) -> ft.Control:
        return ft.Row([
            ft.Column([ft.Text(title, size=34, weight=ft.FontWeight.BOLD), ft.Text(subtitle, color=theme.MUTED)]),
            ft.Container(expand=True),
            ft.Container(content=ft.Text("⌘/Ctrl+K Search  •  Ctrl+N Capture", color=theme.MUTED), padding=12, border_radius=14, bgcolor="#FFFFFF10"),
        ])

    def dashboard_view(self) -> ft.Control:
        return ft.Container(padding=28, expand=True, content=ft.Column([
            self.header("Mynoh", "Your intelligent developer memory assistant"),
            self.stats_row,
            glass_card([ft.Text("Productivity Trends", size=20, weight=ft.FontWeight.BOLD), ft.Text("Charts and heatmaps are generated from your captured issues. Export data for deeper BI analysis.", color=theme.MUTED)]),
        ], spacing=22))

    def refresh_dashboard(self) -> None:
        s = self.dashboard.stats()
        self.stats_row.controls = [
            stat_card("Bugs solved", str(s["total_bugs_solved"]), ft.Icons.BUG_REPORT),
            stat_card("Knowledge entries", str(s["knowledge_entries"]), ft.Icons.LIBRARY_BOOKS),
            stat_card("Hours saved", str(s["hours_saved"]), ft.Icons.SCHEDULE),
            stat_card("Repositories", str(s["repositories_tracked"]), ft.Icons.ACCOUNT_TREE),
        ]

    def search_view(self) -> ft.Control:
        return ft.Container(padding=28, expand=True, content=ft.Column([
            self.header("Intelligent Search", "Keyword and natural-language search across your developer memory"),
            ft.Row([self.search_box, ft.FilledButton("Search", icon=ft.Icons.SEARCH, on_click=self.on_search)]),
            self.results,
        ], spacing=18))

    def timeline_view(self) -> ft.Control:
        self.refresh_timeline()
        return ft.Container(padding=28, expand=True, content=ft.Column([
            self.header("Timeline", "Chronological history of captured issues"), self.timeline
        ], spacing=18))

    def refresh_timeline(self) -> None:
        self.timeline.controls = [self.issue_card(i) for i in self.knowledge.timeline(100)] or [ft.Text("No entries yet. Capture your first solved bug.", color=theme.MUTED)]

    def issue_card(self, i: dict[str, Any]) -> ft.Control:
        return ft.ExpansionTile(
            title=ft.Text(i.get("title", "Untitled"), weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"{i.get('created_at','')[:10]} • {i.get('repository','')} • {i.get('tags','')}", color=theme.MUTED),
            controls=[ft.Container(padding=12, content=ft.Column([
                ft.Text("Problem", weight=ft.FontWeight.BOLD), ft.Text(i.get("description", "")),
                ft.Text("Root cause", weight=ft.FontWeight.BOLD), ft.Text(i.get("root_cause", "")),
                ft.Text(f"Language: {i.get('programming_language','')}  Framework: {i.get('framework','')}  Difficulty: {i.get('difficulty','')}", color=theme.MUTED),
            ]))],
        )

    def capture_view(self) -> ft.Control:
        fields = {name: ft.TextField(label=label, multiline=multi, min_lines=3 if multi else 1) for name, label, multi in [
            ("title", "Problem title", False), ("description", "Detailed bug description", True), ("root_cause", "Root cause", True),
            ("solution", "How it was solved", True), ("files_affected", "Files affected", False), ("programming_language", "Programming language", False),
            ("framework", "Framework", False), ("repository", "Repository", False), ("branch", "Branch", False), ("commit_hash", "Commit hash", False),
            ("tags", "Tags", False), ("code_snippet", "Code snippet", True)
        ]}
        difficulty = ft.Dropdown(label="Difficulty", value="Medium", options=[ft.dropdown.Option(x) for x in ["Easy","Medium","Hard"]])
        time_spent = ft.TextField(label="Time spent (minutes)", value="0")
        def save(_):
            payload = {k:v.value for k,v in fields.items()}
            payload["difficulty"] = difficulty.value; payload["time_spent_minutes"] = time_spent.value
            self.knowledge.capture_bug(payload)
            self.refresh_dashboard(); self.refresh_timeline()
            self.page.snack_bar = ft.SnackBar(ft.Text("Saved to Mynoh memory")); self.page.snack_bar.open = True; self.page.update()
        return ft.Container(padding=28, expand=True, content=ft.Column([
            self.header("Capture Knowledge", "Preserve bugs, decisions, snippets and lessons learned"),
            ft.Container(expand=True, content=ft.ListView([*fields.values(), difficulty, time_spent, ft.FilledButton("Save Memory", icon=ft.Icons.SAVE, on_click=save)], spacing=12))
        ], spacing=18))

    def settings_view(self) -> ft.Control:
        username = ft.TextField(label="GitHub username", value=self.settings_repo.get("github_username"))
        repo = ft.TextField(label="Default repository", value=self.settings_repo.get("default_repository"))
        branch = ft.TextField(label="Default branch", value=self.settings_repo.get("default_branch", "main"))
        token = ft.TextField(label="Personal access token", password=True, can_reveal_password=True, value="")
        interval = ft.TextField(label="Reminder interval seconds", value=str(self.config.reminder_interval_seconds))
        def save(_):
            self.settings_repo.set("github_username", username.value)
            self.settings_repo.set("default_repository", repo.value)
            self.settings_repo.set("default_branch", branch.value)
            if token.value: self.secrets.set_secret("github_token", token.value)
            self.settings_repo.set("reminder_interval_seconds", interval.value)
            self.page.snack_bar = ft.SnackBar(ft.Text("Settings saved securely")); self.page.snack_bar.open = True; self.page.update()
        return ft.Container(padding=28, expand=True, content=ft.Column([
            self.header("Settings", "Theme, GitHub, backup, notifications and AI preferences"),
            glass_card([username, token, repo, branch, interval, ft.Switch(label="Start with OS (configure via scripts/install_startup.py)"), ft.Switch(label="Quiet hours enabled"), ft.FilledButton("Save Settings", icon=ft.Icons.LOCK, on_click=save)])
        ], spacing=18))

    def on_search(self, _=None) -> None:
        rows = self.search_service.natural_language_search(self.search_box.value or "")
        self.results.controls = [self.issue_card(r) for r in rows] or [ft.Text("No matching memories found.", color=theme.MUTED)]
        self.page.update()

    def on_key(self, e: ft.KeyboardEvent) -> None:
        if e.ctrl and e.key.lower() == "k": self.switch_tab(1)
        if e.ctrl and e.key.lower() == "n": self.switch_tab(3)


def run_app(config: AppConfig) -> None:
    def target(page: ft.Page) -> None:
        MynohApp(page, config).setup()
    ft.app(target=target, assets_dir="assets")
