export type CompanyQuestionBank = Record<string, string[]>;

export const staticQuestionBank: CompanyQuestionBank = {
  Google: [
    "Design a URL Shortener system architecture.",
    "Explain the CAP theorem and its trade-offs.",
    "Invert a binary tree.",
    "Find the longest substring without repeating characters.",
    "Explain how a hash table works.",
  ],

  Meta: [
    "Design an Instagram feed backend.",
    "Explain React reconciliation and the virtual DOM.",
    "Merge overlapping intervals.",
    "Find the lowest common ancestor in a binary tree.",
    "Explain how you would scale a social networking application.",
  ],

  Amazon: [
    "Design a scalable e-commerce checkout system.",
    "Describe a time you dealt with ambiguity in a project.",
    "Solve the Two Sum problem efficiently.",
    "Explain the difference between a stack and a queue.",
    "Design a system to track package deliveries.",
  ],
};
