/**
 * Conversations API
 * GET /api/conversations - Get all conversations
 * POST /api/conversations - Create a new conversation
 */

import { conversationStore } from "@/lib/conversationStore";

export async function GET() {
  try {
    const conversations = conversationStore.getAllConversations();
    return new Response(
      JSON.stringify(conversations.map(c => ({
        id: c.id,
        title: c.title,
        updatedAt: c.updatedAt,
      }))),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error fetching conversations:", error);
    return new Response(
      JSON.stringify({ error: "Failed to fetch conversations" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST() {
  try {
    const conversation = conversationStore.createConversation();
    return new Response(
      JSON.stringify({
        id: conversation.id,
        title: conversation.title,
        updatedAt: conversation.updatedAt,
      }),
      { status: 201, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error creating conversation:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create conversation" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
