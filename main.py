from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

# Модель задачи
class Task(BaseModel):
    id: int
    description: str
    done: bool = False
    category: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

# создания и обновления задачи
class TaskCreateUpdate(BaseModel):
    description: str = Field(..., min_length=3, max_length=100)
    done: bool = False
    category: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

# Внутреннее хранилище задач
tasks = []
task_id_counter = 1

#  отображения главной страницы с HTML-шаблоном
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# создания задачи
@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreateUpdate):
    global task_id_counter
    new_task = Task(id=task_id_counter, **task.dict())
    tasks.append(new_task)
    task_id_counter += 1
    return new_task

# получения всех задач
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

#  обновления задачи
@app.put("/tasks/{id}", response_model=Task)
async def update_task(id: int, task_update: TaskCreateUpdate):
    for task in tasks:
        if task.id == id:
            task.description = task_update.description or task.description
            task.done = task_update.done
            task.category = task_update.category or task.category
            task.priority = task_update.priority or task.priority
            return task
    raise HTTPException(status_code=404, detail="Task not found")

#  удаления задачи
@app.delete("/tasks/{id}")
async def delete_task(id: int):
    for task in tasks:
        if task.id == id:
            tasks.remove(task)
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")
