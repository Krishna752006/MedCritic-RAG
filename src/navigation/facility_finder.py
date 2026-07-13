from typing import List, Dict

class FacilityFinder:
    def __init__(self):
        # Database of simulated hospitals and specialized clinical centers
        self.facilities_db = [
            {
                "name": "St. Mary Medical Center",
                "type": "General & Emergency Care Hospital",
                "distance_km": 1.4,
                "address": "450 Medical Heights Way, Sector 4",
                "contact": "+1 (555) 234-9800",
                "emergency_support": True,
                "specialties": ["Cardiology", "Primary Care", "Infectious Diseases / Hematology"],
                "doctors": [
                    {"name": "Dr. Sarah Connor", "specialty": "Cardiologist", "booking_url": "https://stmary.org/appointments/connor-cardio"},
                    {"name": "Dr. Alex Mercer", "specialty": "General Practitioner", "booking_url": "https://stmary.org/appointments/mercer-gp"}
                ]
            },
            {
                "name": "Metropolitan Endocrinology Clinic",
                "type": "Specialty Treatment Center",
                "distance_km": 2.8,
                "address": "88 Glycemic Suites, Medical Zone 2",
                "contact": "+1 (555) 890-4122",
                "emergency_support": False,
                "specialties": ["Endocrinology"],
                "doctors": [
                    {"name": "Dr. Elena Rostova", "specialty": "Endocrinologist", "booking_url": "https://metroendo.org/booking/rostova-elena"}
                ]
            },
            {
                "name": "Cardiovascular Wellness Institute",
                "type": "Specialty Clinic",
                "distance_km": 3.1,
                "address": "12 Arterial Plaza, Boulevard Center",
                "contact": "+1 (555) 441-2399",
                "emergency_support": False,
                "specialties": ["Cardiology"],
                "doctors": [
                    {"name": "Dr. Marcus Vance", "specialty": "Cardiologist", "booking_url": "https://cardiovance.com/schedule/vance-marcus"}
                ]
            },
            {
                "name": "Mercy General Practice Clinicians",
                "type": "Primary Health Clinic",
                "distance_km": 0.6,
                "address": "102 Care Lane, Sector 1",
                "contact": "+1 (555) 112-7800",
                "emergency_support": False,
                "specialties": ["Primary Care"],
                "doctors": [
                    {"name": "Dr. John Doe", "specialty": "General Practitioner", "booking_url": "https://mercyclinic.org/booking/john-doe-gp"}
                ]
            },
            {
                "name": "City Neurological & Trauma Center",
                "type": "Tertiary Hospital & Emergency Trauma Hub",
                "distance_km": 4.2,
                "address": "800 Synapse Boulevard, Sector 9",
                "contact": "+1 (555) 777-9000",
                "emergency_support": True,
                "specialties": ["Neurology", "Cardiology", "Primary Care"],
                "doctors": [
                    {"name": "Dr. Robert Harrison", "specialty": "Neurologist", "booking_url": "https://citytrauma.org/find-doctor/harrison-neuro"},
                    {"name": "Dr. Lisa Cuddy", "specialty": "Neurological Specialist", "booking_url": "https://citytrauma.org/find-doctor/cuddy-lisa"}
                ]
            }
        ]

    def find_nearest(self, specialty: str, require_emergency: bool = False, limit: int = 3) -> List[Dict[str, any]]:
        """
        Retrieves matching nearby healthcare clinical facilities, ranked by proximity
        and whether they match the specialty and emergency requirements.
        """
        results = []
        for fac in self.facilities_db:
            specialty_match = False
            for s in fac["specialties"]:
                if specialty.lower() in s.lower():
                    specialty_match = True
                    break
            
            # Additional penalty/sorting score
            score = 0
            if specialty_match:
                score += 10
            if require_emergency == fac["emergency_support"]:
                score += 5
            elif require_emergency and not fac["emergency_support"]:
                score -= 10 # Critical penalty if emergency requested but facility doesn't support it

            results.append({
                "name": fac["name"],
                "type": fac["type"],
                "distance_km": fac["distance_km"],
                "address": fac["address"],
                "contact": fac["contact"],
                "emergency_support": fac["emergency_support"],
                "specialty_match": specialty_match,
                "score": score,
                "doctors": [doc for doc in fac["doctors"] if specialty.lower() in doc["specialty"].lower() or specialty.lower() in fac["specialties"]]
            })
            
        # Sort based on score(desc) and distance_km(asc)
        results.sort(key=lambda x: (-x["score"], x["distance_km"]))
        return results[:limit]

    def get_referrals_for_specialty(self, specialty: str) -> List[Dict[str, any]]:
        """
        Retrieves doctor recommendations and referral booking links for a specific specialty.
        """
        referrals = []
        for fac in self.facilities_db:
            for doc in fac["doctors"]:
                if specialty.lower() in doc["specialty"].lower() or any(specialty.lower() in spec.lower() for spec in fac["specialties"]):
                    referrals.append({
                        "doctor_name": doc["name"],
                        "specialty": doc["specialty"],
                        "hospital_name": fac["name"],
                        "distance_km": fac["distance_km"],
                        "booking_url": doc["booking_url"]
                    })
        referrals.sort(key=lambda x: x["distance_km"])
        return referrals
