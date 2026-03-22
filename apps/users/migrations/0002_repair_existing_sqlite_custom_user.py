from django.db import migrations


def repair_existing_sqlite_custom_user(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'sqlite':
        return

    cursor = connection.cursor()
    tables = {row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}

    if 'auth_user' in tables and 'users_user' not in tables:
        cursor.execute(
            """
            CREATE TABLE users_user (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                password varchar(128) NOT NULL,
                last_login datetime NULL,
                is_superuser bool NOT NULL,
                username varchar(150) NOT NULL UNIQUE,
                first_name varchar(150) NOT NULL,
                last_name varchar(150) NOT NULL,
                is_staff bool NOT NULL,
                is_active bool NOT NULL,
                date_joined datetime NOT NULL,
                email varchar(254) NOT NULL UNIQUE
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO users_user (
                id, password, last_login, is_superuser, username,
                first_name, last_name, is_staff, is_active, date_joined, email
            )
            SELECT
                id, password, last_login, is_superuser, username,
                first_name, last_name, is_staff, is_active, date_joined, email
            FROM auth_user
            """
        )

    if 'users_user' in tables:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users_user_groups (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id bigint NOT NULL REFERENCES users_user (id),
                group_id integer NOT NULL REFERENCES auth_group (id)
            )
            """
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_user_groups_user_id_group_id_uniq "
            "ON users_user_groups (user_id, group_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS users_user_groups_group_id_idx "
            "ON users_user_groups (group_id)"
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users_user_user_permissions (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id bigint NOT NULL REFERENCES users_user (id),
                permission_id integer NOT NULL REFERENCES auth_permission (id)
            )
            """
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_user_perms_user_id_permission_id_uniq "
            "ON users_user_user_permissions (user_id, permission_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS users_user_perms_permission_id_idx "
            "ON users_user_user_permissions (permission_id)"
        )

        if 'auth_user_groups' in tables:
            existing = cursor.execute(
                "SELECT COUNT(*) FROM users_user_groups"
            ).fetchone()[0]
            if existing == 0:
                cursor.execute(
                    """
                    INSERT INTO users_user_groups (id, user_id, group_id)
                    SELECT id, user_id, group_id
                    FROM auth_user_groups
                    """
                )

        if 'auth_user_user_permissions' in tables:
            existing = cursor.execute(
                "SELECT COUNT(*) FROM users_user_user_permissions"
            ).fetchone()[0]
            if existing == 0:
                cursor.execute(
                    """
                    INSERT INTO users_user_user_permissions (id, user_id, permission_id)
                    SELECT id, user_id, permission_id
                    FROM auth_user_user_permissions
                    """
                )

    if 'users_profile' in tables:
        profile_columns = [
            row[1] for row in cursor.execute("PRAGMA table_info(users_profile)")
        ]
        profile_fk = list(cursor.execute("PRAGMA foreign_key_list(users_profile)"))
        fk_targets = {row[2] for row in profile_fk if row[3] == 'user_id'}
        needs_rebuild = (
            'phone' in profile_columns
            or 'avatar' not in profile_columns
            or fk_targets != {'users_user'}
        )

        if needs_rebuild:
            avatar_select = 'avatar' if 'avatar' in profile_columns else 'NULL'
            cursor.execute("ALTER TABLE users_profile RENAME TO users_profile_old")
            cursor.execute(
                """
                CREATE TABLE users_profile (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    display_name varchar(150) NOT NULL,
                    avatar varchar(100) NULL,
                    created_at datetime NOT NULL,
                    user_id bigint NOT NULL UNIQUE REFERENCES users_user (id)
                )
                """
            )
            cursor.execute(
                f"""
                INSERT INTO users_profile (id, display_name, avatar, created_at, user_id)
                SELECT id, display_name, {avatar_select}, created_at, user_id
                FROM users_profile_old
                """
            )
            cursor.execute("DROP TABLE users_profile_old")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(repair_existing_sqlite_custom_user, migrations.RunPython.noop),
    ]
