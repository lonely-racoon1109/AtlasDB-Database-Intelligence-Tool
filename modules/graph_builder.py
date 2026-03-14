from pyvis.network import Network
import graphviz

def detect_cardinality(df, fk_col):
    unique_vals = df[fk_col].nunique()
    total_rows = len(df)
    return "1-1" if unique_vals >= total_rows * 0.98 else "1-N"


def build_graph(schema, tables):

    net = Network(
        width="100%",
        height="630px",
        directed=True,
        bgcolor="#ffffff",
        font_color="black"
    )

    net.barnes_hut(
        gravity=-100,        # negative gravity pushes nodes apart
        central_gravity=0.1,  # lower central pull
        spring_length=100,    # increase distance between connected nodes
        spring_strength=0.01, # weaker springs allow more spacing
        damping=1       # lower damping = more movement
    )

    net.toggle_physics(False)

    # ---------- ADD TABLE NODES ----------
    for table, data in schema.items():
        columns_html = "\n".join([f"- {col}: {meta['dtype']} {meta['constraints']}" 
                                  for col, meta in data["columns"].items()])
        tooltip = f"{table}\n[Rows: {data['rows']}]\n{columns_html}"

        net.add_node(
            table,
            label=table,
            title=tooltip,
            shape="box",
            color="#e3f2fd"
        )

    # ---------- ADD FK EDGES ----------
    # Use FK info from schema instead of guessing table names
    for table, data in schema.items():
        for col, meta in data["columns"].items():
            if meta["constraints"] == "FK":
                # find the actual table that has this column as PK
                fk_table = None
                for t, d in schema.items():
                    for c, m in d["columns"].items():
                        if m["constraints"] == "PK" and c == col:
                            fk_table = t
                            break
                    if fk_table:
                        break

                if fk_table:
                    card = detect_cardinality(tables[table], col)
                    net.add_edge(
                        fk_table,
                        table,
                        arrows="to",
                        width=0.5,
                        label=card,
                        color="gray",
                        smooth="cubicBezier"
                    )



    # ---------- HOVER HIGHLIGHT ----------
    # Inside build_rigid_graph / build_graph
    # After adding nodes and edges
    net.set_options("""
    {
    "interaction": {
        "hover": true,
        "hoverConnectedEdges": true,
        "multiselect": false
    },
    "nodes": {
        "shape": "box",
        "borderWidth": 1,
        "borderWidthSelected": 3
    },
    "edges": {
        "arrows": {"to": {"enabled": true, "scaleFactor":1}},
        "smooth": {"type": "discrete"}
    }
    }
    """)

    return net

def build_er_diagram(schema):

    dot = graphviz.Digraph()

    dot.attr(rankdir="LR")
    dot.attr(splines="ortho")
    dot.attr(nodesep="0.8")
    dot.attr(ranksep="1")

    # ---------- ENTITIES ----------
    for table in schema.keys():

        dot.node(
            table,
            shape="box",
            style="filled",
            color="black",
            fillcolor="white"
        )

    # ---------- ATTRIBUTES ----------
    for table, data in schema.items():

        for col, meta in data["columns"].items():

            attr_id = f"{table}_{col}"

            label = col

            if meta["constraints"] == "PK":
                label = f"{col} (PK)"

            if meta["constraints"] == "FK":
                label = f"{col} (FK)"

            dot.node(
                attr_id,
                label=label,
                shape="ellipse"
            )

            dot.edge(table, attr_id)

    # ---------- RELATIONSHIPS ----------
    for table, data in schema.items():

        for col, meta in data["columns"].items():

            if meta["constraints"] == "FK":

                parent = None

                for t, d in schema.items():
                    for c, m in d["columns"].items():
                        if m["constraints"] == "PK" and c == col:
                            parent = t
                            break
                    if parent:
                        break

                if parent:

                    rel_name = f"{parent}_{table}_rel"

                    dot.node(
                        rel_name,
                        label="relation",
                        shape="diamond",
                        style="filled",
                        color="blue",
                        fillcolor="lightblue"
                    )

                    dot.edge(parent, rel_name, arrowhead="none")
                    dot.edge(rel_name, table, arrowhead="vee")

    dot.render("er_diagram", format="png", cleanup=True)

    return dot