/**
 * Task API endpoints using shared store.
 * GET /api/tasks - Get all tasks
 * POST /api/tasks - Create a new task
 */

import { taskStore } from "@/lib/taskStore";

export async function GET() {
  try {
    const tasks = taskStore.getTasks();
    return new Response(JSON.stringify(tasks), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error fetching tasks:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch tasks" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST(req: Request) {
  try {
    const { title, description } = await req.json();

    if (!title || !title.trim()) {
      return new Response(
        JSON.stringify({ error: "Title is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const task = taskStore.addTask(title.trim(), description?.trim());

    return new Response(JSON.stringify(task), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error creating task:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create task" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
