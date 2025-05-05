import carla
import math

class DistanceTracker:
    def __init__(self):
        self.total_distance_meters = 0
        self.previous_location = None

    @staticmethod
    def _calculate_distance(loc1, loc2):
        """Calculate the Euclidean distance between two CARLA locations."""
        return math.sqrt((loc2.x - loc1.x)**2 + (loc2.y - loc1.y)**2 + (loc2.z - loc1.z)**2)

    def update_distance(self, current_location):
        """Update the total distance based on the current location of the vehicle."""
        if self.previous_location is not None:
            distance = self._calculate_distance(self.previous_location, current_location)
            self.total_distance_meters += distance
            print(f"Total Distance Meters: {self.total_distance_meters}")
        self.previous_location = current_location

    def get_total_distance_km(self):
        """Get the total distance traveled in kilometers."""
        return self.total_distance_meters / 1000
