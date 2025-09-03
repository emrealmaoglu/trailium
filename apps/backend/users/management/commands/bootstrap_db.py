import getpass
import os
import sys
from pathlib import Path

import psycopg2
from django.core.management.base import BaseCommand, CommandError


def _load_env_from_file(env_path: Path) -> None:
    """Basit .env yükleyici (yerel/demo amaçlı).

    Açıklama
    ---------
    Yerel/demo ortamında, `apps/backend/.env` dosyasından PostgreSQL
    bağlantı bilgilerini okur. `python-dotenv` mevcutsa onu kullanır; değilse
    satırları minimal biçimde ayrıştırır. Üretim amaçlı değildir.

    Notlar
    ------
    - Kullanılan değişkenler: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
      POSTGRES_HOST, POSTGRES_PORT, PG_SUPERUSER, PG_SUPERPASSWORD.
    - Sadece mevcut olmayan ortam değişkenlerini set eder.
    """

    try:
        # Tercihen dotenv kullan
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=str(env_path), override=False)
        return
    except Exception:
        pass

    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class Command(BaseCommand):
    help = (
        "Yerel/demo için Postgres rolü ve veritabanını oluşturur. "
        ".env içinden değişkenleri okur ve yoksa rol/DB yaratır."
    )

    def handle(self, *args, **options):
        """Yerel Postgres rol + veritabanı bootstrap işlemi.

        Açıklama
        ---------
        Bu komut yalnızca yerel/demo ortamları içindir. `apps/backend/.env`
        dosyasından PostgreSQL yapılandırmasını (POSTGRES_DB, POSTGRES_USER,
        POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT) okur. Bir süper kullanıcı
        bağlantısı (PG_SUPERUSER/PG_SUPERPASSWORD) ile 127.0.0.1:5432 üzerinden
        bağlanmaya çalışır ve eksik ise rolü ve veritabanını oluşturur.

        Adımlar
        -------
        1) Süper kullanıcıya bağlan (varsayılan postgres).
        2) Rol mevcut mu kontrol et; yoksa CREATE ROLE ... LOGIN PASSWORD ...
        3) Veritabanı mevcut mu kontrol et; yoksa CREATE DATABASE ... OWNER ...
        4) GRANT ALL PRIVILEGES ON DATABASE ... TO ...

        Notlar
        ------
        - İdempotent olacak şekilde tasarlanmıştır; mevcut objeler için sadece bilgi mesajı basar.
        - Üretim mantığını değiştirmez; sadece yerel kurulum kolaylığı sağlar.
        """

        project_root = Path(__file__).resolve().parents[4]
        backend_dir = project_root / "apps" / "backend"
        env_path = backend_dir / ".env"

        _load_env_from_file(env_path)

        pg_db = os.environ.get("POSTGRES_DB", "trailium")
        pg_user = os.environ.get("POSTGRES_USER", "trailium")
        pg_password = os.environ.get("POSTGRES_PASSWORD", "trailium")
        pg_host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
        pg_port = int(os.environ.get("POSTGRES_PORT", "5432"))

        su_user = os.environ.get("PG_SUPERUSER", "postgres")
        su_pass = os.environ.get("PG_SUPERPASSWORD")
        if not su_pass and sys.stdin.isatty():
            try:
                su_pass = getpass.getpass(
                    f"Postgres superuser password for '{su_user}': "
                )
            except Exception:
                su_pass = None

        if not su_pass:
            self.stderr.write(
                "Superuser password not provided. Set PG_SUPERPASSWORD or run interactively."
            )
            raise CommandError("Missing PG_SUPERPASSWORD for bootstrap")

        # Süper kullanıcı ile maintenance db'ye bağlan (postgres)
        self.stdout.write(
            self.style.NOTICE(
                f"Connecting as superuser '{su_user}' to {pg_host}:{pg_port}/postgres ..."
            )
        )
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=su_user,
                password=su_pass,
                host=pg_host,
                port=pg_port,
            )
            conn.autocommit = True
        except Exception as exc:
            self.stderr.write("Could not connect to Postgres as superuser.")
            self.stderr.write(
                "Hint: Ensure local Postgres is running and credentials are correct (PG_SUPERUSER/PG_SUPERPASSWORD)."
            )
            raise CommandError(str(exc))

        try:
            with conn.cursor() as cur:
                # Rol mevcut mu?
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (pg_user,))
                role_exists = cur.fetchone() is not None
                if role_exists:
                    self.stdout.write(
                        self.style.SUCCESS(f"Role '{pg_user}' already exists.")
                    )
                else:
                    cur.execute(
                        f"CREATE ROLE {psycopg2.extensions.AsIs(pg_user)} LOGIN PASSWORD %s",
                        (pg_password,),
                    )
                    self.stdout.write(self.style.SUCCESS(f"Role '{pg_user}' created."))

                # Veritabanı mevcut mu?
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (pg_db,))
                db_exists = cur.fetchone() is not None
                if db_exists:
                    self.stdout.write(
                        self.style.SUCCESS(f"Database '{pg_db}' already exists.")
                    )
                else:
                    # OWNER kullanıcı adı quote edilmeden kullanılacağı için AsIs kullanıyoruz
                    cur.execute(
                        f"CREATE DATABASE {psycopg2.extensions.AsIs(pg_db)} OWNER {psycopg2.extensions.AsIs(pg_user)}"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Database '{pg_db}' created with owner '{pg_user}'."
                        )
                    )

                # GRANT ALL PRIVILEGES (idempotent; var olan grant'ler tekrar verilse hata değildir)
                cur.execute(
                    f"GRANT ALL PRIVILEGES ON DATABASE {psycopg2.extensions.AsIs(pg_db)} TO {psycopg2.extensions.AsIs(pg_user)}"
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Granted ALL on '{pg_db}' to '{pg_user}'.")
                )

        finally:
            conn.close()

        self.stdout.write(
            self.style.SUCCESS("Bootstrap complete. You can now run migrations.")
        )
        self.stdout.write("Next: python manage.py migrate")
