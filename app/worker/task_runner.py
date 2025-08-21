from app.config.settings import settings


def run_task(task_func, *args, **kwargs):
    if settings.ENVIRONMENT == "production":
        task_func.delay(*args, **kwargs)
    else:
        print(f"[TASK-DEV] Executando tarefa local: {task_func.__name__}({args}, {kwargs})")
        task_func(*args, **kwargs)