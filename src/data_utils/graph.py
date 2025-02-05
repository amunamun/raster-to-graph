import numpy as np
from collections import deque
import random
from typing import List, Tuple, Dict, Any, Union


class GraphAnnotator:
    """
    Class to build a graph from segments and create annotations based on neighbor connectivity.

    The graph is maintained in two representations:
      - coordinate_graph: Stores neighboring points as coordinates.
      - code_graph: Stores neighbor connectivity as a 4-character binary string representing
                    connections in the order [Up, Left, Down, Right].

    The class also constructs a quatree (via BFS) based on the coordinate graph and generates
    annotation dictionaries for further processing.
    """
    # Mapping from binary edge string to an edge code integer.
    edges_rev: Dict[str, int] = {
        '0000': 0, '0001': 1, '0010': 2, '0011': 3,
        '0100': 4, '0110': 5, '0111': 6, '1000': 7,
        '1001': 8, '1011': 9, '1100': 10, '1101': 11,
        '1110': 12, '1111': 13, '0101': 14, '1010': 15
    }

    def __init__(self, segments: List[Tuple[Tuple[int, int], Tuple[int, int]]],
                 image_id: Union[int, str],
                 category_id: Union[int, str],
                 logger) -> None:
        """
        Initialize the GraphAnnotator.

        Args:
            segments (List[Tuple[Tuple[int, int], Tuple[int, int]]]):
                List of segments, each defined by two points (pt1, pt2).
            image_id (int or str): Identifier for the image.
            category_id (int or str): Identifier for the category.
        """
        self.logger = logger
        self.segments = segments
        self.image_id = image_id
        self.category_id = category_id
        self.coordinate_graph: Dict[Any, Any] = {}  # Keys: points; Values: list of neighbor coordinates.
        self.code_graph: Dict[Any, str] = {}  # Keys: points; Values: neighbor connectivity as a binary string.
        self.annotations: List[Dict[str, Any]] = []  # List to store annotation dictionaries.
        self.logger.info(f"GraphAnnotator initialized with {len(segments)} segments.")

    def init_neighbors_as_coordinates(self) -> List[Tuple[int, int]]:
        """
        Initialize a list of neighbor coordinates with default values.
        The default value for a neighbor is (-1, -1), indicating no neighbor.

        Returns:
            List[Tuple[int, int]]: List representing neighbors [Up, Left, Down, Right].
        """
        return [(-1, -1)] * 4

    def init_neighbors_as_code(self) -> str:
        """
        Initialize a neighbor connectivity code string.

        Returns:
            str: A 4-character binary string ("0000") representing no connections.
        """
        return "0000"

    def get_direction_index(self, origin: Tuple[int, int], point: Tuple[int, int]) -> int:
        """
        Compute the direction index from the origin to a point based on image coordinate conventions.

        The direction indices are:
            0: Up
            1: Left
            2: Down
            3: Right

        Args:
            origin (Tuple[int, int]): The starting point (x, y).
            point (Tuple[int, int]): The target point (x, y).

        Returns:
            int: The index corresponding to the direction from origin to point.
        """
        dx = point[0] - origin[0]
        dy = origin[1] - point[1]  # Invert Y-axis for image coordinates
        angle = np.degrees(np.arctan2(dy, dx))

        if -45 <= angle <= 45:
            return 3  # Right
        elif 45 < angle <= 135:
            return 0  # Up
        elif angle > 135 or angle < -135:
            return 1  # Left
        elif -135 <= angle < -45:
            return 2  # Down
        # Should not reach here; default to -1 if undefined
        self.logger.warning(f"Undefined direction for origin {origin} and point {point}. Angle: {angle}")
        return -1

    def build_graphs(self) -> Tuple[Dict[Any, Any], Dict[Any, str]]:
        """
        Build the coordinate and code graphs from the segments.
        Also constructs a quatree via BFS that is stored in the coordinate_graph under the 'quatree' key.

        Returns:
            Tuple[Dict[Any, Any], Dict[Any, str]]:
                - coordinate_graph: Graph with neighbors as coordinates.
                - code_graph: Graph with neighbor connectivity as binary strings.
        """
        self.logger.info("Building graphs from segments.")
        # Build graphs based on segments
        for pt1, pt2 in self.segments:
            if pt1 not in self.coordinate_graph:
                self.coordinate_graph[pt1] = self.init_neighbors_as_coordinates()
            if pt2 not in self.coordinate_graph:
                self.coordinate_graph[pt2] = self.init_neighbors_as_coordinates()

            if pt1 not in self.code_graph:
                self.code_graph[pt1] = self.init_neighbors_as_code()
            if pt2 not in self.code_graph:
                self.code_graph[pt2] = self.init_neighbors_as_code()

            # Determine direction indexes for each connection
            dir_idx_pt1_to_pt2 = self.get_direction_index(pt1, pt2)
            dir_idx_pt2_to_pt1 = self.get_direction_index(pt2, pt1)

            # Update coordinate graph with neighbor points
            self.coordinate_graph[pt1][dir_idx_pt1_to_pt2] = pt2
            self.coordinate_graph[pt2][dir_idx_pt2_to_pt1] = pt1

            # Update code graph by setting the corresponding digit to "1"
            code_list_pt1 = list(self.code_graph[pt1])
            code_list_pt1[dir_idx_pt1_to_pt2] = "1"
            self.code_graph[pt1] = ''.join(code_list_pt1)

            code_list_pt2 = list(self.code_graph[pt2])
            code_list_pt2[dir_idx_pt2_to_pt1] = "1"
            self.code_graph[pt2] = ''.join(code_list_pt2)

            self.logger.debug(f"Connected {pt1} to {pt2}; updated indices {dir_idx_pt1_to_pt2} and {dir_idx_pt2_to_pt1}.")

        # Find the starting point closest to (0, 0) (ignore any special keys like 'quatree')
        valid_points = [pt for pt in self.coordinate_graph.keys() if pt != 'quatree']
        origin = min(valid_points, key=lambda p: np.hypot(p[0], p[1]))
        self.logger.info(f"Origin for quatree determined as {origin}.")

        # BFS to construct quatree levels
        visited = set()
        queue = deque([(origin, 0)])  # Each entry is a tuple: (point, level)
        quatree: Dict[int, List[Any]] = {}

        while queue:
            point, level = queue.popleft()
            if point in visited:
                continue
            visited.add(point)
            quatree.setdefault(level, []).append(point)
            for neighbor in self.coordinate_graph[point]:
                if neighbor != (-1, -1) and neighbor not in visited:
                    queue.append((neighbor, level + 1))
            self.logger.debug(f"Point {point} added at level {level} in quatree.")

        self.coordinate_graph['quatree'] = [quatree]
        self.logger.info(f"quatree construction complete with levels: {list(quatree.keys())}")
        return self.coordinate_graph, self.code_graph

    def get_edge_code(self, edges_class: str) -> int:
        """
        Convert a 4-character binary string representing neighbor connectivity into an edge code.

        Args:
            edges_class (str): 4-character binary string representing neighbor connections.

        Returns:
            int: The corresponding edge code from the mapping.
        """
        code = self.edges_rev.get(edges_class)
        if code is None:
            self.logger.error(f"Edge code not found for binary string: {edges_class}")
            raise ValueError(f"Invalid edges_class: {edges_class}")
        return code

    def create_annotations(self, annot_id):
        """
        Generate annotation dictionaries based on the code graph.
        Each annotation includes:
            - image_id
            - category_id
            - unique annotation id
            - point (as a list)
            - edge_code (derived from the connectivity string)
            - a list of semantic tags (randomly chosen)

        Returns:
            List[Dict[str, Any]]: A list of annotation dictionaries.
        """
        self.logger.info("Creating annotations based on code graph.")
        for key, value in self.code_graph.items():
            # Skip special keys (e.g., the 'quatree' entry)
            if key == 'quatree':
                continue
            semantics = random.choices(
                ['outside', 'kitchen', 'bathroom', 'bedroom', 'closet', 'corridor', 'restroom', 'balcony'],
                k=4
            )
            annotation = {
                "image_id": self.image_id,
                "category_id": self.category_id,
                "id": annot_id,
                "point": list(key) if isinstance(key, tuple) else key,
                "edge_code": self.get_edge_code(value),
                "semantic": semantics
            }
            self.annotations.append(annotation)
            self.logger.debug(f"Annotation created: {annotation}")
            annot_id += 1
        self.logger.info(f"Total annotations created: {len(self.annotations)}")
        return self.annotations, annot_id


    def create_structure_bbox(self):
        # Extract x and y values
        x_values = [p[0] for p in self.code_graph.keys()]
        y_values = [p[1] for p in self.code_graph.keys()]

        # Compute bounding box
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)

        return {'x_min': x_min, 'y_min': y_min, 'x_max': x_max, 'y_max': y_max}