from datetime import date
from django.utils import timezone

def get_deadline_info():
    aujourdhui = timezone.now().date()
    annee_actuelle = aujourdhui.year

    deadlines = {
        1: date(annee_actuelle, 5, 31),
        2: date(annee_actuelle, 8, 31),
        3: date(annee_actuelle, 11, 30),
        4: date(annee_actuelle + 1, 2, 28),
    }

    quarter = 0
    next_deadline = None
    deadline_designation = ""
    days_remaining = None

    if aujourdhui <= deadlines[1]:
        quarter = 1
        next_deadline = deadlines[1]
        deadline_designation = "1er trimestre"
        days_remaining = (next_deadline - aujourdhui).days
    elif aujourdhui <= deadlines[2]:
        quarter = 2
        next_deadline = deadlines[2]
        deadline_designation = "2ème trimestre"
        days_remaining = (next_deadline - aujourdhui).days
    elif aujourdhui <= deadlines[3]:
        quarter = 3
        next_deadline = deadlines[3]
        deadline_designation = "3ème trimestre"
        days_remaining = (next_deadline - aujourdhui).days
    else:
        quarter = 4
        next_deadline = deadlines[4]
        deadline_designation = "4ème trimestre"
        days_remaining = (next_deadline - aujourdhui).days

    return {
        'quarter': quarter,
        'deadline': next_deadline,
        'designation': deadline_designation,
        'days_remaining': days_remaining,
    }

def get_deadline_for_arrivage(trimestre, annee):
    if trimestre == 1:
        return date(annee, 5, 31)
    elif trimestre == 2:
        return date(annee, 8, 31)
    elif trimestre == 3:
        return date(annee, 11, 30)
    elif trimestre == 4:
        return date(annee + 1, 2, 28)
    return None