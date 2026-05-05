export interface WorkspaceEntry {
  id: string
  name: string
  path: string
  kind: string
  created_at: string | null
  updated_at: string | null
}

/**
 * Detect whether the app is running inside a Tauri WebView.
 * Tauri v2 injects window.__TAURI_INTERNALS__ at runtime.
 */
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

/**
 * Platform-native bridge.
 * - In Tauri: delegates to Rust commands via @tauri-apps/api
 * - In Browser: returns null / no-ops / uses browser fallbacks
 *
 * Uses dynamic import() for @tauri-apps/api so the web-only build
 * never tries to bundle it.
 */
export const native = {
  /** Open system directory picker. Returns absolute path or null. */
  async chooseDirectory(): Promise<string | null> {
    if (!isTauri()) return null
    const { invoke } = await import('@tauri-apps/api/core')
    return invoke<string | null>('choose_directory')
  },

  /** Open Finder at the given directory or file path. macOS only. */
  async revealInFinder(path: string): Promise<void> {
    if (!isTauri()) return
    const { invoke } = await import('@tauri-apps/api/core')
    await invoke('reveal_in_finder', { path })
  },

  /** Copy text to system clipboard. Falls back to navigator.clipboard in browser. */
  async copyToClipboard(text: string): Promise<void> {
    if (!isTauri()) {
      await navigator.clipboard.writeText(text)
      return
    }
    const { invoke } = await import('@tauri-apps/api/core')
    await invoke('copy_to_clipboard', { text })
  },

  /** Get recent workspaces from Tauri app data storage. */
  async getRecentWorkspaces(): Promise<WorkspaceEntry[]> {
    if (!isTauri()) return []
    const { invoke } = await import('@tauri-apps/api/core')
    return invoke<WorkspaceEntry[]>('get_recent_workspaces')
  },

  /** Save a workspace to Tauri app data storage. */
  async saveRecentWorkspace(path: string, name?: string): Promise<void> {
    if (!isTauri()) return
    const { invoke } = await import('@tauri-apps/api/core')
    await invoke('save_recent_workspace', { path, name })
  },

  /** Remove a workspace from Tauri app data storage. */
  async forgetWorkspace(id: string): Promise<void> {
    if (!isTauri()) return
    const { invoke } = await import('@tauri-apps/api/core')
    await invoke('forget_workspace', { id })
  },
}
