# Todo

Tracks the implementation of [plan.md](plan.md). Naming convention: English
identifiers in code (`department`, `archive_folder`, `document_view`), Uzbek labels in
UI via `app/utils/labels.ts`.

User model and roles are **not** modified in this iteration.

## Phase 1: Department (Bo'lim)

- [x] **1.1** Department domain entity, model, repository, migration ✅ commit `a2fa1f8`
- [x] **1.2** Department API: CRUD + `/activate` + `/deactivate` (admin-gated mutations) ✅ commit `b90cfdc`
- [x] **1.3** Frontend types + `useDepartments()` composable + `labels.ts` map +
  sidebar nav entry ✅ commit `3ff5736`
- [x] **1.4** `/admin/departments` card-grid page (create / edit / delete modals) ✅ commit pending below

### Checkpoint — Phase 1
- [x] `make migrate` clean on fresh + populated DBs
- [x] Admin can create / rename / activate-deactivate / delete a department (API + SSR verified)
- [x] Archive flow regression check — no existing files touched outside new aggregates + 3 wiring edits
- [x] Phase 1 commits landed (`a2fa1f8`, `b90cfdc`, `3ff5736`, + 1.4)
- [ ] **Human review**

---

## Phase 2: Archive Folder (Yig'ma jild)

- [x] **2.1** Archive Folder domain entity, model, repository, migration ✅ commit `4303b42`
- [x] **2.2** Archive Folder API (CRUD, list filters, `document_count` stub = 0) ✅ commit `c02dad2`
- [x] **2.3** Frontend types + `useArchiveFolders()` + labels + sidebar nav entry ✅ commit `cab27de`
- [x] **2.4** `/archive-folders` list page with 7 columns + create/edit modal ✅ commit `053f000`

### Checkpoint — Phase 2
- [x] Archive folders CRUD works end-to-end (API 16-case + SSR 17-check verified)
- [x] Year filter functional (useAsyncData watch auto-refetch)
- [x] No regression on Phase 1 or archive — only new files + append-only edits
- [x] Phase 2 commits landed (`4303b42`, `c02dad2`, `cab27de`, `053f000`)

---

## Phase 3: Document overhaul

### Pre-phase block: all Open Questions resolved
- [x] Conditional extras per `document_view` → locked (see plan.md)
- [x] Retention period format → **enum** (3/5/10/25/50/75/permanent/epk)

### Tasks
- [x] **3.1** Document model: `document_view`, `archive_folder_id`, common new
  columns, view-specific extras, migration with `'unknown'` backfill ✅ commit `87ce79a`
- [x] **3.2** Document API: extended request/response + server-side conditional
  validation + filter params ✅ commit `c7e527f`
- [x] **3.3** Archive Folder list query: real `COUNT()` for `document_count` ✅ commit `5592f99`
- [x] **3.4** Document create form: `document_view` select + conditional fields +
  archive folder select cascaded on year ✅ commit `abe4160`
  - [x] Yig'ma jild (archive folder) select — year-scoped ✅ commit `f1f4dac`
  - [x] `document_view` select + conditional view-specific fields ✅ commit `abe4160`
  - [x] universal fields (sender, document_form, language, related_document_*) ✅ commit `abe4160`
- [~] **3.5** Document edit + detail pages updated to show/edit new fields
  - [x] Edit page — shared `DocumentForm.vue` already renders/edits new fields (`abe4160`)
  - [ ] Detail page (`[documentId]/index.vue`) — render Phase 3 fields read-only

### Ad-hoc (user-requested mid-Phase-3)
- [x] **User ↔ Department link** — `users.department_id`, full vertical
  (entity→API→UI), "Xodim qo'shish" on Bo'lim cards ✅ commit `6e52bce`
  (supersedes the earlier "user model untouched" decision)
- [x] **Hujjat turi (DocumentType)** — new aggregate (entity→API→UI),
  `documents.document_type_id` FK, migration seeds 123 types from
  `backend/types.json`, "Hujjat turi" select in document form
  (supersedes the "Hujjat turlari taxonomy" out-of-scope note)

### Checkpoint — Phase 3
- [ ] All three reference-screenshot features functional
- [ ] No regression on attachments, person assignment, PDF preview
- [ ] Migrations apply cleanly on fresh AND populated DB
- [ ] Phase 3 commit landed
- [ ] **Human review before release tag**

---

## Out-of-scope (future phases, do not implement yet)

- Statistika dashboard
- Ro'yxatlar
- Kelib tushganlar (filtered view; can be derived once Phase 3 ships)
- Hujjat turlari taxonomy
- Nomenklatura workflow states (Yangi → Tasdiqlangan)
- Notifications bell, Ko'rsatmalar page
- **User ↔ Department link** (deferred — user model is untouched in this iteration)

---

# Plan v2: OCR + Elasticsearch + Postgres + Advanced Search

See [plan.md § Plan v2](plan.md) for full specs. Locked tech: Tesseract (OCR),
Elasticsearch 8.x, Postgres 16, arq + Redis (queue), outbox-lite sync pattern.

## Phase 4: Infrastructure & Postgres production-ready

- [x] **4.1** Docker Compose: postgres + redis + elasticsearch + kibana (profile) ✅ live-verified (db/redis/es all healthy)
- [x] **4.2** Postgres-aware types in models (`UUID`, `JSONB` with SQLite fallback) ✅ 33 uuid + 3 jsonb columns on PG; SQLite migrations unchanged; ORM round-trip verified
- [x] **4.3** `migrate_sqlite_to_postgres.py` data move script ✅ 375 rows across 17 tables migrated; FK integrity preserved (year/category/archive_folder/department/retention_period resolve via ORM)
- [x] **4.4** arq worker bootstrap (placeholder job only — actual jobs in 5/6) ✅ `make worker` boots; enqueue→process→result round-trip verified through Redis

### Checkpoint — Phase 4
- [x] `docker compose up -d` brings up full stack
- [x] Migrations clean on Postgres (existing + new promote migration)
- [x] Dev data migrated; app works on Postgres (ORM read of documents w/ FKs verified)
- [x] arq worker connects + runs placeholder
- [x] **No user-visible change** (foundational only)
- [ ] **Human review**

---

## Phase 5: Elasticsearch indexing (metadata only, no OCR yet)

- [x] **5.1** ES client + `documents-v1` index template + `documents` alias ✅ ICU plugin baked into custom ES image; ensure_index runs at FastAPI startup; uz_multi + uz_autocomplete analyzers verified on Latin + Cyrillic input
- [x] **5.2** Document indexer service (Postgres → ES with denormalized joins) ✅ index_document/delete_document/index_bulk verified; 2 dev docs indexed, search by title + short_desc finds them, delete tolerates 404
- [x] **5.3** `search_index_jobs` outbox table + on-save / on-delete hook ✅ save→outbox(index), update→outbox(index), delete→outbox(delete) — all three verified through SqlAlchemyDocumentRepository
- [x] **5.4** arq cron job: drain outbox → index/delete in ES ✅ drain_search_outbox runs every 2s; 10 inserts → drained in 0.26s → 10 ES docs; 10 deletes → drained → 0 ES docs
- [ ] **5.5** Reindex CLI (`python -m src.scripts.reindex`)
- [ ] **5.6** `/api/health` reports ES + Redis status

### Checkpoint — Phase 5
- [ ] Every existing document searchable via `documents` alias
- [ ] CRUD changes reflected in ES within 5s
- [ ] Reindex CLI works
- [ ] Existing search UI still uses ILIKE (cut-over in Phase 7)
- [ ] **Human review**

---

## Phase 6: OCR pipeline

- [ ] **6.1** OCR service abstraction (PyMuPDF → Tesseract fallback, lang `uzb+rus+eng`)
- [ ] **6.2** `documents.extracted_text` + `ocr_status` + same for attachments + migration
- [ ] **6.3** arq job: OCR on upload → write text → trigger reindex
- [ ] **6.4** Backfill CLI: OCR all existing documents
- [ ] **6.5** UI badge: OCR status (pending / processing / done / failed)

### Checkpoint — Phase 6
- [ ] All existing docs have `ocr_status=done` or logged `failed`
- [ ] New uploads auto-OCR within ~60s for typical 5-page PDF
- [ ] Search a body phrase → document found
- [ ] **Human review**

---

## Phase 7: Advanced search UI + API

- [ ] **7.1** `POST /api/search` — full-text query + filters + facets + highlights
- [ ] **7.2** Frontend types + `useSearch()` composable
- [ ] **7.3** `/archive/search` page — filters panel + result cards + highlights
- [ ] **7.4** Global search box in dashboard header (`/` keyboard shortcut)

### Checkpoint — Phase 7
- [ ] Advanced search works with all filter combinations
- [ ] Highlights render correctly (`<mark>` wrapped)
- [ ] Facet counts accurate
- [ ] Global header search works from every dashboard page
- [ ] **Human review before release**

---

## Locked tech (call out NOW if any of these is wrong for prod)

| Concern | Locked choice |
|---------|---------------|
| OCR | Tesseract 5 + `pytesseract` + `pdf2image` (Poppler) |
| PDF path | PyMuPDF first; Tesseract fallback when embedded text < 100 chars |
| Queue | `arq` + Redis 7 |
| Search engine | Elasticsearch 8.x, single node, `analysis-icu` plugin |
| ES analyzer | ICU tokenizer + lowercase + ICU folding + Russian stemmer (Uzbek mixes scripts) |
| Postgres types | Real `UUID` + `JSONB` on Postgres, `String(36)` + `JSON` fallback on SQLite |
| Sync pattern | Outbox-lite (`search_index_jobs` table drained by arq cron job) |
| Index strategy | Single index `documents-v1`, alias `documents`, swap-on-reindex |
