#!/usr/bin/env python3
"""
validate.py — checks that portfolio/index.html meets assignment requirements.
Run from the repository's root: python3 scripts/validate.py
"""

import sys
import os
import re
from html.parser import HTMLParser

# Minimal DOM builder using only stdlib html.parser
class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []
        self.text_parts = []

    @property
    def text(self):
        """All text inside this node and its descendants, concatenated."""
        parts = list(self.text_parts)
        for child in self.children:
            parts.append(child.text)
        return " ".join(parts)

    def find_all(self, tag):
        """Return all descendant nodes with the given tag."""
        results = []
        for child in self.children:
            if child.tag == tag:
                results.append(child)
            results.extend(child.find_all(tag))
        return results

    def find(self, tag):
        found = self.find_all(tag)
        return found[0] if found else None


class DOMBuilder(HTMLParser):
    # Tags that do not have a closing tag in HTML5
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__()
        self.root = Node("__root__", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if tag in self.VOID_TAGS:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self.stack[-1].text_parts.append(stripped)


def parse_html(path):
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    builder = DOMBuilder()
    builder.feed(source)
    return builder.root


def word_count(text):
    return len(re.findall(r"\S+", text))


# Individual checks
def check_title(root):
    title_node = root.find("title")
    if title_node is None:
        return False, "<title> tag is missing"
    text = title_node.text.strip()
    if not text:
        return False, "<title> is empty"
    if text == "Your Name Here":
        return False, f'<title> says "Your Name Here" -> replace it with your name'
    return True, f'<title> is set to "{text}"'


def find_section(root, section_id):
    """Return the first element whose id attribute matches section_id."""
    def search(node):
        if node.attrs.get("id") == section_id:
            return node
        for child in node.children:
            result = search(child)
            if result is not None:
                return result
        return None
    return search(root)


def check_about(root):
    section = find_section(root, "about")
    if section is None:
        return False, '#about section not found'
    wc = word_count(section.text)
    if wc < 10:
        return False, f'#about has only {wc} word(s) of visible text -> add at least 10'
    return True, f'#about has {wc} words of visible text'


def has_heading(node):
    for tag in ("h2", "h3", "h4"):
        if node.find(tag) is not None:
            return True
    return False


def has_description(node):
    for tag in ("p", "dd", "span", "div"):
        for candidate in node.find_all(tag):
            if word_count(candidate.text) > 0:
                return True
    return False


def check_projects(root):
    section = find_section(root, "projects")
    if section is None:
        return False, '#projects section not found'

    # Count direct or shallow child containers that have a heading + description
    entries = []
    for child in section.children:
        if child.tag in ("div", "article", "li", "section"):
            if has_heading(child) and has_description(child):
                entries.append(child)

    if len(entries) < 2:
        return False, f'#projects has {len(entries)} complete project entry/entries -> need at least 2, each with a heading + description)'
    return True, f'#projects has {len(entries)} project entries'


def check_skills(root):
    section = find_section(root, "skills")
    if section is None:
        return False, '#skills section not found'

    items = []
    for tag in ("li", "span", "td"):
        for node in section.find_all(tag):
            if word_count(node.text) > 0:
                items.append(node)

    if len(items) < 3:
        return False, f'#skills has {len(items)} non-empty item(s) -> should have at least 3'
    return True, f'#skills has {len(items)} skill items'


def check_contact(root):
    section = find_section(root, "contact")
    if section is None:
        return False, '#contact section not found'

    links = section.find_all("a")
    for link in links:
        href = link.attrs.get("href", "").strip()
        if href and href != "#":
            return True, f'#contact has a link with href="{href}"'

    if not links:
        return False, '#contact has no <a> tag'
    return False, '#contact link href is empty or "#" -> replace it with a real URL'


# Runner
CHECKS = [
    ("<title> was updated",          check_title),
    ("#about has enough text",   check_about),
    ("#projects has 2+ entries", check_projects),
    ("#skills has 3+ items",     check_skills),
    ("#contact has a real link",   check_contact),
]

HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")


def main():
    if not os.path.exists(HTML_PATH):
        print(f"ERROR: could not find {HTML_PATH}")
        sys.exit(1)

    root = parse_html(HTML_PATH)

    failures = 0
    for label, fn in CHECKS:
        passed, message = fn(root)
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {message}")
        if not passed:
            failures += 1

    print()
    if failures == 0:
        print("All checks passed.")
        sys.exit(0)
    else:
        print(f"{failures} check(s) failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
