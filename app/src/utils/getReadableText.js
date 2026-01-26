import { unref } from "vue";

export function getReadableText(container) {
  const el = unref(container);
  if (!el) return "";

  const walker = document.createTreeWalker(
    el,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        if (!node.nodeValue?.trim()) return NodeFilter.FILTER_REJECT;

        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;

        // Skip fenced & inline code
        if (parent.closest("pre, code")) {
          return NodeFilter.FILTER_REJECT;
        }

        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  let text = "";
  while (walker.nextNode()) {
    text += walker.currentNode.nodeValue + " ";
  }

  return text.trim();
}
