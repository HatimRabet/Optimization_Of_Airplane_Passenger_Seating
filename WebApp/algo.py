import pickle
import csv
import numpy as np
def main(numbr_grp,Liste):
    def Note_enfant(D, Nb_enfants, Nb_rows2, Nb_rows, Passengers, Nb_passengers):
        seat_passengers = {}
        for k in range(1, Nb_passengers+1):
            i = D[k][0]
            j = D[k][1]
            seat_passengers[int(i), int(j)] = Passengers[k]['Type']

        for i in range(1, Nb_rows+1):
            for j in range(1, Nb_rows2+1):
                if (i, j) not in seat_passengers:
                    seat_passengers[(i, j)] = 'Vide'
        # create a dictionary to store the seat number of each child
        child_seats = {}
        s = 0
        # iterate over all passengers
        for k in range(1, Nb_passengers + 1):
            # check if the passenger is a child
            if Passengers[k]['Type'] == 'Enfant' and Passengers[k]['Classe'] == 'Y':
                # get the row and column number of the child's seat
                row_num = int(D[k][0])
                col_num = int(D[k][1])
            # check if the child is seated next to an adult
                adjacent_seat_found = False
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
                    adjacent_seat_found = True
                if adjacent_seat_found == False:
                    s = s+1
                # seat_passengers[(row_num, col_num)] = Passengers[k]['Type']
                    child_seats[k] = (row_num, col_num)
    # check if all children are seated next to an adult
        for k in range(1, Nb_passengers + 1):
            # check if the passenger is a child
            if Passengers[k]['Type'] == 'Enfant' and Passengers[k]['Classe'] == 'J':
                # get the row and column number of the child's seat
                row_num = int(D[k][0])
                col_num = int(D[k][1])
            # check if the child is seated next to an adult
                adjacent_seat_found = False
            # check the seat to the left of the child's seat
                if col_num > 1 and seat_passengers[(row_num, col_num - 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
            # check the seat to the right of the child's seat
                elif col_num < Nb_rows2 and seat_passengers[(row_num, col_num + 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
            # if the child is in the first column, check the seat to the right of the child's seat
                elif col_num == 1 and seat_passengers[(row_num, col_num + 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
            # if the child is in the last column, check the seat to the left of the child's seat
                elif col_num == Nb_rows2 and seat_passengers[(row_num, col_num - 2)] in {'Homme', 'Femme'}:
                    adjacent_seat_found = True
                if adjacent_seat_found == False:
                    s = s+1
                # seat_passengers[(row_num, col_num)] = Passengers[k]['Type']
                    child_seats[k] = (row_num, col_num)
    # check if all children are seated next to an adult
        if len(child_seats) == 0:
            Note_enfant = 1
        else:
            Note_enfant = 1-s/Nb_enfants
        return Note_enfant
    # Note_transit


    def Note_Transit(D, Nb_passengers, Passengers):
        s = 0
        for k in range(1, Nb_passengers+1):
            if Passengers[k]['Classe'] != 'Y':
                if Passengers[k]['TransitTime'] != 0:
                    i = D[k][0]
                    s += i/Passengers[k]['TransitTime']
        return(s)

    # Note_barycentre
    def Note_Barycentre(D, Nb_rows, Nb_rows2, Passengers, Poids, Nb_passengers):
        Plane = np.zeros((29,7))
        for k in D.keys():
            i,j = D[k]
            Plane[int(i-1),int(j-1)] = k
        
        barycentre_x = sum([j*Poids[Passengers[Plane[i-1, j-1]]['Type']]for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1) if Plane[i-1, j-1] != 0])
        barycentre_y = sum([i*Poids[Passengers[Plane[i-1, j-1]]['Type']]for i in range(1, Nb_rows + 1) for j in range(1, Nb_rows2 + 1) if Plane[i-1, j-1] != 0])
        total_poids = sum([Poids[Passengers[k]['Type']]for k in range(1, Nb_passengers + 1)])
        return (barycentre_x >= 3*total_poids) and (barycentre_x <= 4*total_poids) and (barycentre_y <= (Nb_rows-2)*total_poids) and (barycentre_y >= (Nb_rows)+2*total_poids)


    # Note Distance 
    def note_dist(D,Groupes):
        Y1={}
        Y2={}
        X1={}
        X2={}
        for g in Groupes.keys():
            Y1[g]= max(D[Groupes[g][s]][1] for s in range(len(Groupes[g])))
            Y2[g]= min(D[Groupes[g][s]][1] for s in range(len(Groupes[g])))
            X1[g]= max(D[Groupes[g][s]][0] for s in range(len(Groupes[g])))
            X2[g]= min(D[Groupes[g][s]][0] for s in range(len(Groupes[g])))
        return sum(8*(X1[g]-X2[g]) + Y1[g]-Y2[g] for g in Y1.keys())

    data_file = "21Oct.csv"
    # data_file = "21Oct.csv"


    Passengers = dict() # Dictionnaire qui définit les passagers
    Groupes = dict() # Dictionnaire qui définit les groupes
    M = 0
    B1 = 0
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
                B1 += int(float(row['Femmes'])) + int(float(row['Hommes'])) + int(float(row['Enfants'])) + int(float(row['WCHR'])) + int(float(row['WCHB']))
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

        
    # Dictionnaires pour calculer le nombre d'enfants et d'adultes (Hommes + Femmes) dans chaque groupe

    Nb_Enfants1 = dict() # Nombre d'enfants dans chaque groupe
    Nb_Adultes = dict() # Nombre d'adultes dans chaque groupe

    for g in range(1, len(Groupes) + 1):
        e = 0
        a = 0
        for p in range(len(Groupes[g])):
            if Passengers[Groupes[g][p]]['Type'] == 'Enfant':
                e +=1
            elif Passengers[Groupes[g][p]]['Type'] == 'Homme' or Passengers[Groupes[g][p]]['Type'] == 'Femme':
                a +=1
        Nb_Enfants1[g] = e
        Nb_Adultes[g] = a   
    # Calcul des chiffres utiles pour la modélisation du problème (Les valeurs varient selon la dataset importée)
    # A noter que le nombre de siège peut être insuffisant pour quelques instances, il faut donc augmenter le nombre de rangées

    Nb_rows = 29 # Nombre de rangées (de 1 à 29)
    Nb_rows2 = 7 # Nombre de colonne (A B C (couloir) D E F), 
    Nb_passengers = M # Nombre de passagers
    Nb_groups = len(Groupes) # Nombre de groupes
    Nb_business_passengers = B1 # Nombre de passager en cabine Business
    Nb_Enfants = sum(Nb_Enfants1[g] for g in Nb_Enfants1.keys())

    filename = '21Oct.pkl'
    
    # Load the dictionary from the file
    with open(filename, 'rb') as f:
        D = pickle.load(f)
    Poids = {
        "Homme" : 85,
        "Femme" : 70,
        "Enfant" : 35,
        "WCHR" : 100,
        "WCHB" : 95
    }

    def Verification_solution(D_opti,D,Nb_rows,Nb_rows2,Passengers,Poids,Nb_passengers,Nb_enfants, Groupes):
        business = {(i,j) :Passengers[int(D_opti[i-1,j-1])]['Classe'] ==  'J' for i in range(1,Nb_business_passengers//4 +2) for j in {1,3,5,7} if Nb_business_passengers >0 and int(D_opti[i-1,j-1]) >0}
        business2 = {(i,j):int(D_opti[i-1,j-1]) == None for i in range(1,Nb_business_passengers//4 +2) for j in {2,4,6} if Nb_business_passengers >0 and int(D_opti[i-1,j-1]) >0}
        normal = {(i,j) : Passengers[int(D_opti[i-1,j-1])]['Classe'] ==  'Y' for i in range(Nb_business_passengers//4 +2,Nb_rows+1) for j in {1,2,3,5,6,7} if int(D_opti[i-1,j-1]) >0}
        normal2 = {i: int(D_opti[i-1,3]) == 0 for i in range(Nb_business_passengers//4 +2,Nb_rows+1) }
        if int(D_opti[10,0]) >0:
            enfant1 = (Passengers[int(D_opti[10,0])] != 'Enfant')
        else :
            enfant1= True
        if int(D_opti[10,6]) >0 :
            enfant2 = (Passengers[int(D_opti[10,6])] != 'Enfant' )
        else: 
            enfant2 =True
        if int(D_opti[11,0]) >0:
            enfant3 = (Passengers[int(D_opti[11,0])] != 'Enfant' )
        else:
            enfant3=True
        if int(D_opti[11,6]) >0:
            enfant4 = (Passengers[int(D_opti[11,6])] != 'Enfant' )
        else:
            enfant4=True
        

        
        WCHR={(i,j): D_opti[i-2,j-1] == None and D_opti[i-2,j-2] == None and D_opti[i-1,j-2]==None  for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if int(D_opti[i-1,j-1]) >0 if Passengers[int(D_opti[i-1,j-1])]['Type']== 'WCHR' and j == 3 }
        WCHR2={(i,j): D_opti[i-2,j-1] == None and D_opti[i-2,j] == None and D_opti[i-1,j]==None  for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if int(D_opti[i-1,j-1]) >0 if Passengers[int(D_opti[i-1,j-1])]['Type']== 'WCHR' and j == 5}
        WCHR3={(i,j): j==3 or j==5 for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if int(D_opti[i-1,j-1]) >0  if Passengers[int(D_opti[i-1,j-1])]['Type']== 'WCHR' }

        WCHB={(i,j): D_opti[i-1,j] == None and D_opti[i-1,j+1] == None  and D_opti[i-2,j-1] == None and D_opti[i-2,j] == None and D_opti[i-2,j+1]==None and D_opti[i-3,j-1] == None and D_opti[i-3,j] == None and D_opti[i-3,j+1]==None and D_opti[i-4,j-1] == None and D_opti[i-4,j] == None and D_opti[i-4,j+1]==None for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if int(D_opti[i-1,j-1]) >0  if Passengers[int(D_opti[i-1,j-1])]['Type']== 'WCHB' and (j == 1 or j==5)}
        
        WCHB2={(i,j): j==1 or j==5 for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if int(D_opti[i-1,j-1]) >0  if Passengers[int(D_opti[i-1,j-1])]['Type']== 'WCHR' }
        
        T=True
        for v in business.keys():
            if business[v]==False:
                T=False 
                break
        for v in business2.keys():
            if business2[v]==False:
                T=False 
                break
        for v in normal.keys():
            if normal[v]==False:
                T=False 
                break
        for v in normal2.keys():
            if normal2[v]==False:
                T=False 
                break
        for v in WCHR.keys():
            if WCHR[v]==False:
                T=False 
                break
        for v in WCHR2.keys():
            if WCHR2[v]==False:
                T=False 
                break
        for v in WCHR3.keys():
            if WCHR3[v]==False:
                T=False 
                break
        for v in WCHB.keys():
            if WCHB[v]==False:
                T=False 
                break
        for v in WCHB2.keys():
            if WCHB2[v]==False:
                T=False 
                break
        A={}
        A_opti={}
        for i in range(1,Nb_rows+1):
            for j in range(1,Nb_rows2+1):
                A[int(D[i-1,j-1])] = (i,j)
                A_opti[(D_opti[i-1,j-1])] = (i,j)

        a=Note_Barycentre(A,Nb_rows,Nb_rows2,Passengers,Poids,Nb_passengers)
        b=(Note_enfant(A_opti, Nb_enfants, Nb_rows2, Nb_rows,Passengers, Nb_passengers)-Note_enfant(A, Nb_enfants, Nb_rows2, Nb_rows,Passengers, Nb_passengers))<=0.2*Note_enfant(A_opti, Nb_enfants, Nb_rows2, Nb_rows,Passengers, Nb_passengers)
        c=(Note_Transit(A_opti,Nb_passengers, Passengers)-Note_Transit(D,Nb_passengers, Passengers))<=0.2*Note_Transit(A_opti,Nb_passengers, Passengers)
        d=(note_dist(A_opti,Groupes)-note_dist(A,Groupes))<=0.2*note_dist(A,Groupes)
        return(a and b and c and d and T and enfant1 and enfant2 and enfant3 and enfant4)
    def notequal(V1,V2):
        for v in V1 :
            if v not in V2 :
                return True
        for v in V2 :
            if v not in V1 :
                return True
        return False
    def sousliste(L,n):
        assert n <= len(L)
        sublists = []
        for i in range(len(L) - n + 1):
            sublists.append(L[i:i+n])
        return sublists
        
    def voisinage(n,Liste_Tabou1):
        A=[]
        
        Seats=[(i,j) for i in range(1,Nb_rows+1) for j in range(1,Nb_rows2+1) if (j != 4 and (i,j) not in Liste_Tabou1) ]
        
        Result=sousliste(Seats,n)
        Result2=[]
        
        for v in Result : 
            if max(v[k][0] for k in range(n)) - min(v[k][0] for k in range(len(v))) <= n//3 - (n== (n//3)*3)  :
                if max(v[k][1] for k in range(n)) - min(v[k][1] for k in range(len(v))) <= n - 1   :
                    Result2.append(v)
        


        return Result2
    def permutation(list1,list2,Plane):
        New_plane = Plane.copy()
        compteur = 0
        for n in range(len(list1)):
            for m in range(len(list2)):
                if list1[n][2]==list2[m][2]:
                    if n==m:
                        pass
                    else :
                        list2[n], list2[m] = list2[m], list2[n]
        list2_seats = [(D[0],D[1]) for D in list2]
        list1_seats = [(D[0],D[1]) for D in list1] 
        for k in range(len(list1_seats)):
            temp = list1_seats[k]
            list1_seats[k]=  list2_seats[k]
            list2_seats[k]=temp
    
        for k in range(len(list1)) :
            New_plane[list1_seats[k][0]-1,list1_seats[k][1]-1] = list1[k][2]
            New_plane[list1[k][0]-1,list1[k][1]-1] = list2[k][2]
        
        return New_plane
        
        
    def admissible(New_plane,Plane,Nb_rows,Nb_rows2,Passengers,Poids,Nb_passengers,Nb_enfants, Groupes):
        return Verification_solution(New_plane,Plane,Nb_rows,Nb_rows2,Passengers,Poids,Nb_passengers,Nb_enfants, Groupes)
    #Créer une liste de triplets (i,j,k) en ayant l'avion et les positions

    def positions_add_passenger(positions, Plane):
        seat_passenger = []
        compteur = 0
        for T in positions:
            seat_passenger.append((T[0],T[1],Plane[T[0]-1,T[1]-1]))
        return seat_passenger
    def possible_permutation(groupe, positions, Plane,Liste_Tabou1):
        n = len(Groupes[groupe])
        Choices = []
        for V in voisinage(n,Liste_Tabou1):
            list1 = positions_add_passenger(positions, Plane)
            list2 = positions_add_passenger(V, Plane)
            New_plane = permutation(list1, list2, Plane)
            if admissible(New_plane, Plane, Nb_rows,Nb_rows2,Passengers, Poids,Nb_passengers,Nb_Enfants, Groupes):
                Choices.append(V)

        return Choices
    def get_group_seats(numero_grp,Plane):
        groupe = [k for k in D.keys() if Passengers[k]['Numero de groupe'] == numero_grp]
        seats = []
        for k in groupe:
            i,j = 0,0
            for i0 in range(0,Nb_rows):
                for j0 in range(0,Nb_rows2):
                    if int(Plane[i0,j0]) == k:
                        i,j= i0,j0
            seats.append((i+1,j+1))
        return seats

    def Plane_(A):
        Plane = np.zeros((29,7))
        for k in A.keys():
            i,j = A[k]
            Plane[int(i-1),int(j-1)] = k
        return Plane



    def get_seats(numbr_grp,Liste):
        Liste_Tabou =Liste
        filename = '21Oct.pkl'
    
    # Load the dictionary from the file
        with open(filename, 'rb') as f:
            D = pickle.load(f)
        D=dict(D)

        Plane = Plane_(D)

        groupe,positions = int(numbr_grp),get_group_seats(int(numbr_grp),Plane)

        seat_proposals = possible_permutation(groupe,positions,Plane,Liste_Tabou)

        seats_formatted = [str(seat[0][0])+str(chr(ord('A')+seat[0][1]-1)) for seat in seat_proposals]
        seats_unpermitted = [str(i)+str(chr(ord('A')+j-1)) for i in range(1,29) for  j in range(1,8) if str(i)+str(chr(ord('A')+j-1)) not in seats_formatted]
        #print(seats_unpermitted)
        print(Liste_Tabou)
        return seats_unpermitted
        
    return get_seats(numbr_grp,Liste)