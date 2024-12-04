
import json
import random
import datetime
import py2sql
from dateutil.relativedelta import relativedelta

AANTAL_JAREN = 5

def __main__():

    # importeer voorbeelddata
    bron_locaties = open('datafiles/locaties.json', 'r', encoding='UTF-8')
    locaties = json.loads(bron_locaties.read())
    bron_autotypen = open('datafiles/autotypen.json', 'r', encoding='UTF-8')
    autotypen = json.loads(bron_autotypen.read())
    bron_accessoires = open('datafiles/accessoires.json', 'r', encoding='UTF-8')
    accessoires = json.loads(bron_accessoires.read())
    bron_automerken = open('datafiles/automerken.json', 'r', encoding='UTF-8')
    automerken = json.loads(bron_automerken.read()) 
    bron_kleuren = open('datafiles/kleuren.json', 'r', encoding='UTF-8')
    kleuren = json.loads(bron_kleuren.read())         
    bron_voornamen = open('datafiles/firstnames.json', 'r', encoding='UTF-8')
    voornamen = json.load(bron_voornamen)
    bron_achternamen = open('datafiles/lastnames.json', 'r', encoding='UTF-8')
    achternamen = json.load(bron_achternamen)    
    bron_kentekens = open('datafiles/kentekens.json', 'r', encoding='UTF-8')
    kentekens = json.load(bron_kentekens)        

    # maak gewicht-lijsten voor random.choices
    autotype_weights = []
    for autotype in autotypen:
        autotype_weights.append(autotype['kans'])
        del autotype['kans']

    locatie_weights = []
    for locatie in locaties:
        locatie_weights.append(locatie['kans'])
        del locatie['kans']

    automerk_weights = []
    for automerk in automerken:
        automerk_weights.append(automerk['kans'])

    kleur_weights = []
    for kleur in kleuren:
        kleur_weights.append(kleur['kans'] )   

    accessoire_weights = []
    for accessoire in accessoires:
        accessoire_weights.append(accessoire['kans'])
        del accessoire['kans']        

    # declareer arrays voor records
    autos = []
    huurcontracten = []
    klanten = []
    wenst_accessoires = []    

    # zet eerste nummers
    autonr = 3333    
    contractnr = 1000000000
    klantnr = 200000  

    # MAAK AUTO'S 

    for kenteken in kentekens:
        autonr = autonr + random.randrange(1,4)
        auto = {}
        auto["autonr"] = autonr
        automerk = random.choices(automerken, weights=automerk_weights, k=1)[0] 
        auto["autotype"] = automerk["autotype"]  
        auto["kenteken"] = kenteken
        auto["automerk"] = automerk["merk"]
        auto["modelnaam"] = automerk["modelnaam"]
        auto["kleur"] = random.choices(kleuren, weights=kleur_weights, k=1)[0]["kleur"] 
        auto["is_elektrisch"] = automerk["is_elektrisch"]
        if(automerk["is_elektrisch"] == 1):
            auto["is_automaat"] = 1
        else:
            auto["is_automaat"] = random.choices((0,1), weights=(9,1), k=1)[0]
        auto["is_in_orde"] = random.choices((0,1), weights=(1,500), k=1)[0]
        autos.append(auto)

        # MAAK HUURCONTRACTEN voor deze auto

        # begin ergens in de afgelopen AANTAL_JAREN 
        startdatum = datetime.date.today() - datetime.timedelta(days=random.randrange(100, AANTAL_JAREN*365))
        locatie = random.choices(locaties, weights=locatie_weights, k=1)[0]["locatiecode"]
        # in 1% van de gevallen stopt deze auto (total loss?) en in 99% komt er een nieuw contract, tot maximaal 50 dagen van nu
        while random.randrange(0,99) > 0 and startdatum != None and startdatum < datetime.date.today() + datetime.timedelta(days=50):
            huurcontract = {}
            contractnr = contractnr + random.randrange(1,3)            
            huurcontract["contractnr"] = contractnr

            # als er nog minder dan 100 klanten zijn, daarna in 20% van de gevallen, maak nieuwe klant
            if len(klanten) < 100 or random.randrange(0,5) > 0:           
                klant = {}
                klantnr = klantnr + random.randrange(2,5)
                huurcontract["klant"] = klantnr
                klant["klantnr"] = klantnr
                klant["voornaam"] = random.choice(voornamen)
                achternaam = random.choice(achternamen)
                tussenvoegselsPositie = achternaam.find(",")
                if (tussenvoegselsPositie > -1):
                    klant["tussenvoegsels"] = achternaam[tussenvoegselsPositie+2:]
                    klant["achternaam"] = achternaam[0:tussenvoegselsPositie]                
                else:
                    klant["tussenvoegsels"] = None
                    klant["achternaam"] = achternaam          
                klant["emailadres"] = None
                klanten.append(klant)
            else:
                # kies ander een willekeurige bestaande klant
                huurcontract["klant"] = random.choice(klanten)["klantnr"]

            huurcontract["van_datum"] = startdatum
            # als de startdatum minder dag 50 dagen van vandaag is dan in 5% van de gevallen geen einddatum bekend
            if random.randrange(0,20) == 0 and startdatum > datetime.date.today() - datetime.timedelta(days=50):
                huurcontract["tot_datum"] = None
            else:
                # en anders een contractduur tussen 1 en 10 dagen??
                huurcontract["tot_datum"] = startdatum + datetime.timedelta(days=random.choices(range(1,50), weights=range(50,1,-1), k=1)[0])
            huurcontract["locatie_ophalen"] = locatie

            if(random.randrange(0,2) == 0): # in 50% van de contracten is terugbrengelocatie hetzelfde als ophaallocatie
                huurcontract["locatie_terugbrengen"] = huurcontract["locatie_ophalen"]
            else:
                # en anders een willekeurige locaties, op basis van kans
                huurcontract["locatie_terugbrengen"] = random.choices(locaties, weights=locatie_weights, k=1)[0]["locatiecode"] 

            # contractwensen matchen altijd met auto                
            huurcontract["wenst_autotype"] = auto["autotype"]            
            huurcontract["wenst_automaat"] = auto["is_automaat"]
            huurcontract["wenst_elektrisch"] = auto["is_elektrisch"]

            # alle huurcontracten die zijn gestart/starten binnen een week na nu hebben een auto toegewezen
            if(huurcontract["van_datum"] < datetime.date.today() + datetime.timedelta(days=7)):
                huurcontract["krijgt_auto"] = auto["autonr"]
                huurcontract["is_betaald"] = random.choices((0,1), weights=(1,99), k=1)[0]  # maar nog niet altijd betaald
            else:
                # nieuwe contracten hebben nog geen auto toegewezen gekregen
                huurcontract["krijgt_auto"] = None                
                huurcontract["is_betaald"] = random.choices((0,1), weights=(5,5), k=1)[0] # soms al wel betaald

            # alle contracten zonder einddatum zijn ook nog niet betaald    
            if huurcontract["tot_datum"]  == None:
                huurcontract["is_betaald"] = 0

            huurcontracten.append(huurcontract)

            # ACCESSOIRES VOOR DIT CONTRACT
            huurcontract_wenst_accessoires = []
            for accessoire in random.choices(accessoires, weights=accessoire_weights, k=random.choices(range(0,3), weights=range(4,1,-1), k=1)[0]):
                if accessoire["accessoirenaam"] not in huurcontract_wenst_accessoires:
                    wenst_accessoire = {}
                    wenst_accessoire["huurcontract"] = huurcontract["contractnr"]
                    wenst_accessoire["accessoire"] = accessoire["accessoirenaam"]
                    wenst_accessoire["aantal"] = random.randint(1,accessoire["max"])  
                    huurcontract_wenst_accessoires.append(wenst_accessoire["accessoire"])            
                    wenst_accessoires.append(wenst_accessoire)

            # geen nieuwe contracten voor deze auto als dit het laatste contract is
            if huurcontract["tot_datum"] == None:
                startdatum = None
            else:
                # en anders 1 tot 10 dagen tussen deze en het volgende contract in de zomer, anders  10 to 20 dagen
                if 4 < huurcontract["tot_datum"].month < 9:
                    startdatum = huurcontract["tot_datum"] + datetime.timedelta(days=random.randrange(1,9))
                else:
                    startdatum = huurcontract["tot_datum"] + datetime.timedelta(days=random.randrange(8,20))

            # de auto kan worden opgehaald op de laatste terugbrenglocaties (we gaan geen auto's verplaatsen)    
            locatie = huurcontract["locatie_terugbrengen"]

    # verwijder attributen        
    for accessoire in accessoires:
        del accessoire['max'] 

    # GENEREER INSERTS
    file = open("inserts.sql", "w", encoding = 'UTF-8')
    file.write("SET NOCOUNT ON\ngo\n")  


    print ("Locatie: ", py2sql.list2sql2file('Locatie', locaties, file))    
    print ("Autotype: ", py2sql.list2sql2file('Autotype', autotypen, file))  
    print ("Auto: ", py2sql.list2sql2file('Auto', autos, file))         
    print ("Accessoires: ", py2sql.list2sql2file('Accessoire', accessoires, file)) 
    print ("Klanten: ", py2sql.list2sql2file('Klant', klanten, file))     
    print ("Huurcontracten: ", py2sql.list2sql2file('Huurcontract', huurcontracten, file))
    print ("Wenst accessoires: ", py2sql.list2sql2file('Wenst_accessoire', wenst_accessoires, file))


    file.close()   
  
def tupels2dicts(name, listOfTupels):
    list = []
    for tupel in listOfTupels:
        mydict = {name: tupel}
        list.append(mydict)
    return list

__main__()

