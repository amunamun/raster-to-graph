from shapely.geometry import Polygon, MultiLineString, LineString, Point
from shapely.ops import linemerge, unary_union

# List of polygons
polygons = [
    Polygon([(50, 50), (150, 50), (150, 150), (50, 150)]),
    Polygon([(100, 100), (200, 100), (200, 200), (100, 200)]),
    Polygon([(150, 50), (250, 50), (250, 150), (150, 150)]),
]

# Extract all polygon edges as LineStrings
edges = [LineString(polygon.exterior.coords) for polygon in polygons]

# Merge edges into a MultiLineString (keeps all edges)
merged_edges = linemerge(edges)

# Convert to MultiLineString if needed
if isinstance(merged_edges, LineString):
    merged_edges = MultiLineString([merged_edges])

# Find intersection points between all edges
intersection_points = set()
for i in range(len(edges)):
    for j in range(i + 1, len(edges)):
        inter = edges[i].intersection(edges[j])
        if isinstance(inter, Point):  # Single intersection point
            intersection_points.add((inter.x, inter.y))
        elif inter.geom_type == "MultiPoint":  # Multiple intersection points
            for pt in inter.geoms:
                intersection_points.add((pt.x, pt.y))

# Extract original vertices and edges
vertices = set()
edges_list = []

for line in merged_edges.geoms:
    coords = list(line.coords)
    for i in range(len(coords) - 1):
        v1, v2 = coords[i], coords[i + 1]
        edges_list.append((v1, v2))
        vertices.add(v1)
        vertices.add(v2)

# Include intersection points as vertices
vertices.update(intersection_points)




# Print results
print("Number of unique vertices:", len(vertices))
print("Vertices:", sorted(vertices))
print("\nEdges (connections between vertices):")
for edge in edges_list:
    print(edge)
