#!/home/ken/.virtualenvs/TheCount/bin/python3.12
import os
import sys
from pathlib import Path
import argparse
from typing import Any
from urllib.parse import quote_plus


def in_venv():
    # Detect if running inside a virtualenv
    if os.environ.get('VIRTUAL_ENV'):
        return True
    try:
        import sys as _sys
        return getattr(_sys, 'real_prefix', None) is not None or _sys.base_prefix != _sys.prefix
    except Exception:
        return False


def find_venv_python():
    repo_root = Path(__file__).resolve().parents[1]
    candidates = []
    for name in ('.venv', 'venv', 'env'):
        candidates.append(str(repo_root / name / 'bin' / 'python'))
    # Try bot.py shebang
    bot_file = repo_root / 'bot.py'
    if bot_file.exists():
        try:
            first = bot_file.read_text().splitlines()[0].strip()
            if first.startswith('#!'):
                candidates.append(first[2:].strip())
        except Exception:
            pass

    # Check user's common virtualenvs folder
    venv_home = Path.home() / '.virtualenvs'
    if venv_home.exists():
        for child in venv_home.iterdir():
            candidates.append(str(child / 'bin' / 'python'))

    for p in candidates:
        if p and Path(p).exists() and os.access(p, os.X_OK):
            return p
    return None


# If required packages are missing and we're not in a venv, try to re-exec with repo venv python
missing = []
# Predefine optional imports so static analyzers don't report 'possibly unbound'
yaml: Any = None
create_engine: Any = None
text: Any = None
try:
    import yaml  # PyYAML
except Exception:
    missing.append('pyyaml')

try:
    from sqlalchemy import create_engine, text
except Exception:
    missing.append('sqlalchemy')

if missing and not in_venv() and os.environ.get('MIGRATIONS_REEXEC') != '1':
    venv_python = find_venv_python()
    if venv_python:
        print('Missing packages:', ', '.join(missing))
        print(f"Re-executing with virtualenv python: {venv_python}")
        os.environ['MIGRATIONS_REEXEC'] = '1'
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print('Missing packages:', ', '.join(missing))
        print('No virtualenv detected. Activate your project virtualenv and install requirements:')
        print('  python3 -m venv .venv')
        print('  source .venv/bin/activate')
        print('  pip install -r requirements.txt')
        sys.exit(1)


def load_db_url_from_yaml(cfg_path: Path):
    try:
        with cfg_path.open() as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        return None

    # Try common locations inside the YAML
    db = None
    if isinstance(cfg, dict):
        db = cfg.get('db')
        if not db:
            bc = cfg.get('bot_config') or cfg.get('bot')
            if isinstance(bc, dict):
                db = bc.get('db')

    if not db:
        for key in ('database', 'db_url', 'DATABASE_URL'):
            if key in cfg:
                return cfg[key]
        return None

    if isinstance(db, str):
        return db

    protocol = db.get('protocol')
    if protocol and all(k in db for k in ('user', 'password', 'hostname', 'database')):
        user = quote_plus(str(db['user']))
        password = quote_plus(str(db['password']))
        host = db.get('hostname') or db.get('host')
        port = db.get('port')
        netloc = f"{user}:{password}@{host}"
        if port:
            netloc = f"{netloc}:{port}"
        return f"{protocol}://{netloc}/{db['database']}"
    if 'url' in db:
        return db['url']
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', help='path to counting config YAML')
    args = parser.parse_args()

    db_url = os.environ.get('DATABASE_URL')
    tried = []
    if not db_url:
        # CLI --config
        if args.config is not None:
            p = Path(args.config).expanduser()
            tried.append(str(p))
            if p.exists():
                db_url = load_db_url_from_yaml(p)
        # env override
        if not db_url:
            env_config = os.environ.get('COUNTING_CONFIG')
            if env_config is not None:
                p = Path(env_config).expanduser()
                tried.append(str(p))
                if p.exists():
                    db_url = load_db_url_from_yaml(p)
        # user home location
        if not db_url:
            for name in ('config.yml', 'config.yaml'):
                p = Path.home() / '.countingv2' / name
                tried.append(str(p))
                if p.exists():
                    db_url = load_db_url_from_yaml(p)
                    break
        # repo-local fallback
        if not db_url:
            repo_root = Path(__file__).parent.parent
            for name in ('config.yml', 'config.yaml'):
                p = repo_root / '.countingv2' / name
                tried.append(str(p))
                if p.exists():
                    db_url = load_db_url_from_yaml(p)
                    break

    if not db_url:
        print('No DB configuration found. Tried the following paths:')
        for t in tried:
            print(' -', t)
        print('\nSet DATABASE_URL, use --config, set COUNTING_CONFIG env var, or create ~/.countingv2/config.yml with a db section.')
        sys.exit(1)

    # Prefer using PyMySQL for MySQL connections if not explicitly provided
    if db_url.startswith('mysql://') and 'mysql+' not in db_url:
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)

    engine = create_engine(db_url)
    sql_path = Path(__file__).parent.parent / 'migrations' / 'create_tables.sql'
    if not sql_path.exists():
        print(f'Migration file not found: {sql_path}')
        sys.exit(1)

    sql = sql_path.read_text()
    # Split on semicolons; simple but effective for our migration file
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            print('Executing SQL statement...')
            conn.execute(text(stmt))

    print('Migrations applied successfully.')


if __name__ == '__main__':
    main()
