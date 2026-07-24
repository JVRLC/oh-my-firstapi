"""Populates the database with one kourel and a few khassaides for local testing."""
import asyncio

from app.database import Base, SessionLocal, engine
from app.models import Khassaide, Kourel, Recording, Verse, VerseTiming

VERSES = [
    (
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "Bismillāhi r-Raḥmāni r-Raḥīm",
        "Au nom d'Allah, le Tout Miséricordieux, le Très Miséricordieux",
    ),
    (
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "Al-ḥamdu lillāhi rabbi l-ʿālamīn",
        "Louange à Allah, Seigneur des mondes",
    ),
    ("— vers ٣ —", "Texte du khassaïde à intégrer", "Traduction à valider"),
    ("— vers ٤ —", "Texte du khassaïde à intégrer", "Traduction à valider"),
]

KHASSAIDES = [
    ("matlaboul-fawzeyni", "Matlaboul Fawzeyni", "مطلب", "La quête des deux bonheurs", 2536),
    ("djazboul-khoulob", "Djazboul Khoulob", "جذب", "L'attraction des cœurs", 2100),
    ("mawahibou-nafih", "Mawâhibou Nafih", "مواهب", "Les dons utiles", 1680),
]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        kourel = Kourel(
            name="Kourel Hizbut-Tarqiyyah",
            city="Touba",
            bio="Le Kourel Hizbut-Tarqiyyah perpétue la déclamation des khassaïdes "
            "de Cheikh Ahmadou Bamba depuis Touba.",
            is_partner=True,
            revenue_share=30,
        )
        db.add(kourel)
        await db.flush()

        for slug, title, arabic, meaning, duration in KHASSAIDES:
            kh = Khassaide(
                slug=slug, title_latin=title, title_arabic=arabic, meaning_fr=meaning
            )
            db.add(kh)
            await db.flush()

            verses = []
            for i, (ar, tl, fr) in enumerate(VERSES, start=1):
                v = Verse(
                    khassaide_id=kh.id,
                    position=i,
                    text_arabic=ar,
                    translit=tl,
                    translation_fr=fr,
                    is_validated=i <= 2,
                )
                db.add(v)
                verses.append(v)
            await db.flush()

            rec = Recording(
                khassaide_id=kh.id,
                kourel_id=kourel.id,
                duration_sec=duration,
                audio_path=f"recordings/{slug}-ht/master.m3u8",
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
