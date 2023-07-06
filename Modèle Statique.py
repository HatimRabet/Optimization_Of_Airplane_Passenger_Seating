# Modules de base

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from prettytable import PrettyTable
import pickle


# Module relatif à Gurobi
from gurobipy import *

# Module csv
import csv

def optimisation(data_file, time_limit):

    date = data_file[0:-4]

    # Importation et structuration des données

    Passengers = dict() # Dictionnaire qui définit les passagers
    Groupes = dict() # Dictionnaire qui définit les groupes
    M = 0
    B = 0
    Enfants_Y = 0
    Adultes_Y = 0
    Enfants_J = 0
    Adultes_J = 0
    Cap_max = 0

    # Chargement des donnees

    with open(data_file) as DataFile:
        reader = csv.DictReader(DataFile)
        for row in reader:
            d = int(float(row['Numero du groupe']))

            if row["Femmes"] == '': row["Femmes"] = 0
            if row["Hommes"] == '': row["Hommes"] = 0
            if row["Enfants"] == '': row["Enfants"] = 0
            if row["WCHR"] == '': row["WCHR"] = 0
            if row["WCHB"] == '': row["WCHB"] = 0
            if row["TransitTime"][1] == ":" : row["TransitTime"] = "0" + row["TransitTime"]
            if row["TransitTime"][:2] == "12" : row["TransitTime"] = "00" + row["TransitTime"][2:]

            Gcount = int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHR'])) + int(float(row['WCHB']))
            if row['Classe'] == 'Y' :
                Enfants_Y += int(float(row['Enfants']))
                Adultes_Y += int(float(row['Hommes'])) + int(float(row['Femmes']))
            Cap_max = int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + 4*int(float(row['WCHR'])) + 12*int(float(row['WCHB']))

            if row["Classe"] == "J":
                B += int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHR'])) + int(float(row['WCHB']))
                Enfants_J += int(float(row['Enfants']))
                Adultes_J += int(float(row['Hommes'])) + int(float(row['Femmes']))

                
            if int(float(row['Femmes'])) > 0 :
                for i in range(M+1,M+int(float(row['Femmes'])) + 1):
                    Passengers[i] = {"Numero de groupe" : d, "Cardinal du Groupe" : Gcount, "Type": 'Femme', "Classe" : row['Classe'], "TransitTime" : int(row['TransitTime'][:2])*60 + int(row['TransitTime'][3:5])}
            if int(float(row['Hommes'])) > 0 :
                for i in range(M+int(float(row['Femmes'])) + 1,M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + 1):
                    Passengers[i] = {"Numero de groupe" : d, "Cardinal du Groupe" : Gcount, "Type": 'Homme', "Classe" : row['Classe'], "TransitTime" : int(row['TransitTime'][:2])*60 + int(row['TransitTime'][3:5])}
            if int(float(row['Enfants'])) > 0 :
                for i in range(M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + 1,M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + 1):
                    Passengers[i] = {"Numero de groupe" : d, "Cardinal du Groupe" : Gcount, "Type": 'Enfant', "Classe": row['Classe'], "TransitTime" : int(row['TransitTime'][:2])*60 + int(row['TransitTime'][3:5])}
            if int(float(row['WCHB'])) > 0 :
                for i in range(M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + 1,M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHB']))+1):
                    Passengers[i] = {"Numero de groupe" : d, "Cardinal du Groupe" : Gcount, "Type": 'WCHB', "Classe" : row['Classe'], "TransitTime": int(row['TransitTime'][:2])*60 + int(row['TransitTime'][3:5])}
            if int(float(row['WCHR'])) > 0 :
                for i in range(M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHB'])) + 1,M + int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHB'])) + int(float(row['WCHR'])) + 1):
                    Passengers[i] = {"Numero de groupe" : d, "Cardinal du Groupe" : Gcount, "Type": 'WCHR', "Classe" : row['Classe'], "TransitTime": int(row['TransitTime'][:2])*60 + int(row['TransitTime'][3:5])}
            Groupes[d] = [i for i in range(M+1,M+Gcount+1)]      
            M += Gcount

    # Calcul des chiffres utiles pour la modélisation du problème (Les valeurs varient selon la dataset importée)
    # A noter que le nombre de siège peut être insuffisant pour quelques instances, il faut donc augmenter le nombre de rangées

    if data_file == "7Nov.csv" :
        Nb_rows = 35 # Nombre de rangées (de 1 à 35) pour l'avion A321
    else :
        Nb_rows = 29 # Nombre de rangées (de 1 à 29) pour l'avion A320
    Nb_rows2 = 7 # Nombre de colonne (A B C (couloir) D E F), 
    Nb_passengers = M # Nombre de passagers
    Nb_groups = len(Groupes) # Nombre de groupes
    Nb_business_passengers = B # Nombre de passager en cabine Business

    # Dictionnaire pour définir le poids de chaque type de passager

    Poids = {
        "Homme" : 85,
        "Femme" : 70,
        "Enfant" : 35,
        "WCHR" : 100,
        "WCHB" : 95
    }

    # Modèle
    m = Model("Projet ST7")

    occupied_seat = {(i,j,k) : m.addVar(vtype = GRB.BINARY, name=f'x_{i}_{j}_{k}') for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1) for k in range(1, Nb_passengers + 1)}

    X_min = {g : m.addVar(vtype = GRB.INTEGER, lb = 1 , ub = Nb_rows , name=f'X_min({g})') for g in range(1, Nb_groups + 1) if len(Groupes[g]) >= 2}
    X_max = {g : m.addVar(vtype = GRB.INTEGER, lb = 1 , ub = Nb_rows , name=f'X_max({g})') for g in range(1, Nb_groups + 1) if len(Groupes[g]) >= 2}
    Y_min = {g : m.addVar(vtype = GRB.INTEGER, lb = 1 , ub = Nb_rows2 , name=f'Y_min({g})') for g in range(1, Nb_groups + 1) if len(Groupes[g]) >= 2}
    Y_max = {g : m.addVar(vtype = GRB.INTEGER, lb = 1 , ub = Nb_rows2 , name=f'Y_max({g})') for g in range(1, Nb_groups + 1) if len(Groupes[g]) >= 2}

    # Ajout des contraintes 

    # Chaque passager est affecté à un seul siège
    c1 = {k : m.addConstr(quicksum([occupied_seat[(i, j, k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]) == 1, name = f'c1_{k}') for k in range(1, Nb_passengers + 1)}

    # Chaque siège peut être attribué à au plus un passager
    c2 = {(i,j) : m.addConstr(quicksum([occupied_seat[(i, j, k)] for k in range(1, Nb_passengers + 1)]) <= 1, name = f'c2_{(i,j)}') for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)}

    # Contraintes sur les variables X_min, X_max, Y_min, Y_max
    c3_1 = {(g,p) : m.addConstr(X_min[g] <= quicksum([i*occupied_seat[(i,j,Groupes[g][p])] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]), name = f'c3_1{g}') for g in range(1,Nb_groups + 1) for p in range(len(Groupes[g])) if len(Groupes[g]) >= 2}
    c3_2 = {(g,p) : m.addConstr(Y_min[g] <= quicksum([j*occupied_seat[(i,j,Groupes[g][p])] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]), name = f'c3_2{g}') for g in range(1,Nb_groups + 1) for p in range(len(Groupes[g])) if len(Groupes[g]) >= 2}
    c3_3 = {(g,p) : m.addConstr(X_max[g] >= quicksum([i*occupied_seat[(i,j,Groupes[g][p])] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]), name = f'c3_3{g}') for g in range(1,Nb_groups + 1) for p in range(len(Groupes[g])) if len(Groupes[g]) >= 2}
    c3_4 = {(g,p) : m.addConstr(Y_max[g] >= quicksum([j*occupied_seat[(i,j,Groupes[g][p])] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]), name = f'c3_4{g}') for g in range(1,Nb_groups + 1) for p in range(len(Groupes[g])) if len(Groupes[g]) >= 2}

    #Barycentre
    barycentre_x = quicksum([j*Poids[Passengers[k]['Type']]*occupied_seat[(i,j,k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1) for k in range(1, Nb_passengers + 1)])
    barycentre_y = quicksum([i*Poids[Passengers[k]['Type']]*occupied_seat[(i,j,k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1) for k in range(1, Nb_passengers + 1)])
    total_poids = quicksum([Poids[Passengers[k]['Type']] for k in range(1, Nb_passengers + 1)])
    c4=m.addConstr(barycentre_x >= 3*total_poids , name='c4')
    c5=m.addConstr(barycentre_x <= 5*total_poids , name='c5')
    c6=m.addConstr(barycentre_y <= int(Nb_rows/2 + 3)*total_poids , name='c6')
    c7=m.addConstr(barycentre_y >= int(Nb_rows//2 - 1)*total_poids , name='c7')

    # La colonne 4 qui définit le couloir ne peut pas avoir un siège pour un passager
    c8={k :m.addConstr(occupied_seat[(i, 4, k)] == 0, name = f'c8{(k)}') for i in range(1, Nb_rows + 1) for k in range(1, Nb_passengers + 1)} 

    # Ajout de la cabine "Business Class" et affectation des "Passagers Business" dans cette cabine
    business_class = {(i,k): m.addConstr(occupied_seat[(i,2,k)] + occupied_seat[(i,6,k)] == 0, name=f'bs{k}') for i in range(1, Nb_rows + 1) for k in range(1,Nb_passengers + 1) if Passengers[k]["Classe"] == "J"}
    business_passengers = {k : m.addConstr(quicksum([i*occupied_seat[(i,j,k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]) <= Nb_business_passengers//4 + 1, name = f'pb_{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Classe'] == 'J'}
    simple_passengers = {k : m.addConstr(quicksum([i*occupied_seat[(i,j,k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)]) >= Nb_business_passengers//4 + 2, name = f'pb_{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Classe'] == 'Y' and Nb_business_passengers >=1}

    # Les enfants de peuvent pas être à côté des issues de secours
        # Contrainte pour le siège 11A
    A11 = {k: m.addConstr(occupied_seat[(11,1,k)] == 0, name=f'11A{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Type'] == 'Enfant'}
        # Contrainte pour le siège 12A
    A12 = {k: m.addConstr(occupied_seat[(12,1,k)] == 0, name=f'12A{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Type'] == 'Enfant'}
        # Contrainte pour le siège 11F
    F11 = {k: m.addConstr(occupied_seat[(11,7,k)] == 0, name=f'11F{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Type'] == 'Enfant'}
        # Contrainte pour le siège 12F
    F12 = {k: m.addConstr(occupied_seat[(12,7,k)] == 0, name=f'12F{k}') for k in range(1,Nb_passengers + 1) if Passengers[k]['Type'] == 'Enfant'}

    # Placement spécial des passagers en chaise roulante (On considère que tout les passagers en chaise roulante ne sont pas en cabine business)
        # On place les passagers en chaise roulante dans les rangées 3 et 5 pour bloquer le carré à côté d'eux en côté allée
    c9_1 = {k_WCHR: m.addConstr(quicksum([occupied_seat[(i,3,k_WCHR)] + occupied_seat[(i,5,k_WCHR)] for i in range(1, Nb_rows + 1)]) == 1, name = f'c9_1{k_WCHR}') for k_WCHR in range(1,Nb_passengers + 1) if Passengers[k_WCHR]['Type'] == 'WCHR'}
        # Les passagers en chaise roulante ne peuvent pas être placés dans la première ligne dans la cabine économique
    c9_2 = {k_WCHR: m.addConstr(quicksum([i*(occupied_seat[(i,3,k_WCHR)] + occupied_seat[(i,5,k_WCHR)]) for i in range(1, Nb_rows + 1)]) >= (Nb_business_passengers >=1)*(Nb_business_passengers//4 + 3) + (Nb_business_passengers == 0) * 2, name = f'c9_2{k_WCHR}') for k_WCHR in range(1,Nb_passengers + 1) if Passengers[k_WCHR]['Type'] == 'WCHR'}
        # On bloque le carré à côté des passagers en chaise roulante selon leur rangée (à droite si j = 5 et à gauche si j = 3)
    c9_3= {(i,j,k_WCHR): m.addConstr(quicksum([int((j == 5)) * (occupied_seat[i,j+1,k] + occupied_seat[i-1,j+1,k]) + int((j == 3)) * (occupied_seat[i,j-1,k] + occupied_seat[i-1,j-1,k]) + occupied_seat[i-1,j,k] for k in range(1, Nb_passengers + 1) if k != k_WCHR]) <= 3 * (1 - occupied_seat[i,j,k_WCHR]), name = f'c9_3{(i,j,k_WCHR)}') for k_WCHR in range(1, Nb_passengers + 1) for i in range(2, Nb_rows + 1) for j in [3,5] if Passengers[k_WCHR]['Type'] == 'WCHR'}

    # Placement spécial des passagers en civière (On considère que tout les passagers en civière ne sont pas en cabine business)
        # On place les passagers en civière roulante dans les rangées 1 et 4 pour bloquer le carré à côté d'eux en côté allée
    c10_1 = {k_WCHB: m.addConstr(quicksum([occupied_seat[(i,1,k_WCHB)] + occupied_seat[(i,5,k_WCHB)] for i in range(1, Nb_rows + 1)]) == 1, name = f'c10_1{k_WCHB}') for k_WCHB in range(1,Nb_passengers + 1) if Passengers[k_WCHB]['Type'] == 'WCHB'}
        # Les passagers en civière ne peuvent pas être placés dans les 3 premières lignes dans la cabine économique
    c10_2 = {k_WCHB: m.addConstr(quicksum([i*(occupied_seat[(i,1,k_WCHB)] + occupied_seat[(i,5,k_WCHB)]) for i in range(1, Nb_rows + 1)]) >= (Nb_business_passengers >=1)*(Nb_business_passengers//4 + 5) + (Nb_business_passengers == 0) * 4, name = f'c9_2{k_WCHB}') for k_WCHB in range(1,Nb_passengers + 1) if Passengers[k_WCHB]['Type'] == 'WCHB'}
        # On bloque la rangée du passager en civière et les 3 rangées devant lui
    c10_3= {(i,j,k_WCHB): m.addConstr(quicksum([int((j == 1)) * (occupied_seat[(i,j+1,k)] + occupied_seat[(i,j+2,k)] + occupied_seat[(i-1,j+1,k)] + occupied_seat[(i-1,j+2,k)] + occupied_seat[(i-2,j+1,k)] + occupied_seat[(i-2,j+2,k)] + occupied_seat[(i-3,j+1,k)] + occupied_seat[(i-3,j+2,k)]) + int((j == 5)) * (occupied_seat[(i,j+1,k)] + occupied_seat[(i,j+2,k)] + occupied_seat[(i-1,j+1,k)] + occupied_seat[(i-1,j+2,k)] + occupied_seat[(i-2,j+1,k)] + occupied_seat[(i-2,j+2,k)] + occupied_seat[(i-3,j+1,k)] + occupied_seat[(i-3,j+2,k)]) + occupied_seat[(i-1,j,k)] + occupied_seat[(i-2,j,k)] + occupied_seat[(i-3,j,k)] for k in range(1, Nb_passengers + 1) if k != k_WCHB]) <= 11 * (1 - occupied_seat[(i,j,k_WCHB)]), name = f'c10_3{(i,j,k_WCHB)}') for k_WCHB in range(1, Nb_passengers + 1) for i in range(4, Nb_rows + 1) for j in [1,5] if Passengers[k_WCHB]['Type'] == 'WCHB'}

    # Définition de la note enfant

    Note_enfant = 0

    if Enfants_Y >= 1.25 * Adultes_Y :

        z = {(i,j,k) : m.addVar(vtype = GRB.BINARY, name=f'z_{i}{j}{k}')  for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) for k in range(1, Nb_passengers + 1) if Passengers[k]['Type']=='Enfant' }
        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                for j in range(2,Nb_rows2):
                    if Passengers[k]['Type']=='Enfant' and Passengers[k]['Classe'] == 'Y':
                        m.addConstr((1-occupied_seat[i,j,k] + z[i,j,k] >= 0.25*(quicksum(occupied_seat[i,j-1,k1] + occupied_seat[i,j+1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme'))))
                        m.addConstr((z[i,j,k] <= quicksum(occupied_seat[i,j-1,k1] + occupied_seat[i,j+1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                        m.addConstr((z[i,j,k] <= occupied_seat[i,j,k]))

        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                if Passengers[k]['Type']=='Enfant' and Passengers[k]['Classe'] == 'Y':
            
                    m.addConstr((1-occupied_seat[i,1,k] + z[i,1,k] >= 0.25*(quicksum(occupied_seat[i,2,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme'))))
                    m.addConstr((z[i,1,k] <= quicksum(occupied_seat[i,2,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((z[i,1,k] <= occupied_seat[i,1,k]))

        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                if Passengers[k]['Type']=='Enfant' and Passengers[k]['Classe'] == 'Y':

                    m.addConstr((1-occupied_seat[i,Nb_rows2,k] + z[i,Nb_rows2,k] >= 0.25*(quicksum(occupied_seat[i,Nb_rows2-1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme'))))
                    m.addConstr((z[i,Nb_rows2,k] <= quicksum(occupied_seat[i,Nb_rows2-1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((z[i,Nb_rows2,k] <= occupied_seat[i,Nb_rows2,k]))

                

        Note_enfant = quicksum(z[(i,j,k)] for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) for k in range(1,Nb_passengers+1) if Passengers[k]['Type']=='Enfant')


    else : 
        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                for j in range(2,Nb_rows2):
                    if Passengers[k]['Type']=='Enfant' and Passengers[k]['Classe'] == 'Y':
                        m.addConstr(occupied_seat[i,j,k] <= quicksum(occupied_seat[i,j-1,k1] + occupied_seat[i,j+1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme'))

        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                if Passengers[k]['Type'] == 'Enfant' and Passengers[k]['Classe'] == 'Y':
                    m.addConstr((occupied_seat[i,1,k] <= quicksum(occupied_seat[i,2,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((occupied_seat[i,Nb_rows2,k] <=quicksum(occupied_seat[i,Nb_rows2-1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))

    if Enfants_J <= .75 * Adultes_J :
        for i in range(1,Nb_rows+1):
            for k in range(1,Nb_passengers+1):
                if Passengers[k]['Type'] == 'Enfant' and Passengers[k]['Classe'] == 'J':
                    m.addConstr((occupied_seat[i,1,k] <= quicksum(occupied_seat[i,3,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((occupied_seat[i,3,k] <=quicksum(occupied_seat[i,1,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((occupied_seat[i,5,k] <= quicksum(occupied_seat[i,7,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))
                    m.addConstr((occupied_seat[i,7,k] <=quicksum(occupied_seat[i,5,k1] for k1 in range(1,Nb_passengers+1) if Passengers[k1]['Type']=='Homme' or Passengers[k1]['Type']== 'Femme')))

    # Définition de la note du transit
    Note_transit = quicksum([quicksum([i*occupied_seat[(i,j,k)] for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)])/Passengers[k]["TransitTime"] for k in range(1, Nb_passengers +1) if Passengers[k]['TransitTime'] != 0])

    # Définition de la note de la distance
    Note_dist = quicksum([20*(X_max[g] - X_min[g]) + Y_max[g] - Y_min[g] for g in range(1,Nb_groups + 1) if len(Groupes[g]) >= 2])

    # Définition de la fonction objectif
    m.setObjective(100*Note_dist + Note_transit - 20*Note_enfant, GRB.MINIMIZE) 


    m.params.OutputFlag = 0

    # -- Mise à jour du modèle  --
    m.update()

    m.setParam('TimeLimit', time_limit) # Le TimeLimit pourra être plus petit si l'instance est moins compliquée (et plus grand si l'instance est plus compliquée)

    # -- Affichage en mode texte du PL --
    m.display()

    m.optimize()


    # Affichage du résultat

    D={}
    for k in range(1,Nb_passengers+1):
        D[k]=(sum(i*occupied_seat[(i, j, k)].x for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)) ,sum(j*occupied_seat[(i, j, k)].x for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1)))

    A = np.zeros((Nb_rows, Nb_rows2))
    for k in range(1, Nb_passengers+1):
        i , j = D[k]
        A[int(i)-1,int(j)-1] = k

    # Vérification des enfants non isolés
    B = {}

    for k in range(1, Nb_passengers+1):
        i , j = D[k]
        B[int(i),int(j)] = Passengers[k]['Type']

    for i in range(1,Nb_rows+1):
        for j in range(1,Nb_rows2+1):
            if (i,j) not in B:
                B[(i,j)] = 'Vide'

    # create a dictionary to store the seat number of each child
    child_seats = {}
    seat_passengers=B
    # iterate over all passengers
    for k in range(1, Nb_passengers + 1):
        
        # check if the passenger is a child
        if Passengers[k]['Type'] == 'Enfant':
            
            # get the row and column number of the child's seat
            row_num = int(D[k][0])
            col_num = int(D[k][1])
            
            # check if the child is seated next to an adult
            adjacent_seat_found = False
            if Passengers[k]['Classe'] == 'Y':
            
                # check the seat to the left of the child's seat
                if col_num > 1 and seat_passengers[(row_num, col_num - 1)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
                
                # check the seat to the right of the child's seat
                elif col_num < Nb_rows2 and seat_passengers[(row_num, col_num + 1)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
            
                
                # if the child is in the first column, check the seat to the right of the child's seat
                elif col_num == 1 and seat_passengers[(row_num, col_num + 1)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
                
                
                
                # if the child is in the last column, check the seat to the left of the child's seat
                elif col_num == Nb_rows2 and seat_passengers[(row_num, col_num - 1)] in {'Homme', 'Femme'}:
                    adjacent_seat_found =True

            if Passengers[k]['Classe'] == 'J':

                if col_num == 1 and seat_passengers[(row_num, col_num + 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True

                if col_num == 3 and seat_passengers[(row_num, col_num - 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True

                if col_num == 5 and seat_passengers[(row_num, col_num + 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True

                if col_num == 7 and seat_passengers[(row_num, col_num - 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
        
            if adjacent_seat_found==False:
                child_seats[k] = (row_num, col_num)    #seat_passengers[(row_num, col_num)] = Passengers[k]['Type']
                
    # check if all children are seated next to an adult
    if len(child_seats) == 0:
        child_result = "All children are seated next to an adult."
    else:
        child_result = f"{len(child_seats)} children are not seated next to an adult."

    # Vérification de la satisfaction client
    opt_dist = {
        0 : 0,
        1 : 0,
        2 : 1,
        3 : 2,
        4 : 4,
        5 : 5,
        6 : 6,
        7 : 14,
        8 : 14,
        9 : 15,
        10 : 15,
        11 : 16,
        12 : 16,
        13 : 25,
        14 : 25,
        15 : 25,
        16 : 26,
        17 : 26,
        18 : 26,
        19 : 35,
        20 : 35,
        21 : 36,
        22 : 36,
        23 : 36,
        24 : 36
    }
    Note_dist_opt = sum(opt_dist[len(Groupes[g])] for g in range(1, Nb_groups + 1))
    Note_dist_obt = sum([10*(X_max[g].x - X_min[g].x) + Y_max[g].x - Y_min[g].x for g in range(1,Nb_groups + 1) if len(Groupes[g]) >= 2])
    satisfaction_client = f'Client satisfaction is at {round((Note_dist_opt/Note_dist_obt)*100,2)}%.'

    # Sauvegarder les résultats sous format csv
    with open(f"{date} résultat.csv", mode='w', newline='') as fichier_csv:

        # Créer l'objet writer
        writer = csv.writer(fichier_csv)

        # Écrire les en-têtes de colonne
        writer.writerow(['Passager', 'i', 'j'])

        # Écrire les données
        for passager, (i, j) in D.items():
            writer.writerow([passager, i, j])

        # Fermer le fichier
        fichier_csv.close()

    # Sauvegarder les résultats sous formats pickle

    # Ouvrir un fichier en mode binaire
    with open(f'{date}.pkl', 'wb') as fichier:
        # Écrire le dictionnaire dans le fichier
        pickle.dump(D, fichier)

    # Affichage de l'avion
    # Create a figure with a size of 10x10 inches
    fig, ax = plt.subplots(figsize=(10.4, 8 + 2 * (data_file == "7Nov.csv")))

    # Create a rectangle for the aircraft fuselage
    ax.add_patch(plt.Rectangle((10, 0), 70, 10, facecolor='#c2c2c2', edgecolor='black'))
    ax.add_patch(plt.Rectangle((0, 0), 10, 300 + 60*(data_file == "7Nov.csv"), facecolor='#c2c2c2', edgecolor='black'))

    # Dictionnaire des codes couleurs
    code_couleur = {
        "Homme" : 'royalblue',
        "Femme" : 'lightcoral',
        "Enfant" : 'gold',
        "WCHR" : 'sienna',
        "WCHB" : 'darkgreen'
    }

    Seats = ["A","B","C","couloir","D","E","F"]


    # Create rectangles for the seats
    for row in range(1, Nb_rows + 1):
        if row == Nb_business_passengers//4 + 3 and Nb_business_passengers != 0:
            ax.add_patch(plt.Rectangle((10, y-1), 70, 0.5, fill=True,facecolor ='black', edgecolor='black'))

        for col in range(1, Nb_rows2 + 1):
            if (col == 4) or ((col == 2 or col == 6) and row <= Nb_business_passengers//4 + 1 and Nb_business_passengers != 0) :
                continue  # Skip over the aisles and business cabine fake seats
            x = 12 + (col - 1) * 10
            y = 12 + (row - 1) * 10

            if A[row-1 , col-1] == 0 :
                ax.add_patch(plt.Rectangle((x, y), 8, 8, fill=False, edgecolor='black'))
            else :
                ax.add_patch(plt.Rectangle((x, y), 8, 8, fill=True,facecolor =code_couleur[Passengers[A[row-1 , col-1]]['Type']], edgecolor='black'))

            # Plotting the passenger number and there group on the seat
            if A[row-1 , col-1] == 0 :
                plt.text(x + 4, y + 4, " ", ha='center', va='center', fontsize=8)
            else :
                seat_label = f"{int(A[row-1 , col-1])} - {Passengers[A[row-1 , col-1]]['Numero de groupe']}" 
                plt.text(x + 4, y + 4, seat_label, ha='center', va='center', fontsize=8)

    # adding legend
    for index, type in enumerate(code_couleur.keys()):
        ax.add_patch(plt.Rectangle((x + 20, y - 10*index), 8, 8, fill=True,facecolor =code_couleur[type], edgecolor='black'))
        plt.text(x + 30, y - 10*index + 3, type, ha='left', va='center', fontsize=8)

    # adding rectangle to explain the numbers in each seat : Passenger number and Group ID
    ax.add_patch(plt.Rectangle((x + 12.5, y - 70), 25, 8, fill=False, edgecolor='black'))
    plt.text(x + 25, y - 67, "N° passager - N° groupe", ha='center', va='center', fontsize=8)

    # Plotting child results and client satisfaction
    plt.text(x + 28, y - 167, child_result,fontweight='bold', ha='center', va='center', fontsize=8)
    plt.text(x + 28, y - 177, satisfaction_client,fontweight='bold', ha='center', va='center', fontsize=8)



    # Label the rows and columns
    for row in range(1, Nb_rows + 1):
        y = 12 + (row - 1) * 10
        plt.text(5, y + 4, f"Row {row}", ha='center', va='center', fontsize=8)
    for col in range(1, Nb_rows2 + 1):
        if col == 4:
            continue  # Skip over the aisles
        
        x = 12 + (col - 1) * 10
        plt.text(x + 4, 5, Seats[col-1], ha='center', va='center', fontsize=8)

    # Set the limits of the plot and remove the axes
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 310 + 60*(data_file == "7Nov.csv"))
    ax.axis('off')
    # plt.legend(loc='upper right')
    plt.title(date)


    # plt.show()
    fig.savefig(f'{data_file[:-4]} 30mins.png')


L=["21Oct.csv","22Oct.csv","23Oct.csv","24Oct.csv","26Oct.csv","30Oct.csv","2Nov.csv","5Nov.csv","7Nov.csv"]

for date in L:
    optimisation(date, 900)