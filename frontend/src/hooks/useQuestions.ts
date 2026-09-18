import { useState } from "react";
import { askQuestion } from "../services/api";
import type { QuestionResponse } from "../types";

export function useQuestions(organisationId: number | null) {
  const [answer, setAnswer] = useState<QuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(question: string) {
    if (!organisationId) {
      throw new Error("No organisation selected.");
    }

    try {
      setLoading(true);
      setError(null);

      const result = await askQuestion(organisationId, question);

      setAnswer(result);

      return result;
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to get an answer."
      );

      throw err;
    } finally {
      setLoading(false);
    }
  }

  return {
    answer,

    // Compatibility with existing AskIntelligence page
    response: answer,

    loading,
    error,
    ask,
  };
}