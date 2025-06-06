import React, { useEffect, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import LayoutWrapper from "components/LayoutWrapper";

const VisualizationPage = () => {
  const [graphMap, setGraphMap] = useState({});
  const [selectedNodes, setSelectedNodes] = useState({});
  const [selectedSubgraphKeys, setSelectedSubgraphKeys] = useState({});
  const [highlightEdges, setHighlightEdges] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/cytoscape_subgraphs");
        const data = await response.json();
        setGraphMap(data.subgraphs);
        console.log("data ", data);

        const classKeys = Object.keys(data.subgraphs);

        const newSelected = {};
        classKeys.forEach((key) => {
          const base = key.split("_")[0];
          const subKeys = Object.keys(data.subgraphs).filter(
            (k) => k.startsWith(`${base}_`) || k === base
          );
          if (subKeys.length > 0 && !newSelected[base]) {
            newSelected[base] = subKeys.includes(base) ? base : subKeys[0];
          }
        });
        console.log("New Selected: ", newSelected);

        setSelectedSubgraphKeys(newSelected);
      } catch (error) {
        console.error("Failed to fetch graph data:", error);
      }
    };

    fetchData();
  }, []);

  const handleSubgraphChange = (classroomKey, newSubKey) => {
    setSelectedSubgraphKeys((prev) => ({
      ...prev,
      [classroomKey]: newSubKey,
    }));
    setSelectedNodes((prev) => ({
      ...prev,
      [classroomKey]: null,
    }));
  };

  const handleReassignClassroom = async (node, newClassroom) => {
    const payload = {
      Allocations: {
        [newClassroom]: [node.id],
      },
    };

    try {
      await fetch("http://127.0.0.1:5000/update_allocations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const updated = await fetch("http://127.0.0.1:5000/cytoscape_subgraphs");
      const updatedData = await updated.json();
      setGraphMap(updatedData.subgraphs);
      setSelectedNodes((prev) => ({
        ...prev,
        [node.classroom]: null,
      }));
    } catch (error) {
      console.error("Failed to update allocation:", error);
    }
  };

  const classrooms = Array.from(new Set(Object.keys(graphMap).map((k) => k.split("_")[0])));

  console.log("classrooms: ", classrooms);

  return (
    <LayoutWrapper>
      <h2>Multi-Classroom Graphs</h2>
      <label style={{ marginBottom: "1rem", display: "block" }}>
        <input
          type="checkbox"
          checked={highlightEdges}
          onChange={(e) => setHighlightEdges(e.target.checked)}
        />{" "}
        Highlight edges of selected nodes
      </label>

      {classrooms.map((classroom) => {
        const subgraphKeys = Object.keys(graphMap).filter(
          (k) => k === classroom || k.startsWith(`${classroom}_`)
        );
        const selectedKey = selectedSubgraphKeys[classroom];
        const elements = graphMap[selectedKey] || [];
        const selectedNode = selectedNodes[classroom];

        return (
          <div key={classroom} style={{ marginBottom: "40px" }}>
            <h3>Class Room: {classroom}</h3>

            <label>
              Select Subgraph:&nbsp;
              <select
                value={selectedKey || ""}
                onChange={(e) => handleSubgraphChange(classroom, e.target.value)}
              >
                {subgraphKeys.map((subKey) => (
                  <option key={subKey} value={subKey}>
                    {subKey === classroom
                      ? "all_connections"
                      : subKey.split("_").slice(1).join("_")}
                  </option>
                ))}
              </select>
            </label>

            <div style={{ height: "400px", marginTop: "10px" }}>
              <CytoscapeComponent
                elements={elements}
                style={{ width: "80%", height: "100%", backgroundColor: "#e5e5e5" }}
                layout={{ name: "preset" }}
                cy={(cy) => {
                  cy.on("tap", "node", (evt) => {
                    const nodeData = evt.target.data();
                    setSelectedNodes((prev) => ({
                      ...prev,
                      [classroom]: nodeData,
                    }));

                    if (highlightEdges) {
                      cy.edges().removeClass("highlighted");
                      cy.edges().forEach((edge) => {
                        if (
                          edge.source().id() === nodeData.id ||
                          edge.target().id() === nodeData.id
                        ) {
                          edge.addClass("highlighted");
                        }
                      });
                    }
                  });

                  cy.on("tapBlank", () => {
                    setSelectedNodes((prev) => ({
                      ...prev,
                      [classroom]: null,
                    }));
                    if (highlightEdges) {
                      cy.edges().removeClass("highlighted");
                    }
                  });
                }}
                stylesheet={[
                  {
                    selector: "node",
                    style: {
                      label: "data(label)",
                      width: 20,
                      height: 20,
                      "text-valign": "center",
                      color: "#fff",
                      "font-size": 6,
                      "text-outline-width": 0.5,
                      "text-outline-color": "#000",
                    },
                  },
                  {
                    selector: 'node[classroom = "1"]',
                    style: { "background-color": "#1f77b4" },
                  },
                  {
                    selector: 'node[classroom = "2"]',
                    style: { "background-color": "#ff7f0e" },
                  },
                  {
                    selector: 'node[classroom = "3"]',
                    style: { "background-color": "#2ca02c" },
                  },
                  {
                    selector: 'node[classroom = "4"]',
                    style: { "background-color": "#d62728" },
                  },
                  {
                    selector: 'node[classroom = "5"]',
                    style: { "background-color": "#9467bd" },
                  },
                  {
                    selector: 'node[classroom = "6"]',
                    style: { "background-color": "#8c564b" },
                  },
                  {
                    selector: "edge",
                    style: {
                      width: 2,
                      "target-arrow-shape": "triangle",
                      "curve-style": "bezier",
                    },
                  },
                  {
                    selector: 'edge[connection_type = "friends"]',
                    style: {
                      "line-color": "#0074D9",
                      "target-arrow-color": "#0074D9",
                    },
                  },
                  {
                    selector: 'edge[connection_type = "advice"]',
                    style: {
                      "line-color": "#FF851B",
                      "target-arrow-color": "#FF851B",
                    },
                  },
                  {
                    selector: 'edge[connection_type = "disrespect"]',
                    style: { "line-color": "#FF4136", "target-arrow-color": "#FF4136" },
                  },
                  {
                    selector: 'edge[connection_type = "feedback"]',
                    style: { "line-color": "#B10DC9", "target-arrow-color": "#B10DC9" },
                  },
                  {
                    selector: 'edge[connection_type = "influential"]',
                    style: { "line-color": "#2ECC40", "target-arrow-color": "#2ECC40" },
                  },
                  {
                    selector: "edge.highlighted",
                    style: {
                      "line-color": "#FFD700",
                      "target-arrow-color": "#FFD700",
                      "line-style": "solid",
                      width: 4,
                      "shadow-blur": 10,
                      "shadow-color": "#FFD700",
                      "shadow-opacity": 0.8,
                      "shadow-offset-x": 0,
                      "shadow-offset-y": 0,
                    },
                  },
                ]}
              />
            </div>

            {selectedNode && (
              <div style={{ marginTop: "10px", border: "1px solid #ccc", padding: "10px" }}>
                <p>
                  <strong>{selectedNode.label}</strong>
                </p>
                <p>First Name: {selectedNode.first_name}</p>
                <p>Last Name: {selectedNode.last_name}</p>
                <label>
                  Reassign to Classroom:&nbsp;
                  <select
                    onChange={(e) => handleReassignClassroom(selectedNode, e.target.value)}
                    defaultValue=""
                  >
                    <option value="" disabled>
                      -- Select Classroom --
                    </option>
                    {classrooms
                      .filter((c) => c !== selectedNode.classroom)
                      .map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                  </select>
                </label>
              </div>
            )}
          </div>
        );
      })}
    </LayoutWrapper>
  );
};

export default VisualizationPage;
