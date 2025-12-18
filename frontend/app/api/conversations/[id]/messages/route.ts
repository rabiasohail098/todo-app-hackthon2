/**
 * Conversation Messages API
 * GET /api/conversations/[id]/messages - Get messages for a conversation
 * POST /api/conversations/[id]/messages - Add a message to a conversation
 */

import { conversationStore } from "@/lib/conversationStore";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const conversation = conversationStore.getConversation(id);

    if (!conversation) {
      return new Response(
        JSON.stringify({ error: "Conversation not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(
      JSON.stringify(conversation.messages.map(m => ({
        id: m.id,
        role: m.role,
        content: m.content,
      }))),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching messages:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch messages" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { role, content } = await req.json();

    if (!role || !content) {
      return new Response(
        JSON.stringify({ error: "Role and content are required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const message = conversationStore.addMessage(id, { role, content });

    if (!message) {
      return new Response(
        JSON.stringify({ error: "Conversation not found" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    return new Response(
      JSON.stringify({
        id: message.id,
        role: message.role,
        content: message.content,
      }),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error adding message:", error);
    return new Response(
      JSON.stringify({ error: "Failed to add message" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
