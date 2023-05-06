from .models import *
from datetime import datetime, timedelta

def recommend_activity_checker(date):
    delta = datetime.now() - date

    if Predictions.objects.filter(title = "Land Preparation").exists():
        if delta < timedelta(days=60):
            return "Land Preparation"
        else:
            if Predictions.objects.filter(title = "Weeding").exists():
                if delta < timedelta(days=3):
                    return "Weeding"
                else:
                    if Predictions.objects.filter(title = "Field Lay outing & Holing").exists():
                        if delta < timedelta(days=3):
                            return "Field Lay outing & Holing"
                        else:
                            if Predictions.objects.filter(title = "Application of fertilizer").exists():
                                if delta < timedelta(days=1):
                                    return "Application of fertilizer"
                                else:
                                    if Predictions.objects.filter(title = "Transplanting of Seedlings").exists():
                                        if delta < timedelta(days=3):
                                            return "Transplanting of Seedlings"
                                        
                                        else:
                                            if delta < timedelta(days=730):
                                                return True
                                            else:
                                                return "Harvesting"
                                    else:
                                        return "Transplanting of Seedlings"
                            else:
                                return "Application of fertilizer"
                    else:
                        return "Field Lay outing & Holing"
            else:
                return "Weeding"
    else:
        return "Land Preparation"
    