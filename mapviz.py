def _clean(text):
    return text.replace('"', "'").replace("\\", "")


def build_dot(links, results, reveal=False):
    green_nodes = set()
    for link, r in zip(links, results):
        if r["status"] == "explained":
            green_nodes.add(link["from"])
            green_nodes.add(link["to"])

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontcolor="#111111"];',
        'edge [fontname="Helvetica", fontsize=10, fontcolor="#888888"];',
    ]

    nodes = {n for link in links for n in (link["from"], link["to"])}
    for n in sorted(nodes):
        color = "#a5d6a7" if n in green_nodes else "#eeeeee"
        lines.append(f'"{_clean(n)}" [fillcolor="{color}"];')

    for link, r in zip(links, results):
        a, b = _clean(link["from"]), _clean(link["to"])
        rel = _clean(link["relation"])
        s = r["status"]
        if s == "explained":
            lines.append(f'"{a}" -> "{b}" [label="{rel}", color="#2e7d32", penwidth=2];')
        elif s == "mentioned":
            lines.append(f'"{a}" -> "{b}" [label="named only", color="#ef6c00", style=dashed];')
        elif s == "incorrect":
            lines.append(f'"{a}" -> "{b}" [label="not quite", color="#c62828", style=dashed];')
        else:
            label = rel if reveal else "?"
            lines.append(f'"{a}" -> "{b}" [label="{label}", color="#9e9e9e", style=dashed];')

    lines.append("}")
    return "\n".join(lines)