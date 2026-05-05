use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::process::Child;
use std::sync::Mutex;

// ---- Backend process state ----

pub struct BackendProcess(pub Mutex<Option<Child>>);

// ---- Workspace storage ----

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkspaceEntry {
    pub id: String,
    pub name: String,
    pub path: String,
    pub kind: String,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

fn workspaces_path() -> PathBuf {
    let base = dirs::data_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("photograph-workflow-desktop");
    base.join("recent-workspaces.json")
}

fn read_workspaces() -> Vec<WorkspaceEntry> {
    let path = workspaces_path();
    if !path.exists() {
        return vec![];
    }
    fs::read_to_string(&path)
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

fn write_workspaces(entries: &[WorkspaceEntry]) -> std::io::Result<()> {
    let path = workspaces_path();
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(entries)?;
    fs::write(path, json)
}

// ---- Tauri Commands ----

#[tauri::command]
pub fn choose_directory() -> Result<Option<String>, String> {
    let path = rfd::FileDialog::new().pick_folder();
    Ok(path.map(|p| p.to_string_lossy().to_string()))
}

#[tauri::command]
pub fn reveal_in_finder(path: String) -> Result<(), String> {
    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .args(["-R", &path])
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
pub fn copy_to_clipboard(_text: String) -> Result<(), String> {
    Ok(())
}

#[tauri::command]
pub fn get_recent_workspaces() -> Result<Vec<WorkspaceEntry>, String> {
    Ok(read_workspaces())
}

#[tauri::command]
pub fn save_recent_workspace(
    path: String,
    name: Option<String>,
) -> Result<WorkspaceEntry, String> {
    let mut entries = read_workspaces();

    entries.retain(|e| e.path != path);

    let now = chrono::Utc::now().to_rfc3339();
    let entry = WorkspaceEntry {
        id: uuid::Uuid::new_v4().to_string(),
        name: name.unwrap_or_else(|| {
            std::path::Path::new(&path)
                .file_name()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or_else(|| "Untitled".to_string())
        }),
        path,
        kind: "custom".to_string(),
        created_at: Some(now.clone()),
        updated_at: Some(now),
    };
    entries.insert(0, entry.clone());

    entries.truncate(20);

    write_workspaces(&entries).map_err(|e| e.to_string())?;
    Ok(entry)
}

#[tauri::command]
pub fn forget_workspace(id: String) -> Result<(), String> {
    let mut entries = read_workspaces();
    entries.retain(|e| e.id != id);
    write_workspaces(&entries).map_err(|e| e.to_string())
}
