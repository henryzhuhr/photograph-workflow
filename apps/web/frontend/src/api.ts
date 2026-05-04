export interface PlanIssue {
  code: string
  message: string
  path: string | null
  details: Record<string, unknown> | null
}

export interface ScanItem {
  path: string
  role: 'raw' | 'sidecar' | 'other'
  extension: string
}

export interface CommonPlan {
  operation: string
  root: string
  dry_run: boolean
  items: unknown[]
  warnings: PlanIssue[]
  errors: PlanIssue[]
  metadata_changes: unknown[]
  requires_confirmation: boolean
}

export interface RenamePlanItem {
  source_path: string
  target_path: string
  role: 'raw' | 'sidecar'
  raw_source_path: string | null
  original_name: string
  current_name: string
  planned_name: string | null
  status: string
}

export interface RenamePlan extends CommonPlan {
  operation: 'rename'
  items: RenamePlanItem[]
}

export interface RollbackPlanItem {
  current_path: string
  target_original_path: string
  role: 'raw' | 'sidecar'
  status: string
}

export interface RollbackPlan extends CommonPlan {
  operation: 'rollback'
  items: RollbackPlanItem[]
}

export interface ArchivePlanItem {
  source_path: string
  archive_path: string
  size_bytes: number | null
  included: boolean
  exclude_reason: string | null
}

export interface ArchivePlan extends CommonPlan {
  operation: 'archive'
  source_dir: string
  archive_path: string
  archived_at: string
  overwrite: boolean
  total_size_bytes: number
  included_count: number
  excluded_count: number
  raw_count: number
  sidecar_count: number
  items: ArchivePlanItem[]
}

export interface ArchiveNamePlan extends CommonPlan {
  operation: 'archive_name'
  source_dir: string
  archive_name: string
  archive_path: string | null
  archived_at: string
}

export interface WorkspaceEntry {
  id: string
  name: string
  path: string
  kind: string
  created_at: string | null
  updated_at: string | null
}

export interface WorkspaceFile {
  version: number
  workspaces: WorkspaceEntry[]
  default_workspace_id: string | null
  created_at: string | null
  updated_at: string | null
}

const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  // Workspaces
  listWorkspaces: () => request<WorkspaceFile>('/workspaces'),

  addWorkspace: (path: string, name?: string, kind?: string) =>
    request<CommonPlan>('/workspaces', {
      method: 'POST',
      body: JSON.stringify({ path, name, kind }),
    }),

  removeWorkspace: (id: string) =>
    request<CommonPlan>(`/workspaces/${id}`, { method: 'DELETE' }),

  setDefaultWorkspace: (id: string) =>
    request<CommonPlan>(`/workspaces/${id}/default`, { method: 'PUT' }),

  // Scan
  scan: (root: string) =>
    request<CommonPlan>('/scan', {
      method: 'POST',
      body: JSON.stringify({ root }),
    }),

  // Rename
  renamePlan: (root: string, template?: string, strict?: boolean) =>
    request<RenamePlan>('/rename/plan', {
      method: 'POST',
      body: JSON.stringify({ root, template, strict }),
    }),

  renameExecute: (root: string, template?: string, strict?: boolean) =>
    request<RenamePlan>('/rename/execute', {
      method: 'POST',
      body: JSON.stringify({ root, template, strict }),
    }),

  // Rollback
  rollbackPlan: (photoDir: string) =>
    request<RollbackPlan>('/rollback/plan', {
      method: 'POST',
      body: JSON.stringify({ photo_dir: photoDir }),
    }),

  rollbackExecute: (photoDir: string) =>
    request<RollbackPlan>('/rollback/execute', {
      method: 'POST',
      body: JSON.stringify({ photo_dir: photoDir }),
    }),

  // Archive
  archivePlan: (sourceDir: string, outputDir: string, overwrite?: boolean) =>
    request<ArchivePlan>('/archive/plan', {
      method: 'POST',
      body: JSON.stringify({ source_dir: sourceDir, output_dir: outputDir, overwrite }),
    }),

  archiveExecute: (sourceDir: string, outputDir: string, overwrite?: boolean) =>
    request<ArchivePlan>('/archive/execute', {
      method: 'POST',
      body: JSON.stringify({ source_dir: sourceDir, output_dir: outputDir, overwrite }),
    }),

  archiveName: (sourceDir: string, outputDir?: string) =>
    request<ArchiveNamePlan>('/archive-name', {
      method: 'POST',
      body: JSON.stringify({ source_dir: sourceDir, output_dir: outputDir }),
    }),
}
