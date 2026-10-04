import json
from typing import Dict, Any, List, Tuple
from playwright.async_api import Page
from app.schemas.agent import InteractiveElement, DOMObservation

# JavaScript snippet injected into the browser to label interactive elements and build an index
DOM_GROUNDING_JS = """
(() => {
    // Clean up previous markers if any
    document.querySelectorAll('.autoqa-marker-badge').forEach(el => el.remove());

    const isVisible = (elem) => {
        if (!elem) return false;
        const style = window.getComputedStyle(elem);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = elem.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight && rect.bottom > 0;
    };

    const isInteractive = (elem) => {
        const tag = elem.tagName.toLowerCase();
        const role = elem.getAttribute('role');
        const isClickableRole = ['button', 'link', 'checkbox', 'radio', 'tab', 'menuitem', 'combobox', 'option'].includes(role);
        
        return (
            ['button', 'input', 'select', 'textarea', 'a'].includes(tag) ||
            isClickableRole ||
            elem.onclick != null ||
            elem.getAttribute('contenteditable') === 'true' ||
            window.getComputedStyle(elem).cursor === 'pointer'
        );
    };

    const getOptimalSelector = (el) => {
        if (el.id) return `#${CSS.escape(el.id)}`;
        if (el.getAttribute('data-testid')) return `[data-testid="${CSS.escape(el.getAttribute('data-testid'))}"]`;
        if (el.getAttribute('name')) return `[name="${CSS.escape(el.getAttribute('name'))}"]`;
        if (el.getAttribute('aria-label')) return `[aria-label="${CSS.escape(el.getAttribute('aria-label'))}"]`;
        
        // Tag + Text for buttons and links
        const tag = el.tagName.toLowerCase();
        const text = (el.innerText || '').trim();
        if (['button', 'a'].includes(tag) && text && text.length < 40) {
            return `${tag}:has-text("${text.replace(/"/g, '\\"')}")`;
        }

        // Relative path fallback
        let path = tag;
        if (el.className && typeof el.className === 'string') {
            const classes = el.className.trim().split(/\\s+/).slice(0, 2).filter(c => !c.includes(':')).join('.');
            if (classes) path += `.${classes}`;
        }
        return path;
    };

    const elements = [];
    const allNodes = document.querySelectorAll('*');
    let currentId = 1;

    allNodes.forEach((node) => {
        if (isInteractive(node) && isVisible(node)) {
            node.setAttribute('data-autoqa-id', currentId);
            const rect = node.getBoundingClientRect();

            // Create visual badge for Vision LLM
            const badge = document.createElement('div');
            badge.className = 'autoqa-marker-badge';
            badge.innerText = currentId;
            badge.style.position = 'fixed';
            badge.style.top = `${Math.max(0, rect.top)}px`;
            badge.style.left = `${Math.max(0, rect.left)}px`;
            badge.style.backgroundColor = '#ef4444';
            badge.style.color = '#ffffff';
            badge.style.fontSize = '11px';
            badge.style.fontWeight = 'bold';
            badge.style.fontFamily = 'monospace';
            badge.style.padding = '1px 4px';
            badge.style.borderRadius = '3px';
            badge.style.zIndex = '2147483647';
            badge.style.pointerEvents = 'none';
            badge.style.boxShadow = '0 1px 3px rgba(0,0,0,0.5)';
            document.body.appendChild(badge);

            elements.push({
                id: currentId,
                tag: node.tagName.toLowerCase(),
                text: (node.innerText || node.value || node.getAttribute('placeholder') || '').trim().slice(0, 80),
                role: node.getAttribute('role') || undefined,
                aria_label: node.getAttribute('aria-label') || undefined,
                placeholder: node.getAttribute('placeholder') || undefined,
                name: node.getAttribute('name') || undefined,
                selector: getOptimalSelector(node),
                bounding_box: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }
            });

            currentId++;
        }
    });

    return {
        url: window.location.href,
        title: document.title,
        elements: elements
    };
})();
"""

REMOVE_MARKERS_JS = """
(() => {
    document.querySelectorAll('.autoqa-marker-badge').forEach(el => el.remove());
})();
"""

class DOMGroundingEngine:
    @staticmethod
    async def extract_interactive_map(page: Page) -> Tuple[DOMObservation, Dict[int, InteractiveElement]]:
        raw_result = await page.evaluate(DOM_GROUNDING_JS)
        
        elements_list: List[InteractiveElement] = []
        elements_lookup: Dict[int, InteractiveElement] = {}

        summary_lines = []
        for item in raw_result.get("elements", []):
            elem = InteractiveElement(**item)
            elements_list.append(elem)
            elements_lookup[elem.id] = elem

            desc = f"[{elem.id}] <{elem.tag}>"
            if elem.text:
                desc += f' "{elem.text}"'
            if elem.placeholder:
                desc += f' placeholder="{elem.placeholder}"'
            if elem.role:
                desc += f' role="{elem.role}"'
            if elem.aria_label:
                desc += f' aria-label="{elem.aria_label}"'
            summary_lines.append(desc)

        observation = DOMObservation(
            url=raw_result.get("url", ""),
            title=raw_result.get("title", ""),
            interactive_elements=elements_list,
            compact_text_summary="\n".join(summary_lines)
        )

        return observation, elements_lookup

    @staticmethod
    async def clean_visual_markers(page: Page):
        try:
            await page.evaluate(REMOVE_MARKERS_JS)
        except Exception:
            pass
