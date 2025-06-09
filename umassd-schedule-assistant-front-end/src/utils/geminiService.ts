// utils/geminiService.ts

export const askGemini = async (
  question: string,
  summarizedTimetableContent: string | null
): Promise<string> => {
  try {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        summarizedTimetableContent: summarizedTimetableContent || "",
      }),
    });

    const data = await response.json();
    return data.answer;
  } catch (error) {
    console.error("Error calling /ask:", error);
    return "Sorry, I encountered an error while processing your question.";
  }
};

export const summaryPrompt = async (timetableContent: string): Promise<string> => {
  try {
    const response = await fetch("http://127.0.0.1:8000/summarize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        timetableContent,
      }),
    });

    const data = await response.json();
    return data.summary;
  } catch (error) {
    console.error("Error calling /summarize:", error);
    return "Sorry, I encountered an error while summarizing the timetable.";
  }
};
