# FitPredictor

ML-powered fitness predictor with two modes:
- **BULK** — predicts per-muscle hypertrophy (cm²) at 3/6/9/12 months
- **CUT** — predicts body fat %, lean muscle mass, and definition score (1–5) at 3/6/9/12 months

---

## Architecture

```
fitpredictor/
├── backend/        ← Flask API (deploy to Railway or Render)
│   ├── app.py
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.toml
└── frontend/       ← Next.js app (deploy to Vercel)
    ├── app/
    │   ├── page.tsx          ← Landing (choose BULK or CUT)
    │   ├── bulk/page.tsx     ← Bulk form + results
    │   ├── cut/page.tsx      ← Cut form + results
    │   └── components/
    │       ├── ExerciseBuilder.tsx
    │       └── Field.tsx
    └── ...
```

---

## Step 1 — Train & Export Your Models

Run both notebooks to generate the `.pkl` files:

**bulk.ipynb** produces:
```
bulkPredictor.pkl
le_gender.pkl
le_exercise.pkl
le_experience.pkl
le_muscle_group.pkl
le_category.pkl
```

**cut.ipynb** produces:
```
models/body_composition_models.pkl
models/le_gender_body.pkl
models/le_experience_body.pkl
models/le_exercise_name_body.pkl
models/le_muscle_group_body.pkl
models/le_exercise_category_body.pkl
```

Copy all these files into `backend/` (bulk `.pkl`s at root, cut `.pkl`s in `backend/models/`).

---

## Step 2 — Deploy the Backend (Railway)

1. Push the `backend/` folder to a GitHub repo (or a subfolder).
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub.
3. Select your repo (set root directory to `backend/` if it's a subfolder).
4. Railway auto-detects Python via `requirements.txt` and uses `Procfile` to start gunicorn.
5. Copy the generated public URL (e.g. `https://fitpredictor-api.railway.app`).

**Alternative: Render**
- New Web Service → connect GitHub → Runtime: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

> ⚠️ The `.pkl` files must be committed to the repo or mounted via a volume — Railway/Render won't have them otherwise. For large models (>100MB), use Railway volumes or upload to S3 and load from URL.

---

## Step 3 — Deploy the Frontend (Vercel)

1. Push the `frontend/` folder to GitHub.
2. Go to [vercel.com](https://vercel.com) → New Project → Import from GitHub.
3. Set **Root Directory** to `frontend/` if it's a subfolder.
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.railway.app
   ```
5. Deploy. Vercel auto-detects Next.js.

---

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
# copy your .pkl files here
python app.py
# → running on http://localhost:3001
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:3001
npm run dev
# → running on http://localhost:3000
```

---

## API Reference

### `POST /bulk`
```json
{
  "age": 24,
  "gender": "M",
  "exercises": [
    {
      "exercise_name": "Dumbbell Curls",
      "sets": 3, "reps": 12, "weight": 15,
      "target_muscle_group": "Biceps",
      "exercise_category": "Isolation"
    }
  ],
  "frequency": 4,
  "protein": 150,
  "calories": 2800,
  "sleep": 7.5,
  "experience": "Intermediate",
  "current_size_cm": 30,
  "workout_time_years": 1
}
```
Response:
```json
{
  "result": {
    "3":  { "Biceps growth": "0.84 cm2" },
    "6":  { "Biceps growth": "1.42 cm2" },
    "9":  { "Biceps growth": "1.91 cm2" },
    "12": { "Biceps growth": "2.33 cm2" }
  }
}
```

### `POST /cut`
```json
{
  "age": 26, "gender": "M",
  "exercises": [...],
  "frequency": 4, "protein": 160, "calories": 2200,
  "sleep": 8, "experience": "Intermediate",
  "genetic_advantage": 3, "daily_deficit": 500,
  "initial_bfp": 20, "current_weight": 82, "height": 178
}
```
Response:
```json
{
  "result": {
    "3":  { "bfp": 16.8, "muscle_mass": 64.2, "definition": 2.8 },
    "6":  { "bfp": 14.2, "muscle_mass": 65.1, "definition": 3.4 },
    "9":  { "bfp": 12.7, "muscle_mass": 65.6, "definition": 3.9 },
    "12": { "bfp": 11.5, "muscle_mass": 65.9, "definition": 4.2 }
  }
}
```

### `GET /health`
```json
{ "status": "ok", "bulk_model": true, "cut_model": true }
```
