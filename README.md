# Fulki API

Backend FastAPI : catalogue, auth par OTP, progression de lecture, URLs audio signées.
L'audio ne transite jamais par l'API — l'app streame directement depuis un bucket AWS S3
via des presigned URLs.

## Lancer en local

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py          # crée fulki.db avec des données de test
uvicorn app.main:app --reload
```

Documentation interactive : http://127.0.0.1:8000/docs

## Endpoints

| Méthode | Route | Rôle |
|---|---|---|
| POST | `/auth/otp` | Envoie un code SMS (renvoyé en clair si `OTP_DEV_MODE=true`) |
| POST | `/auth/verify` | Vérifie le code et renvoie un JWT |
| GET | `/auth/me` | Profil courant |
| GET | `/recordings` | Liste du catalogue publié |
| GET | `/recordings/{id}` | Détail + versets |
| GET | `/recordings/{id}/timestamps` | Calage des versets pour la synchro |
| POST | `/recordings/{id}/signed-url` | URL S3 signée (6 h) |
| GET | `/kourels` | Liste des kourels |
| GET | `/search?q=` | Recherche titre / kourel |
| GET/PUT | `/me/progress` | Reprendre l'écoute |
| POST/DELETE | `/me/favorites/{id}` | Favoris |
| POST | `/me/downloads/{id}` | Téléchargement (quota gratuit : 3) |

## AWS S3

`audio_path` sur `Recording` correspond à la clé de l'objet dans le bucket
(`S3_BUCKET_NAME`), ex. `recordings/matlaboul-fawzeyni-ht/master.m3u8`.
`signing_service.py` génère une presigned URL S3 (`GetObject`, 6 h) via `boto3`.

En local, renseigner `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` dans `.env`
(ou laisser vide pour utiliser la chaîne de credentials par défaut de boto3 :
`~/.aws/credentials`, variables d'environnement AWS, etc.). En production,
préférer un rôle IAM (pas de clés en dur) attaché au service qui exécute l'API.

## Avant la production

- Passer `DATABASE_URL` sur PostgreSQL (asyncpg).
- Remplacer le store OTP en mémoire par Redis, brancher un agrégateur SMS sénégalais.
- Attacher un rôle IAM au service (au lieu de clés statiques) pour la génération des presigned URLs S3.
- Ajouter Alembic pour les migrations à la place de `create_all`.
