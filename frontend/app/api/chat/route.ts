import { openai } from "@ai-sdk/openai";
import { generateText, tool } from "ai";
import { z } from "zod";
import { taskStore } from "@/lib/taskStore";

// Check for OpenAI API key
if (!process.env.OPENAI_API_KEY) {
  console.error("OPENAI_API_KEY is not set in environment variables");
}

// Rate limiting configuration
const RATE_LIMIT_WINDOW_MS = 60 * 60 * 1000; // 1 hour
const MAX_REQUESTS_PER_WINDOW = 50;

// In-memory rate limit store (in production, use Redis)
declare global {
  var __rateLimitStore: Map<string, { count: number; resetTime: number }> | undefined;
}

if (!global.__rateLimitStore) {
  global.__rateLimitStore = new Map();
}

function checkRateLimit(userId: string = "demo-user"): { allowed: boolean; remaining: number; resetIn: number } {
  const store = global.__rateLimitStore!;
  const now = Date.now();
  const userLimit = store.get(userId);

  if (!userLimit || now > userLimit.resetTime) {
    // Reset or create new window
    store.set(userId, { count: 1, resetTime: now + RATE_LIMIT_WINDOW_MS });
    return { allowed: true, remaining: MAX_REQUESTS_PER_WINDOW - 1, resetIn: RATE_LIMIT_WINDOW_MS };
  }

  if (userLimit.count >= MAX_REQUESTS_PER_WINDOW) {
    return { allowed: false, remaining: 0, resetIn: userLimit.resetTime - now };
  }

  userLimit.count++;
  return { allowed: true, remaining: MAX_REQUESTS_PER_WINDOW - userLimit.count, resetIn: userLimit.resetTime - now };
}

// Define tools with proper Zod schemas for AI SDK v5
// AI SDK v5 uses 'inputSchema' instead of 'parameters'
const addTaskTool = tool({
  description: "Add a new task with a title and optional description",
  inputSchema: z.object({
    title: z.string().describe("The title of the task"),
    description: z.string().optional().describe("Optional description of the task"),
  }),
  execute: async ({ title, description }) => {
    const newTask = taskStore.addTask(title, description);
    return { success: true, task: newTask, message: `Task "${title}" created with ID ${newTask.id}` };
  },
});

const listTasksTool = tool({
  description: "List all tasks, optionally filtered by status",
  inputSchema: z.object({
    status: z.enum(["all", "pending", "completed"]).optional().default("all").describe("Filter by status"),
  }),
  execute: async ({ status }) => {
    const filteredTasks = taskStore.getTasksByStatus(status || "all");
    return {
      success: true,
      tasks: filteredTasks.map(t => ({
        id: t.id,
        title: t.title,
        description: t.description,
        completed: t.is_completed,
      })),
      count: filteredTasks.length,
      message: filteredTasks.length > 0 ? `Found ${filteredTasks.length} task(s)` : "No tasks found",
    };
  },
});

const completeTaskTool = tool({
  description: "Mark a task as complete by its ID",
  inputSchema: z.object({
    task_id: z.number().describe("The ID of the task to complete"),
  }),
  execute: async ({ task_id }) => {
    const existingTask = taskStore.getTaskById(task_id);
    if (!existingTask) {
      return { success: false, error: `Task with ID ${task_id} not found` };
    }
    if (existingTask.is_completed) {
      return { success: true, message: `Task "${existingTask.title}" is already completed` };
    }
    const task = taskStore.completeTask(task_id);
    return { success: true, message: `Task "${task?.title}" marked as complete` };
  },
});

const uncompleteTaskTool = tool({
  description: "Mark a completed task as incomplete/pending by its ID. Use this when user wants to undo completion or reopen a task.",
  inputSchema: z.object({
    task_id: z.number().describe("The ID of the task to mark as incomplete"),
  }),
  execute: async ({ task_id }) => {
    const existingTask = taskStore.getTaskById(task_id);
    if (!existingTask) {
      return { success: false, error: `Task with ID ${task_id} not found` };
    }
    if (!existingTask.is_completed) {
      return { success: true, message: `Task "${existingTask.title}" is already pending/incomplete` };
    }
    const task = taskStore.updateTask(task_id, { is_completed: false });
    return { success: true, message: `Task "${task?.title}" marked as incomplete/pending` };
  },
});

const deleteTaskTool = tool({
  description: "Delete a task by its ID",
  inputSchema: z.object({
    task_id: z.number().describe("The ID of the task to delete"),
  }),
  execute: async ({ task_id }) => {
    const existingTask = taskStore.getTaskById(task_id);
    if (!existingTask) {
      return { success: false, error: `Task with ID ${task_id} not found` };
    }
    const title = existingTask.title;
    const deleted = taskStore.deleteTask(task_id);
    if (deleted) {
      return { success: true, message: `Task "${title}" deleted successfully` };
    }
    return { success: false, error: "Failed to delete task" };
  },
});

const updateTaskTool = tool({
  description: "Update a task's title and/or description",
  inputSchema: z.object({
    task_id: z.number().describe("The ID of the task to update"),
    title: z.string().optional().describe("New title for the task"),
    description: z.string().optional().describe("New description for the task"),
  }),
  execute: async ({ task_id, title, description }) => {
    const existingTask = taskStore.getTaskById(task_id);
    if (!existingTask) {
      return { success: false, error: `Task with ID ${task_id} not found` };
    }
    const updates: { title?: string; description?: string } = {};
    if (title) updates.title = title;
    if (description !== undefined) updates.description = description;
    const task = taskStore.updateTask(task_id, updates);
    return { success: true, task, message: `Task "${task?.title}" updated successfully` };
  },
});

export async function POST(req: Request) {
  try {
    // Check rate limit
    const rateLimit = checkRateLimit();
    if (!rateLimit.allowed) {
      const resetMinutes = Math.ceil(rateLimit.resetIn / 60000);
      return new Response(
        JSON.stringify({
          error: `Rate limit exceeded. You can send ${MAX_REQUESTS_PER_WINDOW} messages per hour. Try again in ${resetMinutes} minutes.`
        }),
        {
          status: 429,
          headers: {
            "Content-Type": "application/json",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": String(Math.ceil(rateLimit.resetIn / 1000)),
          }
        }
      );
    }

    // Check for API key
    if (!process.env.OPENAI_API_KEY) {
      return new Response(
        JSON.stringify({ error: "OPENAI_API_KEY is not configured. Please add it to frontend/.env.local" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const { messages } = await req.json();

    const toolsConfig = {
      add_task: addTaskTool,
      list_tasks: listTasksTool,
      complete_task: completeTaskTool,
      uncomplete_task: uncompleteTaskTool,
      delete_task: deleteTaskTool,
      update_task: updateTaskTool,
    };

    const systemPrompt = `You are a helpful AI assistant for managing tasks. You help users create, view, update, complete, and delete tasks using natural language.

Available tools:
1. add_task - Create a new task with a title and optional description
2. list_tasks - Show all tasks (can filter by status: all, pending, completed)
3. complete_task - Mark a task as done by its ID
4. uncomplete_task - Mark a completed task as incomplete/pending (undo completion)
5. delete_task - Remove a task by its ID
6. update_task - Change a task's title or description

Guidelines:
- When adding tasks, extract the title from what the user says
- When the user asks to see tasks, use list_tasks
- When completing or deleting, ask for the task ID if not provided
- When user says "unmark", "undo", "reopen", or "mark as incomplete", use uncomplete_task
- IMPORTANT: After using any tool, you MUST provide a text response to the user explaining what happened
- Always confirm actions after completing them with a friendly message
- Be helpful and friendly!`;

    const result = await generateText({
      model: openai("gpt-4o-mini"),
      system: systemPrompt,
      messages,
      tools: toolsConfig,
    });

    console.log("AI Result:", JSON.stringify({
      text: result.text,
      toolCalls: result.toolCalls,
      toolResults: result.toolResults,
    }, null, 2));

    // If there's a text response, return it
    if (result.text && result.text.trim()) {
      return new Response(result.text, {
        headers: { "Content-Type": "text/plain" },
      });
    }

    // If tools were called but no text, make a follow-up call to generate a response
    if (result.toolResults && result.toolResults.length > 0) {
      // Build context from tool results for follow-up
      const toolResultsSummary = result.toolResults.map((tr: any) => {
        const toolResult = tr?.result ?? tr?.output ?? tr;
        return `Tool "${tr?.toolName || 'unknown'}": ${JSON.stringify(toolResult)}`;
      }).join("\n");

      console.log("Tool results summary:", toolResultsSummary);

      // Make a follow-up call to generate a natural response
      const followUp = await generateText({
        model: openai("gpt-4o-mini"),
        system: "You are a helpful task management assistant. Based on the tool execution results, provide a friendly, concise response to the user. Do not use markdown formatting.",
        messages: [
          { role: "user", content: messages[messages.length - 1]?.content || "What happened?" },
          { role: "assistant", content: `I executed the following actions:\n${toolResultsSummary}` },
          { role: "user", content: "Please summarize what happened in a friendly way." }
        ],
      });

      if (followUp.text && followUp.text.trim()) {
        return new Response(followUp.text, {
          headers: { "Content-Type": "text/plain" },
        });
      }

      // If follow-up also fails, return the raw tool results
      return new Response(toolResultsSummary, {
        headers: { "Content-Type": "text/plain" },
      });
    }

    // Fallback response
    return new Response("I'm here to help you manage your tasks! You can ask me to add, view, complete, update, or delete tasks.", {
      headers: { "Content-Type": "text/plain" },
    });
  } catch (error: unknown) {
    console.error("Chat API Error:", error);
    const errorMessage = error instanceof Error ? error.message : "Internal server error";
    return new Response(
      JSON.stringify({ error: errorMessage }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
