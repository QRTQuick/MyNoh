SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_username TEXT UNIQUE,
    display_name TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    remote_url TEXT,
    default_branch TEXT DEFAULT 'main',
    provider TEXT DEFAULT 'github',
    created_at TEXT NOT NULL,
    UNIQUE(name, remote_url)
);

CREATE TABLE IF NOT EXISTS commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    sha TEXT NOT NULL UNIQUE,
    branch TEXT,
    message TEXT,
    pushed_at TEXT,
    processed INTEGER DEFAULT 0,
    FOREIGN KEY(repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    root_cause TEXT,
    difficulty TEXT,
    programming_language TEXT,
    framework TEXT,
    repository TEXT,
    branch TEXT,
    commit_hash TEXT,
    files_affected TEXT,
    stack_overflow_used INTEGER DEFAULT 0,
    ai_assistant_used INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    tags TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS issues_fts USING fts5(
    title, description, root_cause, programming_language, framework, repository,
    files_affected, tags, content='issues', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS issues_ai AFTER INSERT ON issues BEGIN
    INSERT INTO issues_fts(rowid, title, description, root_cause, programming_language, framework, repository, files_affected, tags)
    VALUES (new.id, new.title, new.description, new.root_cause, new.programming_language, new.framework, new.repository, new.files_affected, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS issues_ad AFTER DELETE ON issues BEGIN
    INSERT INTO issues_fts(issues_fts, rowid, title, description, root_cause, programming_language, framework, repository, files_affected, tags)
    VALUES('delete', old.id, old.title, old.description, old.root_cause, old.programming_language, old.framework, old.repository, old.files_affected, old.tags);
END;
CREATE TRIGGER IF NOT EXISTS issues_au AFTER UPDATE ON issues BEGIN
    INSERT INTO issues_fts(issues_fts, rowid, title, description, root_cause, programming_language, framework, repository, files_affected, tags)
    VALUES('delete', old.id, old.title, old.description, old.root_cause, old.programming_language, old.framework, old.repository, old.files_affected, old.tags);
    INSERT INTO issues_fts(rowid, title, description, root_cause, programming_language, framework, repository, files_affected, tags)
    VALUES (new.id, new.title, new.description, new.root_cause, new.programming_language, new.framework, new.repository, new.files_affected, new.tags);
END;

CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER,
    title TEXT,
    markdown TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS issue_tags (
    issue_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(issue_id, tag_id),
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER,
    file_path TEXT NOT NULL,
    caption TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS code_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER,
    language TEXT,
    title TEXT,
    code TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER,
    url TEXT NOT NULL,
    title TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(issue_id) REFERENCES issues(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    encrypted INTEGER DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT,
    status TEXT DEFAULT 'pending',
    scheduled_at TEXT,
    delivered_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    kind TEXT DEFAULT 'manual',
    created_at TEXT NOT NULL
);
"""
