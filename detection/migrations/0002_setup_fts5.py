from django.db import migrations

def create_fts5_table(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS news_index_fts USING fts5(
                    title,
                    summary,
                    source,
                    label UNINDEXED,
                    content_hash UNINDEXED,
                    tokenize = 'porter unicode61'
                );
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_indexed_news_insert AFTER INSERT ON detection_indexednews
                BEGIN
                    INSERT INTO news_index_fts(rowid, title, summary, source, label, content_hash)
                    VALUES (new.id, new.title, new.summary, new.source, new.label, new.content_hash);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_indexed_news_delete AFTER DELETE ON detection_indexednews
                BEGIN
                    DELETE FROM news_index_fts WHERE rowid = old.id;
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_indexed_news_update AFTER UPDATE ON detection_indexednews
                BEGIN
                    DELETE FROM news_index_fts WHERE rowid = old.id;
                    INSERT INTO news_index_fts(rowid, title, summary, source, label, content_hash)
                    VALUES (new.id, new.title, new.summary, new.source, new.label, new.content_hash);
                END;
            """)

def drop_fts5_table(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("DROP TRIGGER IF EXISTS trg_indexed_news_insert;")
            cursor.execute("DROP TRIGGER IF EXISTS trg_indexed_news_delete;")
            cursor.execute("DROP TRIGGER IF EXISTS trg_indexed_news_update;")
            cursor.execute("DROP TABLE IF EXISTS news_index_fts;")

class Migration(migrations.Migration):
    dependencies = [
        ('detection', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_fts5_table, reverse_code=drop_fts5_table),
    ]
