export function copyTextToBoard(text) {
  if (!navigator.clipboard) {
    throw new Error('Clipboard API not supported');
  }

  return navigator.clipboard.writeText(text);
}
