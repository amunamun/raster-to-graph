import cv2
import itertools
from typing import List, Tuple, Set, Union, Optional
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from shapely.ops import linemerge


class GeometryProcessor:
    """
    Processes geometric data from a raw annotation file to create polygons,
    extract edges, merge them, calculate intersections, and split edges into segments.

    Attributes:
        coordinates (List[List[Tuple[int, int]]]): List of coordinate sets read from file.
        polygons (List[Polygon]): List of shapely Polygon objects created from coordinates.
        edges (List[LineString]): List of exterior edges of the polygons.
        merged_edges (MultiLineString): Merged set of edge geometries.
        intersection_points (Set[Tuple[float, float]]): Set of intersection points between edges.
        vertices (Set[Tuple[float, float]]): Set of vertices extracted from merged edges and intersections.
        edges_list (List[Tuple[Tuple[float, float], Tuple[float, float]]]): List of individual edge segments.
        logger: Logger instance passed during initialization.
    """

    def __init__(self, raw_annot_path: str, logger) -> None:
        """
        Initialize GeometryProcessor by reading coordinates from the file,
        creating polygons, extracting and merging edges, computing intersections,
        and finally extracting vertices and edge segments.

        Args:
            raw_annot_path (str): Path to the raw annotation file.
            logger: A logger object to record processing events.

        Raises:
            ValueError: If logger is not provided.
        """
        if logger is None:
            raise ValueError("A logger instance must be provided.")
        self.logger = logger
        self.logger.debug(f"Initializing GeometryProcessor with file: {raw_annot_path}")
        self.coordinates = self._read_coordinates(raw_annot_path)
        self.polygons = self._create_polygons()
        self.edges = self._extract_edges()
        self.merged_edges = self._merge_edges()
        self.intersection_points = self._calculate_intersections()
        self.vertices, self.edges_list = self._extract_vertices_and_edges()
        self.logger.info(f"Initialized GeometryProcessor with {len(self.polygons)} polygons, {len(self.edges)} edges, {len(self.intersection_points)} intersection points.")

    def _read_coordinates(self, file_path: str) -> List[List[Tuple[int, int]]]:
        """
        Read coordinate data from a file. Each line is split into words, with the last two words ignored.

        Args:
            file_path (str): Path to the file.

        Returns:
            List[List[Tuple[int, int]]]: A list of coordinate pairs lists.
        """
        self.logger.debug(f"Reading coordinates from file: {file_path}")
        coordinates_list: List[List[Tuple[int, int]]] = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if not parts or len(parts) < 4:
                        continue  # Skip empty or incomplete lines
                    # Remove the last two words
                    parts = parts[:-2]
                    coordinates = [(int(parts[i]), int(parts[i + 1])) for i in range(0, len(parts), 2)]
                    coordinates_list.append(coordinates)
            self.logger.debug(f"Read {len(coordinates_list)} coordinate sets.")
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise e
        return coordinates_list

    def _create_polygons(self) -> List[Polygon]:
        """
        Create shapely Polygon objects from coordinate sets.

        Returns:
            List[Polygon]: List of Polygon objects.
        """
        self.logger.debug("Creating polygons from coordinate data.")
        polygons = [Polygon(coords) for coords in self.coordinates if coords]
        self.logger.debug(f"Created {len(polygons)} polygons.")
        return polygons

    def _extract_edges(self) -> List[LineString]:
        """
        Extract the exterior edges of each polygon.

        Returns:
            List[LineString]: List of exterior edges as LineString objects.
        """
        self.logger.debug("Extracting exterior edges from polygons.")
        edges = [LineString(p.exterior.coords) for p in self.polygons]
        self.logger.debug(f"Extracted {len(edges)} edges.")
        return edges

    def _merge_edges(self) -> MultiLineString:
        """
        Merge individual edges into a unified MultiLineString.

        Returns:
            MultiLineString: Merged edges.
        """
        self.logger.debug("Merging edges.")
        merged = linemerge(self.edges)
        if isinstance(merged, LineString):
            merged = MultiLineString([merged])
        self.logger.debug(f"Merged edges into {len(merged.geoms)} geometries.")
        return merged

    def _calculate_intersections(self) -> Set[Tuple[float, float]]:
        """
        Calculate intersections between each pair of edges.

        Returns:
            Set[Tuple[float, float]]: Set of (x, y) intersection points.
        """
        self.logger.debug("Calculating intersections among edges.")
        intersection_points: Set[Tuple[float, float]] = set()
        for edge1, edge2 in itertools.combinations(self.edges, 2):
            inter = edge1.intersection(edge2)
            if isinstance(inter, Point):
                intersection_points.add((inter.x, inter.y))
            elif inter.geom_type == "MultiPoint":
                for pt in inter.geoms:
                    intersection_points.add((pt.x, pt.y))
        self.logger.debug(f"Found {len(intersection_points)} intersection points.")
        return intersection_points

    def _extract_vertices_and_edges(self) -> Tuple[
        Set[Tuple[float, float]], List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
        """
        Extract vertices and individual edge segments from merged edges.
        Vertices are taken from segment endpoints and include intersection points.

        Returns:
            Tuple[Set[Tuple[float, float]], List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
                A set of vertices and a list of edge segments.
        """
        self.logger.debug("Extracting vertices and segments from merged edges.")
        vertices: Set[Tuple[float, float]] = set()
        edges_list: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        for line in self.merged_edges.geoms:
            coords = list(line.coords)
            for v1, v2 in zip(coords, coords[1:]):
                edges_list.append((v1, v2))
                vertices.update([v1, v2])
        vertices.update(self.intersection_points)
        self.logger.debug(f"Extracted {len(vertices)} vertices and {len(edges_list)} segments.")
        return vertices, edges_list

    @staticmethod
    def create_segments(points: List[Point]) -> List[List[Point]]:
        """
        Create segments (pairs of points) from a list of points.

        Args:
            points (List[Point]): A list of shapely Point objects.

        Returns:
            List[List[Point]]: List of segments (each a list of two Points).
        """
        return [points[i:i + 2] for i in range(len(points) - 1)]

    @staticmethod
    def split_line_by_candidate_points(
            end1: Tuple[int, int],
            end2: Tuple[int, int],
            candidate_points: Set[Tuple[float, float]],
            tolerance: float = 1e-6
    ) -> List[Point]:
        """
        Split a line (defined by two endpoints) by inserting candidate points that lie on the line.

        Args:
            end1 (Tuple[int, int]): The first endpoint.
            end2 (Tuple[int, int]): The second endpoint.
            candidate_points (Set[Tuple[float, float]]): Candidate points to check.
            tolerance (float): Tolerance for considering a point to be on the line.

        Returns:
            List[Point]: Sorted list of Points along the line.
        """
        pt1, pt2 = Point(end1), Point(end2)
        line = LineString([pt1, pt2])
        included = [pt1, pt2]
        for cp in candidate_points:
            cp_point = Point(cp)
            if line.distance(cp_point) < tolerance or line.contains(cp_point):
                included.append(cp_point)
        # Sort points along the dominant axis
        delta_x, delta_y = abs(pt2.x - pt1.x), abs(pt2.y - pt1.y)
        sort_key = (lambda p: p.x) if delta_x > delta_y else (lambda p: p.y)
        sorted_points = sorted(included, key=sort_key)
        return sorted_points

    def split_edges_into_segments(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Split each edge into smaller segments using candidate intersection points.

        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, int]]]: Unique segments with integer coordinates.
        """
        self.logger.debug("Splitting edges into segments using intersection points.")
        segments = []
        for pt1, pt2 in self.edges_list:
            pt1_int, pt2_int = tuple(map(int, pt1)), tuple(map(int, pt2))
            seg_points = self.split_line_by_candidate_points(pt1_int, pt2_int, self.intersection_points)
            if len(seg_points) > 2:
                segments.extend(self.create_segments(seg_points))
            else:
                segments.append(seg_points)
        unique_segments = set()
        for seg in segments:
            # Convert each segment to a tuple of integer coordinate pairs
            p1 = (int(seg[0].x), int(seg[0].y))
            p2 = (int(seg[1].x), int(seg[1].y))
            unique_segments.add((p1, p2))
        result = list(unique_segments)
        self.logger.debug(f"Created {len(result)} unique segments.")
        return result

    def plot_segments(self,
            segments: List[Tuple[Tuple[int, int], Tuple[int, int]]],
            input_image: str = 'src/utils/plain_sheet.png',
            output_image: str = "polygons.png"
    ) -> None:
        """
        Draw segments and their endpoints on an image and save it.

        Args:
            segments (List[Tuple[Tuple[int, int], Tuple[int, int]]]): List of segments to draw.
            input_image (str): Input image file path.
            output_image (str): Output image file path.
            logger: Optional logger to record the process.

        Raises:
            ValueError: If the input image cannot be read.
        """
        self.logger.debug(f"Saving segments to image: {output_image}")
        image = cv2.imread(input_image)
        if image is None:
            self.logger.error(f"Failed to read image: {input_image}")
            raise ValueError(f"Input image {input_image} not found.")
        for pt1, pt2 in segments:
            cv2.line(image, pt1, pt2, (0, 0, 0), 2)
            cv2.circle(image, pt1, 10, (0, 0, 255), -1)
            cv2.circle(image, pt2, 10, (0, 0, 255), -1)
        cv2.imwrite(output_image, image)
        self.logger.info(f"Saved segments image to: {output_image}")

    @staticmethod
    def scale_segments(
            segments: List[Tuple[Tuple[int, int], Tuple[int, int]]],
            scale_x: float,
            scale_y: float,
            left_padding: int,
            top_padding: int
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Scale and translate segments by provided factors and paddings.

        Args:
            segments (List[Tuple[Tuple[int, int], Tuple[int, int]]]): List of segments.
            scale_x (float): Scaling factor for x-coordinate.
            scale_y (float): Scaling factor for y-coordinate.
            left_padding (int): Padding added to x-coordinate.
            top_padding (int): Padding added to y-coordinate.

        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, int]]]: Scaled and translated segments.
        """
        scaled_segments = []
        for (x1, y1), (x2, y2) in segments:
            new_x1 = int(x1 * scale_x + left_padding)
            new_y1 = int(y1 * scale_y + top_padding)
            new_x2 = int(x2 * scale_x + left_padding)
            new_y2 = int(y2 * scale_y + top_padding)
            scaled_segments.append(((new_x1, new_y1), (new_x2, new_y2)))
        return scaled_segments
