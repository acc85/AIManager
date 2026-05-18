import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TaskQueueHandler(FileSystemEventHandler):
    def __init__(self, workspace_dir, on_new_task_callback):
        self.workspace_dir = workspace_dir
        self.on_new_task_callback = on_new_task_callback
        self.task_path = os.path.join(workspace_dir, "task.md")
        self.last_content = ""
        
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)
            
        if not os.path.exists(self.task_path):
            self._write_template()
        else:
            with open(self.task_path, "r", encoding="utf-8") as f:
                self.last_content = f.read().strip()

    def _write_template(self):
        with open(self.task_path, "w", encoding="utf-8") as f:
            f.write("# Tasks\n\n")

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(self.task_path):
            self._process_task_queue()

    def _process_task_queue(self):
        try:
            time.sleep(0.5)
            with open(self.task_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if content.strip() == self.last_content:
                return
                
            lines = content.split('\n')
            task_to_process = None
            
            for i, line in enumerate(lines):
                if line.strip().startswith("- [ ] "):
                    task_to_process = line.strip()[6:]
                    lines[i] = line.replace("- [ ] ", "- [>] ", 1)
                    break
                    
            if task_to_process:
                new_content = '\n'.join(lines)
                with open(self.task_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.last_content = new_content.strip()
                self.on_new_task_callback(task_to_process)
            else:
                self.last_content = content.strip()
                
        except Exception as e:
            print(f"Error reading task file: {e}")

class Orchestrator:
    def __init__(self, workspace_dir, on_new_task_callback):
        self.workspace_dir = workspace_dir
        self.handler = TaskQueueHandler(workspace_dir, on_new_task_callback)
        self.observer = Observer()
        self.observer.schedule(self.handler, path=self.workspace_dir, recursive=False)
        
    def start(self):
        self.observer.start()
        
    def stop(self):
        self.observer.stop()
        self.observer.join()

    def write_active_task(self, response_text):
        active_task_path = os.path.join(self.workspace_dir, "active_task.md")
        with open(active_task_path, "w", encoding="utf-8") as f:
            f.write(response_text)

    def mark_task_completed(self):
        try:
            with open(self.handler.task_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith("- [>] "):
                    lines[i] = line.replace("- [>] ", "- [x] ", 1)
                    updated = True
                    break
                    
            if updated:
                new_content = '\n'.join(lines)
                with open(self.handler.task_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.handler.last_content = new_content.strip()
        except Exception as e:
            print(f"Error marking task complete: {e}")
