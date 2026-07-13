from src.navigation.facility_finder import FacilityFinder
from src.navigation.specialty_router import SpecialtyRouter
from src.navigation.urgency_detector import UrgencyDetector


class UrgencyService:
    def __init__(self):
        self.urgency_detector = UrgencyDetector()
        self.specialty_router = SpecialtyRouter()
        self.facility_finder = FacilityFinder()

    def route_care(self, findings):
        urgency = self.urgency_detector.evaluate_urgency(findings)
        specialty = self.specialty_router.route_specialty(findings)
        facilities = self.facility_finder.find_nearest(specialty["specialty"])
        return urgency, specialty, facilities

