import aiosqlite
import os
import csv
from datetime import datetime
from .models import CitizenRequest, DistrictPriority

DB_PATH = os.path.join(os.path.dirname(__file__), "jansetu.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS citizen_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT,
                translated_text TEXT,
                language_detected TEXT,
                category TEXT,
                location_district TEXT,
                location_state TEXT,
                urgency INTEGER,
                sentiment TEXT,
                latitude REAL,
                longitude REAL,
                timestamp TEXT,
                source TEXT,
                data_type TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS districts (
                name TEXT,
                state TEXT,
                lat REAL,
                lng REAL,
                population INTEGER,
                infra_index REAL,
                PRIMARY KEY (name, state)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS priority_scores (
                district_name TEXT,
                state TEXT,
                priority_score REAL,
                demand_density REAL,
                infra_gap REAL,
                population_weight REAL,
                urgency_factor REAL,
                category_breakdown TEXT,
                total_requests INTEGER,
                top_issues TEXT,
                PRIMARY KEY (district_name, state)
            )
        """)
        await db.commit()
        await load_csv_data(db)
        await load_synthetic_data(db)

async def load_csv_data(db):
    # Load CSV data if it exists in the data directory
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "districts.csv")
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                await db.execute("""
                    INSERT OR IGNORE INTO districts (name, state, lat, lng, population, infra_index)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (row['district_name'], row['state'], float(row['latitude']), float(row['longitude']), int(row['population']), float(row['infra_index'])))
        await db.commit()

async def load_synthetic_data(db):
    """Load synthetic requests JSON into DB if the table is empty."""
    import json
    cursor = await db.execute("SELECT COUNT(*) FROM citizen_requests")
    count = (await cursor.fetchone())[0]
    if count > 0:
        return  # Already has data

    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_requests.json")
    if not os.path.exists(json_path):
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        requests = json.load(f)

    for req in requests:
        await db.execute("""
            INSERT INTO citizen_requests (
                raw_text, translated_text, language_detected, category,
                location_district, location_state, urgency, sentiment,
                latitude, longitude, timestamp, source, data_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req.get('raw_text', ''),
            req.get('translated_text', ''),
            req.get('language_detected', ''),
            req.get('category', ''),
            req.get('location_district', ''),
            req.get('location_state', ''),
            req.get('urgency', 3),
            req.get('sentiment', 'NEGATIVE'),
            req.get('latitude'),
            req.get('longitude'),
            req.get('timestamp', datetime.utcnow().isoformat()),
            req.get('source', 'TELEGRAM'),
            req.get('data_type', 'SYNTHETIC')
        ))
    await db.commit()
    print(f"Loaded {len(requests)} synthetic requests into database.")

async def insert_request(req: CitizenRequest) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO citizen_requests (
                raw_text, translated_text, language_detected, category, 
                location_district, location_state, urgency, sentiment, 
                latitude, longitude, timestamp, source, data_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req.raw_text, req.translated_text, req.language_detected, req.category.value,
            req.location_district, req.location_state, req.urgency, req.sentiment.value,
            req.latitude, req.longitude, req.timestamp.isoformat(), req.source.value, req.data_type.value
        ))
        await db.commit()
        return cursor.lastrowid

async def get_all_requests():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM citizen_requests")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_requests_by_district(district: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM citizen_requests WHERE location_district = ?", (district,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_districts():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM districts")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def upsert_priority_score(score: DistrictPriority):
    import json
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO priority_scores (
                district_name, state, priority_score, demand_density,
                infra_gap, population_weight, urgency_factor, category_breakdown,
                total_requests, top_issues
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(district_name, state) DO UPDATE SET
                priority_score=excluded.priority_score,
                demand_density=excluded.demand_density,
                infra_gap=excluded.infra_gap,
                population_weight=excluded.population_weight,
                urgency_factor=excluded.urgency_factor,
                category_breakdown=excluded.category_breakdown,
                total_requests=excluded.total_requests,
                top_issues=excluded.top_issues
        """, (
            score.district_name, score.state, score.priority_score, score.demand_density,
            score.infra_gap, score.population_weight, score.urgency_factor,
            json.dumps(score.category_breakdown), score.total_requests, json.dumps(score.top_issues)
        ))
        await db.commit()

async def get_priority_scores():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM priority_scores ORDER BY priority_score DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
