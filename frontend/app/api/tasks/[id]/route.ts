/**
 * Individual task API endpoints.
 * GET /api/tasks/[id] - Get a task
 * PATCH /api/tasks/[id] - Update a task
 * DELETE /api/tasks/[id] - Delete a task
 */

import { taskStore } from "@/lib/taskStore";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const taskId = parseInt(id, 10);

    if (isNaN(taskId)) {
      return new Response(
        JSON.stringify({ error: "Invalid task ID" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const task = taskStore.getTaskById(taskId);

    if (!task) {
      return new Response(
        JSON.stringify({ error: "Task not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(JSON.stringify(task), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error fetching task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function PATCH(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const taskId = parseInt(id, 10);

    if (isNaN(taskId)) {
      return new Response(
        JSON.stringify({ error: "Invalid task ID" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const updates = await req.json();
    const task = taskStore.updateTask(taskId, updates);

    if (!task) {
      return new Response(
        JSON.stringify({ error: "Task not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(JSON.stringify(task), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error updating task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to update task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const taskId = parseInt(id, 10);

    if (isNaN(taskId)) {
      return new Response(
        JSON.stringify({ error: "Invalid task ID" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const deleted = taskStore.deleteTask(taskId);

    if (!deleted) {
      return new Response(
        JSON.stringify({ error: "Task not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(null, { status: 204 });
  } catch (error) {
    console.error("Error deleting task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to delete task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
