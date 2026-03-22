from django.db import migrations


def create_missing_custom_user_m2m_tables(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'sqlite':
        return

    cursor = connection.cursor()
    tables = {
        row[0] for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }

    if 'users_user' not in tables:
        return

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


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_repair_existing_sqlite_custom_user'),
    ]

    operations = [
        migrations.RunPython(
            create_missing_custom_user_m2m_tables,
            migrations.RunPython.noop,
        ),
    ]
