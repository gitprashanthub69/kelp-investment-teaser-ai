from app.tasks import process_project_task
import sys

if __name__ == "__main__":
    project_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"Manually triggering process_project_task for Project {project_id}")
    # Run synchronously for direct output if possible, or use delay()
    process_project_task(project_id)
    print("Trigger script finished.")
