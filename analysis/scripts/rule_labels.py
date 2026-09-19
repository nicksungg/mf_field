"""Consistent display names. Archived method identifiers remain unchanged."""
import re

RULE_NAMES = {
    'single_l2': 'Selected model',
    'selected_single': 'Selected model',
    'inverse_mse': 'Inverse error mixture',
    'full': 'Fitted mixture',
    'auto': 'Automatic selection',
}
ALIASES = {
    'single': 'Selected model', 'selected': 'Selected model',
    'selected single': 'Selected model', 'selected model': 'Selected model',
    'inverse': 'Inverse error mixture', 'inverse weights': 'Inverse error mixture',
    'inverse error weights': 'Inverse error mixture', 'inverse error mixture': 'Inverse error mixture',
    'full': 'Fitted mixture', 'fitted': 'Fitted mixture',
    'full convex stacking': 'Fitted mixture', 'fitted mixture': 'Fitted mixture',
    'automatic': 'Automatic selection', 'auto': 'Automatic selection',
    'automatic selection': 'Automatic selection',
    'pair': 'Fitted pair',
}


def canonical_label(value):
    """Expand a display label or a ratio of labels, not arbitrary prose."""
    parts = []
    for part in str(value).split(' / '):
        match = re.fullmatch(r'(.*?)(\s*\([^)]*\))?', part.strip())
        name, suffix = match.group(1), match.group(2) or ''
        parts.append(ALIASES.get(name.lower(), name) + suffix)
    return ' / '.join(parts)


def header_label(value):
    """Wrap complete names in narrow table columns instead of abbreviating."""
    text = canonical_label(value)
    if not any(name in text for name in RULE_NAMES.values()):
        return text
    if ' / ' in text:
        numerator, denominator = text.split(' / ', 1)
        return r'\shortstack[r]{' + numerator + r' /\\' + denominator + '}'
    lines = []
    for j, part in enumerate(text.split(' / ')):
        if j:
            lines.append('/')
        for name in set(RULE_NAMES.values()):
            if part.startswith(name):
                lines.extend(name.split())
                suffix = part[len(name):].strip()
                if suffix:
                    lines.append(suffix)
                break
        else:
            lines.append(part)
    return r'\shortstack[r]{' + r'\\'.join(lines) + '}'
