document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const textarea = document.getElementById("profile");
  const typingIndicator = document.getElementById("typing-indicator");
  const chatBox = document.getElementById("chat-box");

  const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  form.addEventListener("submit", () => {
    typingIndicator.style.display = "block";
    scrollToBottom();
  });

  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  scrollToBottom();
});
