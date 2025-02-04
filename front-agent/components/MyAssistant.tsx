"use client";

import { Thread } from "@assistant-ui/react";
import { makeMarkdownText } from "@assistant-ui/react-markdown";

const MarkdownText = makeMarkdownText();

export function MyAssistant() {
  return <Thread assistantMessage={{ components: { Text: MarkdownText } }} />;
}
