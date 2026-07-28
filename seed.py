"""Populates the database from seed_data.json for local testing."""
import asyncio
import json
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Khassaide, Kourel, Recording, Verse, VerseTiming

SEED_FILE = Path(__file__).parent / "seed_data.json"


async def main():
    data = json.loads(SEED_FILE.read_text())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        kourels_by_name: dict[str, Kourel] = {}

        for kourel_data in data["kourels"]:
            children_data = kourel_data.pop("children", [])
            parent = Kourel(**kourel_data)
            db.add(parent)
            await db.flush()
            kourels_by_name[parent.name] = parent

            for child_data in children_data:
                child = Kourel(parent_id=parent.id, **child_data)
                db.add(child)
                await db.flush()
                kourels_by_name[child.name] = child

        for kh_data in data["khassaides"]:
            verses_data = kh_data.pop("verses")
            duration_sec = kh_data.pop("duration_sec")
            audio_path = kh_data.pop("audio_path")
            kourel_name = kh_data.pop("kourel")

            kh = Khassaide(**kh_data)
            db.add(kh)
            await db.flush()

            verses = []
            for i, v_data in enumerate(verses_data, start=1):
                v = Verse(khassaide_id=kh.id, position=i, **v_data)
                db.add(v)
                verses.append(v)
            await db.flush()

            rec = Recording(
                khassaide_id=kh.id,
                kourel_id=kourels_by_name[kourel_name].id,
                duration_sec=duration_sec,
                audio_path=audio_path,
                is_published=True,
            )
            db.add(rec)
            await db.flush()

            # Placeholder timings: one verse every 20 seconds.
            for idx, v in enumerate(verses):
                db.add(
                    VerseTiming(
                        recording_id=rec.id,
                        verse_id=v.id,
                        start_ms=idx * 20000,
                        end_ms=(idx + 1) * 20000,
                    )
                )

        await db.commit()
    print("Seed terminé.")


if __name__ == "__main__":
    asyncio.run(main())
