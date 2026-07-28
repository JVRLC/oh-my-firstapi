"""Populates the database from seed_data/*.json for local testing."""
import asyncio
import json
import re
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.models import Khassaide, Kourel, Recording

SEED_DIR = Path(__file__).parent / "seed_data"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-")


async def main():
    kourels_data = json.loads((SEED_DIR / "kourels.json").read_text())
    khassaides_data = json.loads((SEED_DIR / "khassaides.json").read_text())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        kourels_by_name: dict[str, Kourel] = {}
        # S3 folder prefix per kourel: "<parent-slug>/<child-slug>" for sub-kourels,
        # just "<slug>" for root-level ones.
        kourel_prefix_by_name: dict[str, str] = {}

        for kourel_data in kourels_data:
            children_data = kourel_data.pop("children", [])
            kourel_data.setdefault("slug", _slugify(kourel_data["name"]))
            parent = Kourel(**kourel_data)
            db.add(parent)
            await db.flush()
            kourels_by_name[parent.name] = parent
            kourel_prefix_by_name[parent.name] = parent.slug

            for child_data in children_data:
                child_data.setdefault("slug", _slugify(child_data["name"]))
                child = Kourel(parent_id=parent.id, **child_data)
                db.add(child)
                await db.flush()
                kourels_by_name[child.name] = child
                kourel_prefix_by_name[child.name] = f"{parent.slug}/{child.slug}"

        for kh_data in khassaides_data:
            duration_sec = kh_data.pop("duration_sec")
            audio_path = kh_data.pop("audio_path", None)
            kourel_name = kh_data.pop("kourel")
            event_name = kh_data.pop("event", None)
            kh_data.setdefault("slug", _slugify(kh_data["title_latin"]))

            kh = Khassaide(**kh_data)
            db.add(kh)
            await db.flush()

            if audio_path is None:
                prefix = kourel_prefix_by_name[kourel_name]
                audio_path = f"{prefix}/{kh.slug}.mp3"

            rec = Recording(
                khassaide_id=kh.id,
                kourel_id=kourels_by_name[kourel_name].id,
                event_name=event_name,
                duration_sec=duration_sec,
                audio_path=audio_path,
                is_published=True,
            )
            db.add(rec)

        await db.commit()
    print("Seed terminé.")


if __name__ == "__main__":
    asyncio.run(main())
