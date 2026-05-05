// Prevents an additional console window on Windows in release builds
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

use commands::BackendProcess;
use std::process::Child;
use std::sync::Mutex;
use std::time::Duration;

fn start_python_backend() -> Option<Child> {
    let child = std::process::Command::new("uv")
        .args([
            "run",
            "uvicorn",
            "apps.web.backend.server:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ])
        .spawn()
        .ok()?;

    for _ in 0..30 {
        if std::net::TcpStream::connect("127.0.0.1:8000").is_ok() {
            return Some(child);
        }
        std::thread::sleep(Duration::from_millis(500));
    }

    eprintln!("Warning: Backend did not become ready within 15 seconds");
    Some(child)
}

fn main() {
    use tauri::Manager;

    let backend = start_python_backend();
    let backend_state = BackendProcess(Mutex::new(backend));

    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .manage(backend_state)
        .invoke_handler(tauri::generate_handler![
            commands::choose_directory,
            commands::reveal_in_finder,
            commands::copy_to_clipboard,
            commands::get_recent_workspaces,
            commands::save_recent_workspace,
            commands::forget_workspace,
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                let mut child_to_kill = None;
                {
                    let state: tauri::State<BackendProcess> = window.state();
                    if let Ok(mut guard) = state.0.lock() {
                        child_to_kill = guard.take();
                    };
                }
                if let Some(mut child) = child_to_kill {
                    let _ = child.kill();
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
