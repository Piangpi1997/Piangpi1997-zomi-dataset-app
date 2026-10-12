-- PostgreSQL 15+. Apply in the private Dataset Studio backend database.
-- No client may directly INSERT/UPDATE these tables.
CREATE TABLE IF NOT EXISTS dataset_publication_requests (
  id uuid PRIMARY KEY,
  owner_id text NOT NULL,
  dataset_id text NOT NULL,
  snapshot_sha256 char(64) NOT NULL,
  snapshot_json jsonb NOT NULL,
  stage text NOT NULL CHECK (stage IN ('imported','cleaned','translated','verified','training-manifest','evaluation')),
  status text NOT NULL DEFAULT 'pending_review'
    CHECK (status IN ('pending_review','approved','publishing','published','failed','rejected')),
  created_at timestamptz NOT NULL DEFAULT now(),
  approved_at timestamptz,
  approved_by text,
  approval_reason text,
  github_path text,
  github_commit_sha text,
  last_error text,
  attempts integer NOT NULL DEFAULT 0,
  CHECK ((status NOT IN ('approved','publishing','published','failed')) OR approved_by IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS publication_work_idx
 ON dataset_publication_requests (status, created_at);
CREATE INDEX IF NOT EXISTS publication_owner_idx
 ON dataset_publication_requests (owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS dataset_publication_audit (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  request_id uuid NOT NULL REFERENCES dataset_publication_requests(id),
  actor_id text NOT NULL,
  action text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
-- Append-only audit; immutable snapshots cannot be updated.
CREATE OR REPLACE FUNCTION prevent_publication_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.snapshot_json IS DISTINCT FROM OLD.snapshot_json
    OR NEW.snapshot_sha256 IS DISTINCT FROM OLD.snapshot_sha256
    OR NEW.dataset_id IS DISTINCT FROM OLD.dataset_id
    OR NEW.owner_id IS DISTINCT FROM OLD.owner_id
    OR NEW.stage IS DISTINCT FROM OLD.stage
 THEN RAISE EXCEPTION 'publication snapshot is immutable';
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS immutable_publication_snapshot ON dataset_publication_requests;
CREATE TRIGGER immutable_publication_snapshot BEFORE UPDATE ON dataset_publication_requests
 FOR EACH ROW EXECUTE FUNCTION prevent_publication_mutation();
CREATE OR REPLACE FUNCTION prevent_publication_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'audit is append-only'; END $$;
DROP TRIGGER IF EXISTS append_only_publication_audit ON dataset_publication_audit;
CREATE TRIGGER append_only_publication_audit BEFORE UPDATE OR DELETE ON dataset_publication_audit
 FOR EACH ROW EXECUTE FUNCTION prevent_publication_audit_mutation();
