const ALLOWED_PUNCT = new Set(".,?!:;'\"()-");

export const INVALID_TEXT_MSG =
  "Text contains invalid characters. Use letters, numbers, and basic punctuation only.";

export function textHasInvalidChars(text: string): boolean {
  for (const ch of text) {
    if (/\s/u.test(ch) || ALLOWED_PUNCT.has(ch) || /\d/u.test(ch)) continue;
    if (/\p{L}/u.test(ch)) continue;
    return true;
  }
  return false;
}
