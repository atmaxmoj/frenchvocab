import json

data = [
{"id":6444,"qs":[
 {"slot":"s|0","f":"sense","s":"Le nouveau serveur mettait un tel ___ à satisfaire les clients qu'on le remarquait tout de suite.","a":"empressement","en":"The new waiter showed such eagerness and attentiveness in pleasing the customers that people noticed him right away.","alts":[]},
 {"slot":"s|0","f":"sense","s":"Dès son arrivée, il fut entouré d'un ___ chaleureux de la part de toute la famille.","a":"empressement","en":"As soon as he arrived, he was surrounded by warm attentiveness and eagerness from the whole family.","alts":[]},
 {"slot":"s|1","f":"sense","s":"Les candidats déposèrent leur dossier avec un ___ qui trahissait leur crainte de rater la date limite.","a":"empressement","en":"The candidates submitted their file with such haste and eagerness that it betrayed their fear of missing the deadline.","alts":[]},
 {"slot":"s|1","f":"sense","s":"À l'annonce de la promotion, les clients se sont rués vers le magasin avec un ___ inhabituel.","a":"empressement","en":"At the announcement of the promotion, customers rushed to the store with unusual alacrity.","alts":[]},
 {"slot":"gender","f":"gender","s":"Il montra ___ empressement remarquable pour aider ses collègues.","a":"un","en":"He showed remarkable eagerness to help his colleagues.","alts":[]},
 {"slot":"gender","f":"gender","s":"Nous avons apprécié ___ empressement dont il a fait preuve.","a":"l'","en":"We appreciated the eagerness he displayed.","alts":[]}
]},
{"id":6445,"qs":[
 {"slot":"s|0","f":"sense","s":"Le patrimoine culturel ___ comprend les traditions orales et les savoir-faire artisanaux.","a":"immatériel","en":"Intangible cultural heritage includes oral traditions and craft know-how.","alts":[]},
 {"slot":"s|0","f":"sense","s":"Le capital ___ d'une entreprise, comme sa réputation, est difficile à chiffrer.","a":"immatériel","en":"A company's intangible capital, like its reputation, is hard to quantify.","alts":[]},
 {"slot":"s|1","f":"sense","s":"Pour les mystiques, le monde ___ est aussi réel que le monde physique.","a":"immatériel","en":"For mystics, the immaterial world is just as real as the physical world.","alts":[]},
 {"slot":"s|1","f":"sense","s":"En théologie, on affirme que Dieu est un être purement ___.","a":"immatériel","en":"In theology, it is affirmed that God is a purely immaterial being.","alts":[]},
 {"slot":"g|mp","f":"agree","s":"Les brevets et les logiciels sont des biens ___.","a":"immatériels","en":"Patents and software are intangible goods.","alts":[]},
 {"slot":"g|mp","f":"agree","s":"Ces actifs ___ représentent une grande partie de la valeur de l'entreprise.","a":"immatériels","en":"These intangible assets represent a large part of the company's value.","alts":[]},
 {"slot":"g|f","f":"agree","s":"Cette œuvre d'art numérique est entièrement ___.","a":"immatérielle","en":"This digital artwork is entirely immaterial.","alts":[]},
 {"slot":"g|f","f":"agree","s":"Selon lui, l'âme humaine est ___ et éternelle.","a":"immatérielle","en":"According to him, the human soul is immaterial and eternal.","alts":[]},
 {"slot":"g|fp","f":"agree","s":"Les données stockées dans le cloud sont ___, mais bien réelles.","a":"immatérielles","en":"Data stored in the cloud are intangible, but very real.","alts":[]},
 {"slot":"g|fp","f":"agree","s":"Ces traditions ___ font partie du patrimoine de l'UNESCO.","a":"immatérielles","en":"These intangible traditions are part of UNESCO's heritage.","alts":[]}
]},
{"id":6446,"qs":[
 {"slot":"t|Présent|0","f":"tense","form":"Présent","s":"Grâce au GPS, je ___ facilement ma voiture sur le parking.","a":"localise","en":"Thanks to GPS, I easily locate my car in the parking lot.","alts":[]},
 {"slot":"t|Présent|0","f":"tense","form":"Présent","s":"Cette application ___ précisément la position du téléphone volé.","a":"localise","en":"This app precisely locates the position of the stolen phone.","alts":[]},
 {"slot":"t|Présent|1","f":"tense","form":"Présent","s":"Avec cette carte, tu ___ rapidement le village sur la route.","a":"localises","en":"With this map, you quickly locate the village on the road.","alts":[]},
 {"slot":"t|Présent|1","f":"tense","form":"Présent","s":"Tu ___ le signal GPS avant de partir en randonnée.","a":"localises","en":"You locate the GPS signal before setting off on a hike.","alts":[]},
 {"slot":"t|Présent|2","f":"tense","form":"Présent","s":"Nous ___ l'origine de la panne électrique dans le bâtiment.","a":"localisons","en":"We locate the source of the power outage in the building.","alts":[]},
 {"slot":"t|Présent|2","f":"tense","form":"Présent","s":"Chaque matin, nous ___ la position des camions de livraison sur l'écran.","a":"localisons","en":"Every morning, we locate the position of the delivery trucks on the screen.","alts":[]},
 {"slot":"t|Présent|3","f":"tense","form":"Présent","s":"Vous ___ le signal du navire en quelques secondes.","a":"localisez","en":"You locate the ship's signal within a few seconds.","alts":[]},
 {"slot":"t|Présent|3","f":"tense","form":"Présent","s":"Dans ce logiciel, vous ___ facilement l'adresse IP suspecte.","a":"localisez","en":"In this software, you easily locate the suspicious IP address.","alts":[]},
 {"slot":"t|Présent|4","f":"tense","form":"Présent","s":"Les techniciens ___ la fuite d'eau sous la rue.","a":"localisent","en":"The technicians locate the water leak under the street.","alts":[]},
 {"slot":"t|Présent|4","f":"tense","form":"Présent","s":"Ces capteurs ___ précisément les mouvements sismiques.","a":"localisent","en":"These sensors precisely locate seismic movements.","alts":[]},
 {"slot":"t|Passé composé|0","f":"tense","form":"Passé composé","s":"Hier soir, j'___ mon téléphone perdu grâce à une application de suivi.","a":"ai localisé","en":"Last night, I located my lost phone thanks to a tracking app.","alts":[]},
 {"slot":"t|Passé composé|0","f":"tense","form":"Passé composé","s":"La semaine dernière, j'___ enfin l'origine du bug dans le code.","a":"ai localisé","en":"Last week, I finally located the source of the bug in the code.","alts":[]},
 {"slot":"t|Passé composé|1","f":"tense","form":"Passé composé","s":"Tu ___ le colis grâce au numéro de suivi.","a":"as localisé","en":"You located the package thanks to the tracking number.","alts":[]},
 {"slot":"t|Passé composé|1","f":"tense","form":"Passé composé","s":"Tu ___ rapidement la voiture volée hier.","a":"as localisé","en":"You quickly located the stolen car yesterday.","alts":[]},
 {"slot":"t|Passé composé|2","f":"tense","form":"Passé composé","s":"Le technicien ___ la panne en dix minutes.","a":"a localisé","en":"The technician located the fault in ten minutes.","alts":[]},
 {"slot":"t|Passé composé|2","f":"tense","form":"Passé composé","s":"Elle ___ le signal de détresse envoyé par le bateau.","a":"a localisé","en":"She located the distress signal sent by the boat.","alts":[]},
 {"slot":"t|Passé composé|3","f":"tense","form":"Passé composé","s":"Nous ___ l'épicentre du séisme grâce aux capteurs.","a":"avons localisé","en":"We located the epicenter of the earthquake thanks to the sensors.","alts":[]},
 {"slot":"t|Passé composé|3","f":"tense","form":"Passé composé","s":"Hier, nous ___ enfin le studio de notre amie à Paris.","a":"avons localisé","en":"Yesterday, we finally located our friend's studio apartment in Paris.","alts":[]},
 {"slot":"t|Passé composé|4","f":"tense","form":"Passé composé","s":"Vous ___ le véhicule volé en consultant les caméras.","a":"avez localisé","en":"You located the stolen vehicle by checking the cameras.","alts":[]},
 {"slot":"t|Passé composé|4","f":"tense","form":"Passé composé","s":"Vous ___ rapidement la fuite de gaz dans l'immeuble.","a":"avez localisé","en":"You quickly located the gas leak in the building.","alts":[]},
 {"slot":"t|Passé composé|5","f":"tense","form":"Passé composé","s":"Les secouristes ___ les randonneurs perdus grâce à leur portable.","a":"ont localisé","en":"The rescuers located the lost hikers thanks to their cell phone.","alts":[]},
 {"slot":"t|Passé composé|5","f":"tense","form":"Passé composé","s":"Elles ___ enfin l'erreur dans le programme informatique.","a":"ont localisé","en":"They finally located the error in the computer program.","alts":[]},
 {"slot":"t|Imparfait|0","f":"tense","form":"Imparfait","s":"Avant l'invention du GPS, je ___ les villages à l'aide d'une carte papier.","a":"localisais","en":"Before the invention of GPS, I used to locate villages with a paper map.","alts":[]},
 {"slot":"t|Imparfait|0","f":"tense","form":"Imparfait","s":"Quand tu étais enfant, tu ___ toujours les étoiles avec ce livre d'astronomie.","a":"localisais","en":"When you were a child, you always used to locate the stars with this astronomy book.","alts":[]},
 {"slot":"t|Imparfait|1","f":"tense","form":"Imparfait","s":"À cette époque, le radar ___ les avions avec moins de précision.","a":"localisait","en":"At that time, the radar located planes with less precision.","alts":[]},
 {"slot":"t|Imparfait|1","f":"tense","form":"Imparfait","s":"Elle ___ souvent les objets perdus grâce à son sens de l'orientation.","a":"localisait","en":"She often located lost objects thanks to her sense of direction.","alts":[]},
 {"slot":"t|Imparfait|2","f":"tense","form":"Imparfait","s":"Autrefois, nous ___ les navires uniquement par radio.","a":"localisions","en":"In the past, we used to locate ships only by radio.","alts":[]},
 {"slot":"t|Imparfait|2","f":"tense","form":"Imparfait","s":"Chaque été, nous ___ le camping grâce aux panneaux indicateurs.","a":"localisions","en":"Every summer, we used to locate the campsite thanks to the road signs.","alts":[]},
 {"slot":"t|Imparfait|3","f":"tense","form":"Imparfait","s":"Avant cette mise à jour, vous ___ les erreurs manuellement.","a":"localisiez","en":"Before this update, you used to locate the errors manually.","alts":[]},
 {"slot":"t|Imparfait|3","f":"tense","form":"Imparfait","s":"À l'époque, vous ___ vos employés uniquement par téléphone.","a":"localisiez","en":"Back then, you used to locate your employees only by phone.","alts":[]},
 {"slot":"t|Imparfait|4","f":"tense","form":"Imparfait","s":"Les marins ___ leur position grâce aux étoiles avant l'invention du GPS.","a":"localisaient","en":"Sailors used to locate their position using the stars before the invention of GPS.","alts":[]},
 {"slot":"t|Imparfait|4","f":"tense","form":"Imparfait","s":"Ces vieux appareils ___ les signaux avec beaucoup de retard.","a":"localisaient","en":"These old devices used to locate signals with a lot of delay.","alts":[]},
 {"slot":"t|Futur|0","f":"tense","form":"Futur","s":"Demain, je ___ la source du problème avec ce nouvel outil.","a":"localiserai","en":"Tomorrow, I will locate the source of the problem with this new tool.","alts":[]},
 {"slot":"t|Futur|0","f":"tense","form":"Futur","s":"Dès que j'aurai le logiciel, je ___ facilement mon colis.","a":"localiserai","en":"As soon as I have the software, I will easily locate my package.","alts":[]},
 {"slot":"t|Futur|1","f":"tense","form":"Futur","s":"Avec cette application, tu ___ ton ami en quelques secondes.","a":"localiseras","en":"With this app, you will locate your friend in a few seconds.","alts":[]},
 {"slot":"t|Futur|1","f":"tense","form":"Futur","s":"Demain matin, tu ___ le camion de déménagement grâce au traceur.","a":"localiseras","en":"Tomorrow morning, you will locate the moving truck thanks to the tracker.","alts":[]},
 {"slot":"t|Futur|2","f":"tense","form":"Futur","s":"Le nouveau système ___ automatiquement chaque appareil connecté.","a":"localisera","en":"The new system will automatically locate every connected device.","alts":[]},
 {"slot":"t|Futur|2","f":"tense","form":"Futur","s":"On ___ facilement l'origine de la fuite avec ce détecteur.","a":"localisera","en":"We'll easily locate the source of the leak with this detector.","alts":[]},
 {"slot":"t|Futur|3","f":"tense","form":"Futur","s":"Nous ___ le signal du drone dès qu'il redémarrera.","a":"localiserons","en":"We will locate the drone's signal as soon as it restarts.","alts":[]},
 {"slot":"t|Futur|3","f":"tense","form":"Futur","s":"Demain, nous ___ précisément l'épicentre de la secousse.","a":"localiserons","en":"Tomorrow, we will precisely locate the epicenter of the tremor.","alts":[]},
 {"slot":"t|Futur|4","f":"tense","form":"Futur","s":"Vous ___ facilement la boutique grâce à cette carte.","a":"localiserez","en":"You will easily locate the shop thanks to this map.","alts":[]},
 {"slot":"t|Futur|4","f":"tense","form":"Futur","s":"Avec ce badge, vous ___ chaque employé dans le bâtiment.","a":"localiserez","en":"With this badge, you will locate every employee in the building.","alts":[]},
 {"slot":"t|Futur|5","f":"tense","form":"Futur","s":"Les ingénieurs ___ la panne dès leur arrivée sur place.","a":"localiseront","en":"The engineers will locate the fault as soon as they arrive on site.","alts":[]},
 {"slot":"t|Futur|5","f":"tense","form":"Futur","s":"Ces satellites ___ précisément les navires en détresse.","a":"localiseront","en":"These satellites will precisely locate ships in distress.","alts":[]},
 {"slot":"t|Conditionnel|0","f":"tense","form":"Conditionnel","s":"Si j'avais un meilleur GPS, je ___ plus vite l'adresse.","a":"localiserais","en":"If I had a better GPS, I would locate the address faster.","alts":[]},
 {"slot":"t|Conditionnel|0","f":"tense","form":"Conditionnel","s":"Si tu avais ce logiciel, tu ___ facilement l'appareil volé.","a":"localiserais","en":"If you had this software, you would easily locate the stolen device.","alts":[]},
 {"slot":"t|Conditionnel|1","f":"tense","form":"Conditionnel","s":"Si elle avait ce traceur, elle ___ sa valise en un instant.","a":"localiserait","en":"If she had this tracker, she would locate her suitcase in an instant.","alts":[]},
 {"slot":"t|Conditionnel|1","f":"tense","form":"Conditionnel","s":"Avec un meilleur signal, on ___ le bateau plus rapidement.","a":"localiserait","en":"With a better signal, we would locate the boat more quickly.","alts":[]},
 {"slot":"t|Conditionnel|2","f":"tense","form":"Conditionnel","s":"Si nous avions ces coordonnées, nous ___ facilement l'épave.","a":"localiserions","en":"If we had these coordinates, we would easily locate the wreck.","alts":[]},
 {"slot":"t|Conditionnel|2","f":"tense","form":"Conditionnel","s":"Avec votre aide, nous ___ plus vite la source du signal.","a":"localiserions","en":"With your help, we would locate the source of the signal faster.","alts":[]},
 {"slot":"t|Conditionnel|3","f":"tense","form":"Conditionnel","s":"Si vous aviez ce plan, vous ___ facilement la sortie de secours.","a":"localiseriez","en":"If you had this plan, you would easily locate the emergency exit.","alts":[]},
 {"slot":"t|Conditionnel|3","f":"tense","form":"Conditionnel","s":"Avec ce nouvel outil, vous ___ chaque colis en temps réel.","a":"localiseriez","en":"With this new tool, you would locate every package in real time.","alts":[]},
 {"slot":"t|Conditionnel|4","f":"tense","form":"Conditionnel","s":"Si les secouristes avaient ce drone, ils ___ les survivants plus vite.","a":"localiseraient","en":"If the rescuers had this drone, they would locate the survivors faster.","alts":[]},
 {"slot":"t|Conditionnel|4","f":"tense","form":"Conditionnel","s":"Avec ces capteurs, elles ___ instantanément la fuite de gaz.","a":"localiseraient","en":"With these sensors, they would instantly locate the gas leak.","alts":[]},
 {"slot":"t|Subjonctif","f":"subj","form":"Subjonctif","s":"Il faut que tu ___ la position exacte du navire avant midi.","a":"localises","en":"You need to locate the exact position of the ship before noon.","alts":[]},
 {"slot":"t|Subjonctif","f":"subj","form":"Subjonctif","s":"Je veux qu'elle ___ mon colis avant ce soir.","a":"localise","en":"I want her to locate my package before tonight.","alts":[]},
 {"slot":"s|0","f":"sense","s":"Grâce à son téléphone, la police a pu ___ le suspect en quelques minutes.","a":"localiser","en":"Thanks to his phone, the police managed to locate the suspect within minutes.","alts":[]},
 {"slot":"s|0","f":"sense","s":"Les secouristes ont réussi à ___ les randonneurs perdus dans la montagne.","a":"localiser","en":"The rescuers managed to locate the lost hikers in the mountains.","alts":[]},
 {"slot":"s|1","f":"sense","s":"Les pompiers ont réussi à ___ l'incendie avant qu'il ne se propage à toute la forêt.","a":"localiser","en":"The firefighters managed to contain the fire to one area before it spread to the whole forest.","alts":[]},
 {"slot":"s|1","f":"sense","s":"Les médecins ont pu ___ l'infection avant qu'elle n'atteigne d'autres organes.","a":"localiser","en":"The doctors managed to localize the infection before it reached other organs.","alts":[]},
 {"slot":"s|2","f":"sense","s":"Notre équipe doit ___ l'application dans dix langues différentes avant son lancement.","a":"localiser","en":"Our team must localize the app into ten different languages before its launch.","alts":[]},
 {"slot":"s|2","f":"sense","s":"Il est complexe de ___ un jeu vidéo tout en conservant son humour original.","a":"localiser","en":"It is complex to localize a video game while keeping its original humor.","alts":[]}
]}
]

# Validation
total_q = 0
for item in data:
    for q in item["qs"]:
        assert q["s"].count("___") == 1, (item["id"], q["s"])
        total_q += 1

with open("/Users/wangsijie/Develop/projects/french/vocabulary/quizslot_out/g6007_83.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=None)

print("total questions:", total_q)
