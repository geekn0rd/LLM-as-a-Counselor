"use client";

import type { ReactNode } from "react";
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
} from "@assistant-ui/react";

const MyModelAdapter: ChatModelAdapter = {
  async *run({ messages, abortSignal }) {
    console.log("Starting fetch request");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages }),
        signal: abortSignal,
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("Failed to read response stream");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log("Stream complete");
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Split on double newlines (SSE message boundary)
        const parts = buffer.split("\n\n");

        // Keep the last part if it's incomplete
        buffer = parts.pop() || "";

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const chunk = part.slice(6); // Remove 'data: ' prefix
            console.log("Received chunk:", chunk);

            accumulatedText += chunk;

            yield {
              content: [{ type: "text", text: accumulatedText }],
            };
          }
        }
      }
    } catch (error) {
      console.error("Error:", error);
      throw error;
    }
  },
};

export function MyRuntimeProvider({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  const runtime = useLocalRuntime(MyModelAdapter);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
