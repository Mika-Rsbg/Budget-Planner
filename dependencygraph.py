import os


def get_py_files(src_dir):
    """
    Get a list of all Python files in the source directory
    and its subdirectories.
    """
    py_files = []
    for root, _, files in os.walk(src_dir):
        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, src_dir)
            # Modulname: ersetzt OS-Pfade durch Punkte und entfernt .py
            module = rel_path.replace(os.sep, ".")[:-3]
            py_files.append((module, rel_path))
    return py_files


def extract_imports(file_path):
    """
    Parse a Python file and return a set of importierte Modulnamen.
    Example: 'from gui.basewindow import BaseWindow' → 'gui.basewindow'
    """
    import ast
    try:
        with open(file_path, "r", encoding="utf8") as f_obj:
            source = f_obj.read()
        tree = ast.parse(source, filename=file_path)
    except (SyntaxError, UnicodeDecodeError) as err:
        print(f"Fehler beim Parsen von {file_path}: {err}")
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # vollen Modulpfad nehmen, z.B. 'foo.bar'
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            # ebenfalls vollen Modulpfad
            imports.add(node.module)
    return imports


def hierarchy_pos(G, root, width=1.0, vert_gap=1.0, vert_loc=0.0, xcenter=0.0):
    """
    Create a hierarchy layout for a directed graph.
    This function is used to position nodes in a tree-like structure.
    """
    pos = {root: (xcenter, vert_loc)}
    children = list(G.successors(root))
    if not children:
        return pos
    dx = width / len(children)
    nextx = xcenter - width/2 - dx/2
    for child in children:
        nextx += dx
        pos.update(hierarchy_pos(G, child,
                                 width=dx,
                                 vert_gap=vert_gap,
                                 vert_loc=vert_loc-vert_gap,
                                 xcenter=nextx))
    return pos


def main():
    import tkinter as tk
    from tkinter import filedialog
    root_tk = tk.Tk()
    root_tk.withdraw()
    src_dir = filedialog.askdirectory(
        title="Select source directory (e.g. src folder)"
    )
    if not src_dir:
        print("No directory selected. Exiting.")
        return
    main_file = filedialog.askopenfilename(
        initialdir=src_dir, title="Select main file",
        filetypes=(("Python files", "*.py"),)
    )
    if not main_file:
        print("No main file selected. Exiting.")
        return
    # Netzwerk- und Plot-Bibliothek erst nach Dateiauswahl importieren
    import networkx as nx
    import matplotlib.pyplot as plt
    main_rel = os.path.relpath(main_file, src_dir)

    # Liste aller Module mit ihrem Pfad
    modules = get_py_files(src_dir)
    # Mapping: modulname → relative Datei
    module_mapping = {mod: rel for mod, rel in modules}

    g = nx.DiGraph()
    # Knoten hinzufügen effizient per Sammelaufruf
    g.add_nodes_from([rel for _, rel in modules])

    # Kanten erzeugen, wenn ein Modul ein anderes lokal importiert
    for mod, rel_path in modules:
        file_path = os.path.join(src_dir, rel_path)
        imported = extract_imports(file_path)
        for imp in imported:
            # Direkte Übereinstimmung
            if imp in module_mapping:
                target = module_mapping[imp]
                g.add_edge(rel_path, target)
            # ggf. nur Top-Level vergleichen (optional)
            else:
                top = imp.split(".")[0]
                if top in module_mapping:
                    g.add_edge(rel_path, module_mapping[top])

    # Liste der Module mit Nummern für einfachere Eingabe
    # mark isolated modules for overview
    isolates = [n for n, d in g.degree() if d == 0]
    isolate_names = [
        m for m in module_mapping if module_mapping[m] in isolates
    ]
    mods = list(module_mapping.keys())
    print("Module Übersicht (isoliert mit *):")
    for i, m in enumerate(mods, 1):
        mark = '*' if m in isolate_names else ''
        print(f"{i}: {m}{mark}")
    print("Manuelle Verknüpfungen hinzufügen (Format: quelle,ziel). "
          "Mehrere mit ';' trennen. Leere Eingabe zum Beenden.")
    print("Beispiel: 10,9;11,9;12,9;13,9;14,9;15,9;16,15")
    while True:
        line = input("Verknüpfung: ")
        if not line.strip():
            break
        for pair in [p.strip() for p in line.split(';') if p.strip()]:
            try:
                m1, m2 = [p.strip() for p in pair.split(",")]
            except ValueError:
                print("Ungültiges Format, bitte 'quelle,ziel'")
                continue

            # Nummern auflösen
            def resolve(tok):
                if tok.isdigit():
                    idx = int(tok)
                    if 1 <= idx <= len(mods):
                        return mods[idx-1]
                    print(f"Ungültige Nummer: {tok}")
                    return None
                return tok
            r1 = resolve(m1)
            r2 = resolve(m2)
            if not r1 or not r2:
                continue
            if r1 in module_mapping and r2 in module_mapping:
                g.add_edge(module_mapping[r1], module_mapping[r2])
                print(f"Manuell hinzugefügt: {r1} -> {r2}")
            else:
                print("Modul nicht gefunden:", r1, r2)

    # Textuelle Ausgabe der Dependencies
    print("Dependencies:")
    for src, dst in g.edges():
        print(f"{src} → {dst}")

    # Visualisierung
    # ── Baum-/Flow-Diagramm horizontal (links→rechts) ─────────────────────
    g.graph["graph"] = {
        "rankdir": "LR",
        "nodesep": "0.5",
        "ranksep": "1.0",
    }
    # use selected main file as root
    root = main_rel
    from collections import deque
    depth = {root: 0}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        for succ in g.successors(current):
            if succ not in depth:
                depth[succ] = depth[current] + 1
                queue.append(succ)
    max_depth = max(depth.values())
    for n in g.nodes():
        depth.setdefault(n, max_depth + 1)
    layers = {}
    for n, d in depth.items():
        layers.setdefault(d, []).append(n)
    # verschiebe Knoten mit nur einer Verbindung hinter ihren einzigen Nachbarn
    for n in list(g.nodes()):
        if g.degree(n) == 1:
            neighs = list(g.predecessors(n)) + list(g.successors(n))
            if len(neighs) == 1:
                neigh = neighs[0]
                new_d = depth.get(neigh, max_depth) + 1
                old_d = depth[n]
                if new_d != old_d:
                    layers[old_d].remove(n)
                    depth[n] = new_d
                    layers.setdefault(new_d, []).append(n)
    horizontal_gap = 1.0
    vertical_gap = 1.0
    pos = {}
    # small right shift per step within a layer
    intra_layer_offset = horizontal_gap * 0.1
    # isolate nodes with no connections and place them in top-left corner
    isolates = [n for n in g.nodes() if g.degree(n) == 0]
    print("Isolierte Module (kein Import):", isolates)
    for n in isolates:
        layers[depth[n]].remove(n)
    max_layer_size = max((len(nodes) for nodes in layers.values()), default=0)
    corner_x = -horizontal_gap
    corner_y = (max_layer_size - 1) / 2 * vertical_gap
    for i, n in enumerate(isolates):
        pos[n] = (corner_x, corner_y - i * (vertical_gap * 0.5))
    for d, nodes_in_layer in layers.items():
        cnt = len(nodes_in_layer)
        for i, n in enumerate(nodes_in_layer):
            x = d * horizontal_gap + i * intra_layer_offset
            y = (cnt - 1) / 2.0 * vertical_gap - i * vertical_gap
            pos[n] = (x, y)

    fig, ax = plt.subplots()

    # Zeichenfunktion extrahieren
    def draw_graph():
        ax.clear()
        nx.draw_networkx_nodes(
            g, pos, ax=ax, node_color="lightblue", node_size=sizes
        )
        nx.draw_networkx_labels(
            g, pos, labels=labels, ax=ax, font_color="black",
            font_weight="bold"
        )
        nx.draw_networkx_edges(g, pos, ax=ax, edge_color="gray",
                               arrowstyle="->", arrowsize=20,
                               connectionstyle="arc3,rad=0.3")
        ax.set_title("Import-Diagramm (Flow-Layout LR)")
        ax.set_axis_off()
        fig.canvas.draw_idle()

    # shorten node labels to base filename without extension
    labels = {n: os.path.splitext(os.path.basename(n))[0] for n in g.nodes()}
    # set node sizes: base 300 plus 100 per import
    sizes = [300 + 100 * g.in_degree(n) for n in g.nodes()]
    # initial draw
    draw_graph()
    # setup interactive draggable nodes
    selected = None

    def on_press(event):
        nonlocal selected
        if not event.inaxes:
            return
        for n, (x, y) in pos.items():
            xt, yt = ax.transData.transform((x, y))
            if ((xt - event.x)**2 + (yt - event.y)**2)**0.5 < 40:
                selected = n
                break

    def on_motion(event):
        if selected is None or not event.inaxes:
            return
        inv = ax.transData.inverted()
        xdata, ydata = inv.transform((event.x, event.y))
        pos[selected] = (xdata, ydata)
        # nur über draw_graph neu zeichnen
        draw_graph()

    def on_release(event):
        nonlocal selected
        selected = None
        # nach Loslassen neu zeichnen
        draw_graph()

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    fig.canvas.mpl_connect('button_release_event', on_release)

    plt.show()


if __name__ == "__main__":
    main()
