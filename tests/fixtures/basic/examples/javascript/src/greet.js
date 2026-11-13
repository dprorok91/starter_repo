/** Return a greeting, rejecting an empty name. */
export function greet(name) {
  if (!name.trim()) throw new Error('A name is required');
  return `Hello, ${name.trim()}!`;
}
