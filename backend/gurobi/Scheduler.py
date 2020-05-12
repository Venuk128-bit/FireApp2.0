import gurobipy as gp
from gurobipy import GRB

from gurobi.DataGenerator import *
from gurobi.AssetTypes import *

# Takes a list of volunteers, returns a tupleList formatted for the constraint model
from gurobi.VolunteerGraph import Assignment, VolunteerPlot, RequestPlot


def formatAvailability(Volunteers):
    availability = gp.tuplelist()
    for volunteer in Volunteers:
        for shift in shiftpopulator():
            if volunteer.Availability[shift]:
                availability.append((volunteer.id, DayHourtoNumConverter(shift)))
    return availability


# Takes a list of Volunteers and Requests and returns a volunteer assignment and model
def Schedule(Volunteers, VehicleRequest):
    # Number of volunteers required for each shift. "time": (total, advanced)
    shiftRequirements = RequesttoRequirements(VehicleRequest)

    # Amount of hours each volunteer wants to work over the entire week
    preferredHours = {}
    for volunteer in Volunteers:
        preferredHours[volunteer.id] = volunteer.prefHours

    # Volunteer availability
    availability = formatAvailability(Volunteers)
    formattedRequests = gp.tuplelist()
    for volunteer in Volunteers:
        for request in VehicleRequest:
            formattedRequests.append((volunteer.id, request.RequestNo))

    # list qualified Volunteers
    advancedQualified = []
    crewLeaderQualified = []
    driverQualified = []
    for volunteer in Volunteers:
        if volunteer.Explvl == "Advanced":
            advancedQualified.append(volunteer)
        elif volunteer.Explvl == "Crew Leader":
            crewLeaderQualified.append(volunteer)
            driverQualified.append(volunteer)
            advancedQualified.append(volunteer)
        elif volunteer.Explvl == "Driver":
            driverQualified.append(volunteer)
            advancedQualified.append(volunteer)

    # Model
    model = gp.Model("assignment")

    # Assignment variables: assigned[v,s] == 1 if volunteer v is assigned to shift s.
    assigned = model.addVars(availability, ub=1, lb=0, name="assigned")

    # Assignment variables: assignedToVehicle[volunteerID, VehicleID, VehicleStart]
    assignedToVehicle = model.addVars(formattedRequests, ub=1, lb=0, name="assignedToVehicle")

    # easy access to constraints, mostly for debugging
    constraints = []

    # Constraints: volunteer must be assigned to a vehicle for an entire shift
    for volunteer in Volunteers:
        for request in VehicleRequest:
            shiftSum = 0
            for i in range(request.Duration):
                time = request.StartTime + i
                shiftSum = shiftSum + assigned.sum(volunteer.id, time)
            constraints.append(
                model.addGenConstrIndicator(assignedToVehicle[volunteer.id, request.RequestNo], True, shiftSum,
                                            GRB.EQUAL, request.Duration))

    # Constraints: Volunteers cannot be assigned to 2 vehicles at once
    for i in range(len(VehicleRequest)):
        for g in range(i + 1, len(VehicleRequest)):
            iRangeMin = VehicleRequest[i].StartTime
            iRangeMax = VehicleRequest[i].StartTime + VehicleRequest[i].Duration
            gRangeMin = VehicleRequest[g].StartTime
            gRangeMax = VehicleRequest[g].StartTime + VehicleRequest[g].Duration

            # if vehicle times overlap, a volunteer can only be assigned to one of them
            if (iRangeMin <= gRangeMin and iRangeMax >= gRangeMin) or (
                    gRangeMin <= iRangeMin and gRangeMax >= iRangeMin):
                for volunteer in Volunteers:
                    sum = 0
                    sum = sum + assignedToVehicle.sum(volunteer.id, VehicleRequest[i].RequestNo)
                    sum = sum + assignedToVehicle.sum(volunteer.id, VehicleRequest[g].RequestNo)
                    constraints.append(model.addConstr(sum, GRB.LESS_EQUAL, 1, "IncompatibleTrucks_" + str(i) + str(g)))

    # Constraints: Each vehicle must be filled + Each vehicle must meet qualifications
    for request in VehicleRequest:
        constraints.append(
            model.addConstr(assignedToVehicle.sum('*', request.RequestNo), GRB.EQUAL,
                            request.AssetType.TotalReq, "TruckFilled_" + str(request.RequestNo)))

        totalAdvancedOnVehicle = 0
        for volunteer in advancedQualified:
            totalAdvancedOnVehicle = totalAdvancedOnVehicle + assignedToVehicle.sum(volunteer.id, request.RequestNo)
        advancedTarget = request.AssetType.AdvancedReq + request.AssetType.CrewLeaderReq + request.AssetType.DriverReq
        constraints.append(model.addConstr(totalAdvancedOnVehicle, GRB.GREATER_EQUAL, advancedTarget,"TruckQualifiedAdvanced_" + str(request.RequestNo)))

        totalCrewLeadersOnVehicle = 0
        for volunteer in crewLeaderQualified:
            totalCrewLeadersOnVehicle = totalCrewLeadersOnVehicle + assignedToVehicle.sum(volunteer.id, request.RequestNo)
        crewLeaderTarget = request.AssetType.CrewLeaderReq
        constraints.append(model.addConstr(totalCrewLeadersOnVehicle, GRB.GREATER_EQUAL, crewLeaderTarget,
                                           "TruckQualifiedCrewLeader_" + str(request.RequestNo)))
        totalDriversOnVehicle = 0
        for volunteer in driverQualified:
            totalDriversOnVehicle = totalDriversOnVehicle + assignedToVehicle.sum(volunteer.id, request.RequestNo)
        driverTarget = request.AssetType.CrewLeaderReq + request.AssetType.DriverReq
        constraints.append(model.addConstr(totalDriversOnVehicle, GRB.GREATER_EQUAL, driverTarget,
                            "TruckQualifiedDriver_" + str(request.RequestNo)))


    # Constraints: total hours worked <= preferred hours for each volunteer
    for volunteer in Volunteers:
        constraints.append(
            model.addConstr(assigned.sum(volunteer.id, '*'), GRB.LESS_EQUAL, preferredHours[volunteer.id],
                            "prefHours_" + str(volunteer.id)))

    # Constraints: total volunteers met for each shift
    for shiftKey in shiftRequirements.keys():
        numRequired = shiftRequirements[shiftKey][0]
        constraints.append(
            model.addConstr(assigned.sum('*', shiftKey), GRB.EQUAL, numRequired, "ShiftFilled_" + str(shiftKey)))

    # Constraints: qualifications met for each shift
    for shiftKey in shiftRequirements.keys():
        numRequiredAdvanced = shiftRequirements[shiftKey][1] + shiftRequirements[shiftKey][2] + shiftRequirements[shiftKey][3]
        totalAdvanced = 0
        for volunteer in advancedQualified:
            totalAdvanced = totalAdvanced + assigned.sum(volunteer.id, shiftKey)
        constraints.append(
            model.addConstr(totalAdvanced, GRB.GREATER_EQUAL, numRequiredAdvanced, "ShiftQualifiedAdvanced_" + str(shiftKey)))

        numRequiredCrewLeaders = shiftRequirements[shiftKey][2]
        totalCrewLeaders = 0
        for volunteer in crewLeaderQualified:
            totalCrewLeaders = totalCrewLeaders + assigned.sum(volunteer.id, shiftKey)
        constraints.append(
            model.addConstr(totalCrewLeaders, GRB.GREATER_EQUAL, numRequiredCrewLeaders,
                            "ShiftQualifiedCrewLeaders_" + str(shiftKey)))

        numRequiredDrivers = shiftRequirements[shiftKey][3] + shiftRequirements[shiftKey][2]
        totalDrivers = 0
        for volunteer in driverQualified:
            totalDrivers = totalDrivers + assigned.sum(volunteer.id, shiftKey)
        constraints.append(
            model.addConstr(totalDrivers, GRB.GREATER_EQUAL, numRequiredDrivers,
                            "ShiftQualifiedDrivers_" + str(shiftKey)))

    # The objective is to minimise the hours worked by volunteers (while still filling all requirements)
    model.setObjective(gp.quicksum(assigned[v, s] for v, s in availability), GRB.MINIMIZE)

    model.optimize()

    # assignments = []
    plotList = []
    RecommendationList = []
    for request in VehicleRequest:
        vehicleDict = {}
        vehicleDict["asset_id"] = request.RequestNo
        vehicleDict["asset_class"] = request.AssetType.type
        VolunteerListAdvanced = []
        VolunteerListBasic = []
        VolunteerListDriver = []
        VolunteerListCrewLeader = []
        for volunteer in Volunteers:
            value = assignedToVehicle[(volunteer.id, request.RequestNo)].X
            if value > 0:
                volunteerDict = {}
                if volunteer.Explvl == "Advanced":
                    volunteerDict["volunteer_id"] = volunteer.id
                    volunteerDict["volunteer_name"] = volunteer.name
                    volunteerDict["role"] = "Crew Member"
                    qualifications = []
                    qualifications.append("Advanced Training")
                    volunteerDict["qualifications"] = qualifications
                    volunteerDict["contact_info"] = {"type": "phone", "detail": volunteer.phonenumber}
                    VolunteerListAdvanced.append(volunteerDict)
                elif volunteer.Explvl == "Crew Leader":
                    volunteerDict["volunteer_id"] = volunteer.id
                    volunteerDict["volunteer_name"] = volunteer.name
                    volunteerDict["role"] = "Crew Member"
                    qualifications = []
                    qualifications.append("Advanced Training")
                    qualifications.append("Driver")
                    qualifications.append("Crew Leader")
                    volunteerDict["qualifications"] = qualifications
                    volunteerDict["contact_info"] = {"type": "phone", "detail": volunteer.phonenumber}
                    VolunteerListCrewLeader.append(volunteerDict)
                elif volunteer.Explvl == "Driver":
                    volunteerDict["volunteer_id"] = volunteer.id
                    volunteerDict["volunteer_name"] = volunteer.name
                    volunteerDict["role"] = "Crew Member"
                    qualifications = []
                    qualifications.append("Advanced Training")
                    qualifications.append("Driver")
                    volunteerDict["qualifications"] = qualifications
                    volunteerDict["contact_info"] = {"type": "phone", "detail": volunteer.phonenumber}
                    VolunteerListDriver.append(volunteerDict)
                else:
                    volunteerDict["volunteer_id"] = volunteer.id
                    volunteerDict["volunteer_name"] = volunteer.name
                    volunteerDict["role"] = "Crew Member"
                    qualifications = []
                    qualifications.append("Basic Training")
                    volunteerDict["qualifications"] = []
                    volunteerDict["contact_info"] = {"type": "phone", "detail": volunteer.phonenumber}
                    VolunteerListBasic.append(volunteerDict)
        position = 1
        VolunteerList = []
        for volunteer in VolunteerListCrewLeader:
            if position == 1:
                if request.AssetType == LightUnit:
                    volunteer["role"] = "CrewLeader/Driver"
                if request.AssetType == HeavyTanker:
                    volunteer["role"] = "CrewLeader"
            if position == 2:
                if request.AssetType == HeavyTanker:
                    volunteer["role"] = "Driver"
            volunteer["position"] = position
            VolunteerList.append(volunteer)
            position = position + 1
        for volunteer in VolunteerListDriver:
            if position == 2:
                if request.AssetType == HeavyTanker:
                    volunteer["role"] = "Driver"
            volunteer["position"] = position
            VolunteerList.append(volunteer)
            position = position + 1
        for volunteer in VolunteerListAdvanced:
            volunteer["position"] = position
            VolunteerList.append(volunteer)
            position = position + 1
        for volunteer in VolunteerListBasic:
            volunteer["position"] = position
            VolunteerList.append(volunteer)
            position = position + 1
        vehicleDict["volunteers"] = VolunteerList
        RecommendationList.append(vehicleDict)

    return RecommendationList, Volunteers

#Test Code
#v = volunteerGenerate(200)
#request = [Request(1,LightUnit, 34, 35)]
#print(Schedule(v, request))
