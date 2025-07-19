export function countTokens(text: string): number {
  // Rough token estimation: 1 token per 4 characters
  return Math.ceil(text.length / 4);
}
