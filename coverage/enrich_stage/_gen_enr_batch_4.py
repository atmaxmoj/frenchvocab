import json
import os

data = [
  {
    "id": "7895",
    "fr": "évacuation",
    "pos": "noun",
    "en": "evacuation (of people, gas, fumes, etc.)",
    "ipa": "/e.va.kɥa.zjɔ̃/",
    "zh": "疏散；撤离；排空",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>evacuatio</em>, « action de vider ».",
      "hook": {
        "roots": "源自拉丁语 evacuatio（evacuare 的过去分词 evacuatus，e-‘出’+ vacuus‘空’），与英语 evacuation、evacuate、vacant、vacuum 同源；核心意象：把内部清空、让人撤出。",
        "why": "疏散就是把建筑里的空间‘清空’，让所有人出去。"
      }
    },
    "examples": [
      {"fr": "Les pompiers ont ordonné l'évacuation immédiate de l'immeuble.", "en": "The firefighters ordered the immediate evacuation of the building.", "target": "évacuation"},
      {"fr": "L'évacuation des fumées toxiques a duré plusieurs heures.", "en": "The evacuation of the toxic fumes lasted several hours.", "target": "évacuation"}
    ],
    "formF": "",
    "cog": "evacuation",
    "cogWarn": []
  },
  {
    "id": "7896",
    "fr": "gouvernant",
    "pos": "noun",
    "en": "ruler, governing person (male); person in authority",
    "ipa": "/ɡu.vɛʁ.nɑ̃/",
    "zh": "统治者；掌权者；执政者（男性）",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>*gubernare</em>, « diriger un navire ».",
      "hook": {
        "roots": "源自通俗拉丁语 *gubernare‘掌舵、统治’（拉丁语 gubernator‘舵手’），与英语 govern、governor、government、gubernatorial 同源；核心意象：掌舵的人。",
        "why": "统治者就像船长掌舵，把握国家方向。"
      }
    },
    "examples": [
      {"fr": "Le gouvernant fit publier un édit qui surprit toute la cour.", "en": "The ruler issued an edict that surprised the entire court.", "target": "gouvernant"},
      {"fr": "Ce jeune gouvernant rêvait de réformer le royaume sans verser de sang.", "en": "This young ruler dreamed of reforming the kingdom without bloodshed.", "target": "gouvernant"}
    ],
    "formF": "gouvernante",
    "cog": "governor",
    "cogWarn": ["gouvernant 指旧称的统治者/当权者，与 governor（州长、总督）并不完全等同"]
  },
  {
    "id": "7897",
    "fr": "amidon",
    "pos": "noun",
    "en": "starch",
    "ipa": "/a.mi.dɔ̃/",
    "zh": "淀粉；浆粉",
    "etym": {
      "from": "gr.",
      "text": "Du grec <em>amylon</em>, « qui n'est pas moulu au moulin ».",
      "hook": {
        "roots": "源自希腊语 amylon（a-‘不’+ myle‘磨坊’），指未经碾磨的纯净淀粉；与英语 amyl、amylase、amylum 同源；核心意象：未经过磨坊的精细粉末。",
        "why": "淀粉是磨坊里没磨过的纯白粉末，用来勾芡。"
      }
    },
    "examples": [
      {"fr": "On ajoute un peu d'amidon pour épaissir la sauce.", "en": "A little starch is added to thicken the sauce.", "target": "amidon"},
      {"fr": "L'amidon de maïs remplace souvent la farine dans cette recette.", "en": "Corn starch often replaces flour in this recipe.", "target": "amidon"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7898",
    "fr": "fainéant",
    "pos": "noun",
    "en": "idler, lazy person (male); slacker",
    "ipa": "/fɛ.ne.ɑ̃/",
    "zh": "懒汉；游手好闲的人；偷懒者（男性）",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>*fingentem</em>, « celui qui feint pour ne pas travailler ».",
      "hook": {
        "roots": "源自通俗拉丁语 fingere‘塑造；假装’的分词 *fingentem，指装病逃避劳动的人；与英语 feign、fiction、figment、faint 同源；核心意象：装出一副样子不干活。",
        "why": "懒汉总爱‘塑造’借口，假装很忙其实没干活。"
      }
    },
    "examples": [
      {"fr": "Ce fainéant passe ses journées sur le canapé.", "en": "That idler spends his days on the couch.", "target": "fainéant"},
      {"fr": "Le patron a renvoyé le fainéant qui ne finissait jamais ses tâches.", "en": "The boss fired the slacker who never finished his tasks.", "target": "fainéant"}
    ],
    "formF": "fainéante",
    "cog": "faineant",
    "cogWarn": []
  },
  {
    "id": "7899",
    "fr": "incinération",
    "pos": "noun",
    "en": "incineration, cremation",
    "ipa": "/ɛ̃.si.ne.ʁa.zjɔ̃/",
    "zh": "焚化；火化；焚烧",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>incineratio</em>, « action de réduire en cendres ».",
      "hook": {
        "roots": "源自拉丁语 cinis‘灰’与 incinerare‘烧成灰’；与英语 incinerate、incineration、cinder 同源；核心意象：化为灰烬。",
        "why": "火化就是把遗体烧成 cinis 一样的灰烬。"
      }
    },
    "examples": [
      {"fr": "L'incinération des déchets médicaux exige une température très élevée.", "en": "The incineration of medical waste requires a very high temperature.", "target": "incinération"},
      {"fr": "Elle a choisi l'incinération plutôt que l'inhumation.", "en": "She chose cremation rather than burial.", "target": "incinération"}
    ],
    "formF": "",
    "cog": "incineration",
    "cogWarn": []
  },
  {
    "id": "7900",
    "fr": "ivresse",
    "pos": "noun",
    "en": "intoxication, drunkenness; euphoria",
    "ipa": "/i.vʁɛs/",
    "zh": "醉酒；陶醉；兴奋",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>ebrietas</em>, « état d'ébriété ».",
      "hook": {
        "roots": "源自拉丁语 ebrius‘醉的’与 ebrietas‘醉酒状态’；与英语 inebriate、inebriation、sobriety 同源；核心意象：醉醺醺的状态。",
        "why": "ivresse 就是 ebrius 上身，理智被酒精冲昏。"
      }
    },
    "examples": [
      {"fr": "L'ivresse lui fit perdre tout sens de la prudence.", "en": "Intoxication made him lose all sense of caution.", "target": "ivresse"},
      {"fr": "Une ivresse collective s'empara du stade après le but.", "en": "A collective euphoria swept through the stadium after the goal.", "target": "ivresse"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7901",
    "fr": "onirique",
    "pos": "adj",
    "en": "dreamlike, oneiric",
    "ipa": "/ɔ.ni.ʁik/",
    "zh": "梦境的；如梦的",
    "etym": {
      "from": "gr.",
      "text": "Du grec <em>oneiros</em>, « rêve ».",
      "hook": {
        "roots": "源自希腊语 oneiros‘梦’；与英语 oneiric、oneiromancy、incubus（经由同一梦境意象）同源；核心意象：从梦里飘出来的画面。",
        "why": "onirique 就像从 oneiros 梦境里摘出来的场景，朦胧不真实。"
      }
    },
    "examples": [
      {"fr": "Le film offre une atmosphère onirique peuplée de symboles.", "en": "The film offers a dreamlike atmosphere filled with symbols.", "target": "onirique"},
      {"fr": "Ses tableaux oniriques brouillent la frontière entre veille et sommeil.", "en": "His oneiric paintings blur the boundary between waking and sleeping.", "target": "oniriques"}
    ],
    "formF": "",
    "cog": "oneiric",
    "cogWarn": []
  },
  {
    "id": "7902",
    "fr": "raz",
    "pos": "noun",
    "en": "tidal race, strong tidal current",
    "ipa": "/ʁa/",
    "zh": "潮汐急流；海峡急流",
    "etym": {
      "from": "germ.",
      "text": "De l'ancien norrois <em>rás</em>, « course rapide de l'eau ».",
      "hook": {
        "roots": "源自古诺尔斯语 rás‘快速水流、赛跑’（日耳曼语支）；与英语 race、rush、run、racecourse 同源；核心意象：潮水在海峡里赛跑。",
        "why": "raz 就是潮水在狭窄水道里 rush 冲刺，形成急流。"
      }
    },
    "examples": [
      {"fr": "Le raz de Sein attire les amateurs de sensations fortes.", "en": "The Sein tidal race attracts thrill seekers.", "target": "raz"},
      {"fr": "Naviguer dans ce raz demande une parfaite connaissance des marées.", "en": "Sailing in this tidal race requires perfect knowledge of the tides.", "target": "raz"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7903",
    "fr": "rejaillir",
    "pos": "verb",
    "en": "to splash back, rebound; to reflect (light, blame); to backlash",
    "ipa": "/ʁə.ʒa.jiʁ/",
    "zh": "溅回；反弹；反射；波及",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>*jactare</em> avec le préfixe re-, « sauter de nouveau ».",
      "hook": {
        "roots": "源自拉丁语 jacere/jactare‘投掷、抛洒’，加上 re-‘回’；与英语 jet、jettison、project、eject 同源；核心意象：被抛出去后又弹回来。",
        "why": "rejaillir 就像水珠被 jactare 扔出去，又溅回脸上。"
      }
    },
    "examples": [
      {"fr": "Les gouttes d'eau rejaillirent sur le mur de la douche.", "en": "The water droplets splashed back against the shower wall.", "target": "rejaillirent"},
      {"fr": "Son erreur de jugement rejaillit sur toute l'équipe.", "en": "His error of judgment rebounded on the whole team.", "target": "rejaillit"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7904",
    "fr": "électromécanique",
    "pos": "adj",
    "en": "electromechanical",
    "ipa": "/e.lɛk.tʁo.me.ka.nik/",
    "zh": "机电的；电动机械的",
    "etym": {
      "from": "gr.",
      "text": "Du grec <em>ēlektron</em>, « ambre », et <em>mēkhanē</em>, « machine ».",
      "hook": {
        "roots": "源自希腊语 ēlektron‘琥珀’（摩擦生电）与 mēkhanē‘机械装置’；与英语 electric、electron、mechanical、machine 同源；核心意象：电与机械联手工作。",
        "why": "电（electron）和机械（machine）合体，就是 électromécanique。"
      }
    },
    "examples": [
      {"fr": "Le technicien répare les systèmes électromécaniques du métro.", "en": "The technician repairs the electromechanical systems of the subway.", "target": "électromécaniques"},
      {"fr": "Une panne électromécanique a immobilisé l'ascenseur.", "en": "An electromechanical breakdown immobilized the elevator.", "target": "électromécanique"}
    ],
    "formF": "",
    "cog": "electromechanical",
    "cogWarn": []
  },
  {
    "id": "7905",
    "fr": "prédominant",
    "pos": "adj",
    "en": "predominant, prevailing, dominant",
    "ipa": "/pʁe.dɔ.mi.nɑ̃/",
    "zh": "占主导地位的；主要的；盛行的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>prae-</em> et <em>dominari</em>, « dominer avant les autres ».",
      "hook": {
        "roots": "源自拉丁语 prae-‘在前’与 dominari‘统治、主宰’；与英语 predominant、dominate、dominion、domain 同源；核心意象：提前占据统治地位。",
        "why": "prédominant 就是 pre-提前 dominari 统治全场。"
      }
    },
    "examples": [
      {"fr": "Le rouge est la couleur prédominante de ce tableau.", "en": "Red is the predominant color in this painting.", "target": "prédominante"},
      {"fr": "L'influence américaine reste prédominante dans l'industrie du cinéma.", "en": "American influence remains predominant in the film industry.", "target": "prédominante"}
    ],
    "formF": "prédominante",
    "cog": "predominant",
    "cogWarn": []
  },
  {
    "id": "7906",
    "fr": "entasser",
    "pos": "verb",
    "en": "to pile up, heap up, stack; to cram",
    "ipa": "/ɑ̃.ta.se/",
    "zh": "堆积；堆放；塞满",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>taxare</em>, « toucher, presser », avec le préfixe en-.",
      "hook": {
        "roots": "源自拉丁语 taxare‘触摸、评估、按压’，en- 表示‘进入、使成’；与英语 tax、task、tangible、exact 同源；核心意象：压紧成一堆。",
        "why": "把东西 tax 压紧，堆成一座小山。"
      }
    },
    "examples": [
      {"fr": "Il entasse les cartons dans le garage depuis des mois.", "en": "He has been piling up boxes in the garage for months.", "target": "entasse"},
      {"fr": "La grand-mère entasse les assiettes sur le buffet.", "en": "The grandmother stacks the plates on the sideboard.", "target": "entasse"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7907",
    "fr": "nuageux",
    "pos": "adj",
    "en": "cloudy, overcast",
    "ipa": "/nɥa.ʒø/",
    "zh": "多云的；阴天的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>nubes</em>, « nuage », avec le suffixe -eux.",
      "hook": {
        "roots": "源自拉丁语 nubes‘云’，加上形容词后缀 -eux；与英语 nuance、nubilous、nebulous（均表云/朦胧）同源；核心意象：布满云朵。",
        "why": "天空像盖了一层 nubes 云被，灰蒙蒙的。"
      }
    },
    "examples": [
      {"fr": "Le ciel nuageux annonçait une pluie prochaine.", "en": "The cloudy sky signaled impending rain.", "target": "nuageux"},
      {"fr": "Cette région est nuageuse plus de deux cents jours par an.", "en": "This region is cloudy more than two hundred days a year.", "target": "nuageuse"}
    ],
    "formF": "nuageuse",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7908",
    "fr": "écrasé",
    "pos": "adj",
    "en": "crushed, flattened; overwhelming (victory)",
    "ipa": "/e.kʁa.ze/",
    "zh": "被压碎的；压扁的；压倒性的",
    "etym": {
      "from": "germ.",
      "text": "De l'ancien français <em>escraser</em>, du germanique <em>*kratsjan</em>, « briser ».",
      "hook": {
        "roots": "源自古法语 escraser，来自日耳曼语 *kratsjan‘压碎、碎裂’；与英语 crash、crush、crunch 同源；核心意象：被碾成薄片。",
        "why": "像被车 crash 碾过一样，又扁又碎。"
      }
    },
    "examples": [
      {"fr": "Un fruit écrasé gâchait le fond du sac.", "en": "A crushed fruit was spoiling the bottom of the bag.", "target": "écrasé"},
      {"fr": "L'équipe locale a remporté une victoire écrasante.", "en": "The local team won an overwhelming victory.", "target": "écrasante"}
    ],
    "formF": "écrasée",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7909",
    "fr": "déporter",
    "pos": "verb",
    "en": "to deport; to displace, shift off course",
    "ipa": "/de.pɔʁ.te/",
    "zh": "驱逐出境；使偏离；流放",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>deportare</em>, « transporter hors d'un lieu ».",
      "hook": {
        "roots": "源自拉丁语 de-‘离开’与 portare‘携带’；与英语 deport、deportation、portable、porter 同源；核心意象：强行带离。",
        "why": "déporter 就是把人从祖国 de-port 运走。"
      }
    },
    "examples": [
      {"fr": "Le régime décida de déporter les opposants dans des camps lointains.", "en": "The regime decided to deport the opponents to distant camps.", "target": "déporter"},
      {"fr": "Le vent violent déporta le voilier vers les récifs.", "en": "The strong wind shifted the sailboat off course toward the reefs.", "target": "déporta"}
    ],
    "formF": "",
    "cog": "deport",
    "cogWarn": []
  },
  {
    "id": "7910",
    "fr": "fendre",
    "pos": "verb",
    "en": "to split, cleave, crack",
    "ipa": "/fɑ̃dʁ/",
    "zh": "劈开；使裂开；分开",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>findere</em>, « fendre, diviser ».",
      "hook": {
        "roots": "源自拉丁语 findere‘劈开、分裂’；与英语 fissure、fission、cleave（共同意象）同源；核心意象：把物体劈成两半。",
        "why": "斧头 findere 木头，咔嚓一声裂开。"
      }
    },
    "examples": [
      {"fr": "Il fend le bois avec une hache aiguisée.", "en": "He splits the wood with a sharpened axe.", "target": "fend"},
      {"fr": "Un éclair fendit le ciel au-dessus de la mer.", "en": "A flash of lightning split the sky above the sea.", "target": "fendit"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7911",
    "fr": "mi-voix",
    "pos": "adv",
    "en": "in a low voice, half aloud, under one's breath",
    "ipa": "/mi vwa/",
    "zh": "低声地；半声地；自言自语般地",
    "etym": {
      "from": "lat.",
      "text": "De <em>mi-</em>, « à moitié », et du latin <em>vox</em>, « voix ».",
      "hook": {
        "roots": "源自拉丁语 vox‘声音’（与法语 voix 同源），mi- 表‘一半’；与英语 voice、vocal、vocation、vociferous 同源；核心意象：只用一半声音说话。",
        "why": "mi-voix 就是 voice 只开一半，别人刚好听见。"
      }
    },
    "examples": [
      {"fr": "Elle répéta le mot mi-voix pour ne pas réveiller l'enfant.", "en": "She repeated the word in a low voice so as not to wake the child.", "target": "mi-voix"},
      {"fr": "Il marmonna une excuse mi-voix.", "en": "He muttered an excuse under his breath.", "target": "mi-voix"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7912",
    "fr": "nuque",
    "pos": "noun",
    "en": "nape (of the neck); back of the neck",
    "ipa": "/nyk/",
    "zh": "后颈；颈背",
    "etym": {
      "from": "ar.",
      "text": "De l'arabe <em>nuḵāʿ</em>, passé par le latin médical <em>nucha</em>, « nuque ».",
      "hook": {
        "roots": "源自阿拉伯语 nuḵāʿ‘脊髓/后颈’，经中世纪拉丁语 nucha 进入法语；与英语 nucha、nuchal 同源；核心意象：脖子后面。",
        "why": "nuque 就是后脑勺下面的 nucha，一捏就酸。"
      }
    },
    "examples": [
      {"fr": "Elle sentit une main froide sur sa nuque.", "en": "She felt a cold hand on the nape of her neck.", "target": "nuque"},
      {"fr": "Le médecin examina la nuque du patient avec attention.", "en": "The doctor examined the back of the patient's neck carefully.", "target": "nuque"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7913",
    "fr": "piller",
    "pos": "verb",
    "en": "to pillage, plunder, loot, ransack",
    "ipa": "/pi.je/",
    "zh": "掠夺；洗劫；抢劫",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>pilare</em>, « dépouiller, mettre à sac ».",
      "hook": {
        "roots": "源自通俗拉丁语 pilare‘剥光、掠夺’；与英语 pillage、pill、plunder（近义）同源；核心意象：把地方抢得一干二净。",
        "why": "piller 就是把村庄 pilare 一空，像吃 pill 一样吞掉财物。"
      }
    },
    "examples": [
      {"fr": "Des émeutiers ont commencé à piller les magasins du centre-ville.", "en": "Rioters began to loot the downtown shops.", "target": "piller"},
      {"fr": "Les soldats pillèrent le temple et emportèrent les statues.", "en": "The soldiers pillaged the temple and carried off the statues.", "target": "pillèrent"}
    ],
    "formF": "",
    "cog": "pillage",
    "cogWarn": []
  },
  {
    "id": "7914",
    "fr": "pompeux",
    "pos": "adj",
    "en": "pompous, bombastic, grandiloquent",
    "ipa": "/pɔ̃.pø/",
    "zh": "浮夸的；自大的；辞藻华丽的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>pompa</em>, « cortège solennel », avec le suffixe -eux.",
      "hook": {
        "roots": "源自拉丁语 pompa‘盛大游行、排场’；与英语 pomp、pompous、pompadour 同源；核心意象：讲话像盛大游行一样摆排场。",
        "why": "pompeux 的人说话像在办 pompa 大游行，华而不实。"
      }
    },
    "examples": [
      {"fr": "Son discours pompeux ennuya la moitié de l'assistance.", "en": "His pompous speech bored half of the audience.", "target": "pompeux"},
      {"fr": "Elle déteste les titres pompeux des articles à sensation.", "en": "She hates the bombastic headlines of sensational articles.", "target": "pompeux"}
    ],
    "formF": "pompeuse",
    "cog": "pompous",
    "cogWarn": []
  },
  {
    "id": "7915",
    "fr": "suave",
    "pos": "adj",
    "en": "suave, smooth, mellow, sweet",
    "ipa": "/swav/",
    "zh": "柔和的；圆滑的；甜美的；温文尔雅的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>suavis</em>, « doux, agréable ».",
      "hook": {
        "roots": "源自拉丁语 suavis‘甜美、愉悦’；与英语 suave、suasion、persuade 同源；核心意象：像蜜一样顺滑悦耳。",
        "why": "suave 的声音或举止像 suavis 一样让人舒服。"
      }
    },
    "examples": [
      {"fr": "Sa voix suave apaisait les nerfs de tout le monde.", "en": "His suave voice soothed everyone's nerves.", "target": "suave"},
      {"fr": "Un parfum suave de vanille flottait dans la cuisine.", "en": "A sweet scent of vanilla floated in the kitchen.", "target": "suave"}
    ],
    "formF": "",
    "cog": "suave",
    "cogWarn": []
  },
  {
    "id": "7916",
    "fr": "bouffer",
    "pos": "verb",
    "en": "to eat, gobble, scoff (slang); to blow (a fuse)",
    "ipa": "/bu.fe/",
    "zh": "（俚语）狼吞虎咽；吃；烧坏（保险丝）",
    "etym": {
      "from": "germ.",
      "text": "De l'ancien français <em>bouffer</em>, « gonfler », d'origine germanique expressive.",
      "hook": {
        "roots": "源自古法语 bouffer‘鼓起、大口吃’，来自日耳曼语表达性词根；与英语 buff、puff、buffoon 同源；核心意象：鼓起腮帮子大口吞。",
        "why": "bouffer 就像 puff 一样把食物鼓进嘴里。"
      }
    },
    "examples": [
      {"fr": "Les ados ont bouffé toute la pizza en cinq minutes.", "en": "The teenagers gobbled up the whole pizza in five minutes.", "target": "bouffé"},
      {"fr": "La surcharge a fait bouffer le fusible du sous-sol.", "en": "The overload blew the basement fuse.", "target": "bouffer"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7917",
    "fr": "capituler",
    "pos": "verb",
    "en": "to surrender, capitulate, give in",
    "ipa": "/ka.pi.ty.le/",
    "zh": "投降；屈服；让步",
    "etym": {
      "from": "lat.",
      "text": "Du latin médiéval <em>capitulare</em>, « rédiger un chapitre, traiter ».",
      "hook": {
        "roots": "源自中世纪拉丁语 capitulare（capitulum‘小头、章节’），原指按章节列条件谈判；与英语 capitulate、chapter、capital、Capitol 同源；核心意象：按条件交出城池。",
        "why": "capituler 就是按 chapter 一条条谈完，最后投降。"
      }
    },
    "examples": [
      {"fr": "Après un siège de trois mois, la ville fut forcée de capituler.", "en": "After a three-month siege, the city was forced to surrender.", "target": "capituler"},
      {"fr": "Il refusa de capituler devant les pressions politiques.", "en": "He refused to give in to political pressure.", "target": "capituler"}
    ],
    "formF": "",
    "cog": "capitulate",
    "cogWarn": []
  },
  {
    "id": "7918",
    "fr": "furie",
    "pos": "noun",
    "en": "fury, rage; (mythology) Fury; fierce woman",
    "ipa": "/fy.ʁi/",
    "zh": "狂怒；暴怒；（希腊神话）复仇女神；泼妇",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>furor</em> et <em>furiae</em>, « rage, divinités vengeresses ».",
      "hook": {
        "roots": "源自拉丁语 furere‘狂怒’与 furiae‘复仇女神’；与英语 fury、furious、furor、infuriate 同源；核心意象：燃烧般的狂怒。",
        "why": "furie 就像复仇女神 fury 附体，怒气冲天。"
      }
    },
    "examples": [
      {"fr": "Une furie indicible s'empara d'elle en entendant la nouvelle.", "en": "An unspeakable fury seized her when she heard the news.", "target": "furie"},
      {"fr": "Les furies de la jalousie la tourmentaient jour et nuit.", "en": "The furies of jealousy tormented her day and night.", "target": "furies"}
    ],
    "formF": "",
    "cog": "fury",
    "cogWarn": []
  },
  {
    "id": "7919",
    "fr": "importuner",
    "pos": "verb",
    "en": "to bother, pester, harass, importune",
    "ipa": "/ɛ̃.pɔʁ.ty.ne/",
    "zh": "打扰；纠缠；烦扰",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>importunus</em>, « incommode, déplacé ».",
      "hook": {
        "roots": "源自拉丁语 importunus‘不方便的、讨人厌的’；与英语 importune、importunate、opportune、opportunity 同源；核心意象：在不合适的时机打扰别人。",
        "why": "opportune 是‘时机正好’，importuner 就是专挑不对的时机烦人。"
      }
    },
    "examples": [
      {"fr": "Le vendeur importunait les passants avec son insistance.", "en": "The salesman kept importuning passersby with his insistence.", "target": "importunait"},
      {"fr": "Excusez-moi de vous importuner si tard dans la soirée.", "en": "Excuse me for bothering you so late in the evening.", "target": "importuner"}
    ],
    "formF": "",
    "cog": "importune",
    "cogWarn": []
  },
  {
    "id": "7920",
    "fr": "replanter",
    "pos": "verb",
    "en": "to replant, transplant; to put back in place",
    "ipa": "/ʁə.plɑ̃.te/",
    "zh": "重新种植；移植；重新安放",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>replantare</em>, « planter de nouveau ».",
      "hook": {
        "roots": "源自拉丁语 plantare‘种植’与 re-‘重新’；与英语 replant、plant、plantation、transplant 同源；核心意象：把植物重新种回土里。",
        "why": "花被拔出来后，要 replant 回花盆。"
      }
    },
    "examples": [
      {"fr": "Nous devons replanter les rosiers à l'ombre du mur.", "en": "We must replant the rose bushes in the shade of the wall.", "target": "replanter"},
      {"fr": "Le jardinier replanta les jeunes pousses avec beaucoup de soin.", "en": "The gardener replanted the young shoots with great care.", "target": "replanta"}
    ],
    "formF": "",
    "cog": "replant",
    "cogWarn": []
  },
  {
    "id": "7921",
    "fr": "subjuguer",
    "pos": "verb",
    "en": "to subjugate, subdue, captivate, enthral",
    "ipa": "/syb.ʒy.ɡe/",
    "zh": "征服；使屈服；使着迷",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>subjugare</em>, « mettre sous le joug ».",
      "hook": {
        "roots": "源自拉丁语 sub‘在…下’与 jugum‘轭、枷锁’；与英语 subjugate、jugular、conjugate、yoke 同源；核心意象：给敌人套上轭。",
        "why": "subjuguer 就是给对方套上 jugum，让他低头拉套。"
      }
    },
    "examples": [
      {"fr": "Le conquérant cherchait à subjuguer les peuples voisins.", "en": "The conqueror sought to subjugate the neighboring peoples.", "target": "subjuguer"},
      {"fr": "Sa présence sur scène subjugua le public dès les premières notes.", "en": "Her stage presence captivated the audience from the first notes.", "target": "subjugua"}
    ],
    "formF": "",
    "cog": "subjugate",
    "cogWarn": []
  },
  {
    "id": "7922",
    "fr": "bravoure",
    "pos": "noun",
    "en": "bravery, valor, courage",
    "ipa": "/bʁa.vuʁ/",
    "zh": "勇敢；英勇；无畏",
    "etym": {
      "from": "it.",
      "text": "De l'italien <em>bravura</em>, « courage, adresse », dérivé de <em>bravo</em>.",
      "hook": {
        "roots": "源自意大利语 bravura‘勇敢、精湛’，来自 bravo‘好样的’；与英语 bravura、brave、bravo、bravado 同源；核心意象：勇士般的无畏。",
        "why": "bravoure 就是像 bravo 勇士一样冲在前面。"
      }
    },
    "examples": [
      {"fr": "Le soldat fut décoré pour son exceptionnelle bravoure.", "en": "The soldier was decorated for his exceptional bravery.", "target": "bravoure"},
      {"fr": "Son acte de bravoure sauva trois enfants de l'incendie.", "en": "His act of valor saved three children from the fire.", "target": "bravoure"}
    ],
    "formF": "",
    "cog": "bravura",
    "cogWarn": ["bravoure 指勇敢/英勇，而英语 bravura 多指技艺精湛、华丽乐段，并非同义"]
  },
  {
    "id": "7923",
    "fr": "embuscade",
    "pos": "noun",
    "en": "ambush; trap",
    "ipa": "/ɑ̃.bys.kad/",
    "zh": "埋伏；伏击；陷阱",
    "etym": {
      "from": "it.",
      "text": "De l'italien <em>imboscata</em>, « action de se cacher dans les bois ».",
      "hook": {
        "roots": "源自意大利语 imboscata‘林中埋伏’，来自 bosco‘树林’；与英语 ambush、bush、bosky、ambuscade 同源；核心意象：藏在树林里突然袭击。",
        "why": "embuscade 就是躲在 bush 里，等人靠近再跳出来。"
      }
    },
    "examples": [
      {"fr": "Les soldats tombèrent dans une embuscade au détour du chemin.", "en": "The soldiers fell into an ambush around the bend in the path.", "target": "embuscade"},
      {"fr": "La police avait tendu une embuscade aux trafiquants.", "en": "The police had set an ambush for the traffickers.", "target": "embuscade"}
    ],
    "formF": "",
    "cog": "ambuscade",
    "cogWarn": []
  },
  {
    "id": "7924",
    "fr": "laser",
    "pos": "noun",
    "en": "laser",
    "ipa": "/la.ze/",
    "zh": "激光；镭射",
    "etym": {
      "from": "angl.",
      "text": "De l'anglais <em>laser</em>, acronyme de <em>Light Amplification by Stimulated Emission of Radiation</em>.",
      "hook": {
        "roots": "来自英语 laser 的首字母缩略词（Light Amplification by Stimulated Emission of Radiation，受激辐射光放大）；与英语 laser、maser 同源；核心意象：一束受激放大的相干光束。",
        "why": "laser 就是一束被‘受激辐射’放大的强光。"
      }
    },
    "examples": [
      {"fr": "Le chirurgien utilise un laser de haute précision.", "en": "The surgeon uses a high-precision laser.", "target": "laser"},
      {"fr": "Un faisceau laser traversa la pièce dans l'obscurité.", "en": "A laser beam crossed the room in the darkness.", "target": "laser"}
    ],
    "formF": "",
    "cog": "laser",
    "cogWarn": []
  },
  {
    "id": "7925",
    "fr": "maniérer",
    "pos": "verb",
    "en": "to handle affectedly, overrefine; to be affected (in style)",
    "ipa": "/ma.nje.ʁe/",
    "zh": "做作地处理；过分雕琢；（风格）矫揉造作",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>manuarius</em>, « relatif à la main », devenu <em>manière</em>.",
      "hook": {
        "roots": "源自拉丁语 manus‘手’与 manuarius‘与手相关的’，演变为 manière‘方式’；与英语 manual、maneuver、manage、manicure 同源；核心意象：用手过分摆弄姿势。",
        "why": "maniérer 就是 manual 式地过度摆弄，显得不自然。"
      }
    },
    "examples": [
      {"fr": "Il maniait chaque geste avec une précision excessive.", "en": "He handled every gesture with excessive precision.", "target": "maniait"},
      {"fr": "Le comédien maniait la voix de façon trop théâtrale pour être crédible.", "en": "The actor handled his voice too theatrically to be credible.", "target": "maniait"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7926",
    "fr": "rassasier",
    "pos": "verb",
    "en": "to satiate, satisfy, fill up",
    "ipa": "/ʁa.sa.zje/",
    "zh": "使吃饱；使满足；腻烦",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>satiare</em>, « rassasier, satisfaire », avec le préfixe re-.",
      "hook": {
        "roots": "源自拉丁语 satiare‘使饱足’，re- 表‘完全’；与英语 satiate、satisfy、sate、saturation 同源；核心意象：吃到心满意足。",
        "why": "rassasier 就是让人完全 satiate，胃里再也装不下。"
      }
    },
    "examples": [
      {"fr": "Ce plat copieux rassasia toute la famille.", "en": "This hearty dish satiated the whole family.", "target": "rassasia"},
      {"fr": "L'enfant se rassasia de fraises jusqu'à ne plus en vouloir.", "en": "The child ate his fill of strawberries until he wanted no more.", "target": "rassasia"}
    ],
    "formF": "",
    "cog": "satiate",
    "cogWarn": []
  },
  {
    "id": "7927",
    "fr": "saillant",
    "pos": "adj",
    "en": "salient, prominent, projecting, striking",
    "ipa": "/sa.jɑ̃/",
    "zh": "突出的；显著的；凸起的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>salire</em>, « sauter, faire saillie ».",
      "hook": {
        "roots": "源自拉丁语 salire‘跳、突出’；与英语 salient、sally、assault、insult 同源；核心意象：跳出来吸引眼球。",
        "why": "saillant 就像 salire 一样从背景里跳出来，特别显眼。"
      }
    },
    "examples": [
      {"fr": "Les traits saillants de son visage attirent le regard.", "en": "The prominent features of his face attract attention.", "target": "saillants"},
      {"fr": "Le rapport souligne les points saillants de la réforme.", "en": "The report highlights the salient points of the reform.", "target": "saillants"}
    ],
    "formF": "saillante",
    "cog": "salient",
    "cogWarn": []
  },
  {
    "id": "7928",
    "fr": "tressaillir",
    "pos": "verb",
    "en": "to shudder, tremble, start",
    "ipa": "/tʁe.sa.jiʁ/",
    "zh": "颤抖；惊跳；战栗",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>salire</em> avec le préfixe intensif tres-, « tressauter ».",
      "hook": {
        "roots": "源自拉丁语 salire‘跳’，加上古法语的 tres- 强化前缀；与英语 salient、sally、assault、insult 同源；核心意象：突然惊跳一下。",
        "why": "tressaillir 就是身体突然 salire 一跳，像被吓到。"
      }
    },
    "examples": [
      {"fr": "Elle tressaillit en entendant la porte claquer derrière elle.", "en": "She started when she heard the door slam behind her.", "target": "tressaillit"},
      {"fr": "Un frisson lui fit tressaillir les épaules.", "en": "A shiver made her shoulders tremble.", "target": "tressaillir"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7929",
    "fr": "buanderie",
    "pos": "noun",
    "en": "laundry room; washhouse",
    "ipa": "/bɥɑ̃.dʁi/",
    "zh": "洗衣房；洗衣间",
    "etym": {
      "from": "dériv.",
      "text": "Dérivé de l'ancien français <em>bue</em>, « lessive », désignant le lieu du lavage.",
      "hook": {
        "roots": "源自古法语 bue‘碱液、洗涤’加上 -anderie 表场所；与英语 laundry、lavatory、lye、wash 同源；核心意象：专门洗衣物的房间。",
        "why": "buanderie 就是房子里专门 wash 衣物的地方。"
      }
    },
    "examples": [
      {"fr": "Le linge sale s'entasse dans la buanderie depuis lundi.", "en": "The dirty laundry has been piling up in the laundry room since Monday.", "target": "buanderie"},
      {"fr": "La buanderie du château abrite d'immenses cuves en pierre.", "en": "The château's laundry room houses huge stone vats.", "target": "buanderie"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7930",
    "fr": "polaire",
    "pos": "adj",
    "en": "polar",
    "ipa": "/pɔ.lɛʁ/",
    "zh": "极地的；两极的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>polaris</em>, « relatif au pôle ».",
      "hook": {
        "roots": "源自拉丁语 polus‘极’与 polaris‘极的’；与英语 polar、pole、polarity、polarize 同源；核心意象：地球两端的冰雪世界。",
        "why": "polaire 就是靠近地球 pole 的寒冷地带。"
      }
    },
    "examples": [
      {"fr": "L'expédition étudie la faune polaire en hiver.", "en": "The expedition studies polar wildlife in winter.", "target": "polaire"},
      {"fr": "Ses yeux bleus avaient une lumière presque polaire.", "en": "His blue eyes had an almost polar light.", "target": "polaire"}
    ],
    "formF": "",
    "cog": "polar",
    "cogWarn": []
  },
  {
    "id": "7931",
    "fr": "altérer",
    "pos": "verb",
    "en": "to alter, change; to spoil, tamper with",
    "ipa": "/al.te.ʁe/",
    "zh": "改变；篡改；使变质；损害",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>alterare</em>, « rendre autre, changer ».",
      "hook": {
        "roots": "源自拉丁语 alter‘另一个’与 alterare‘使变成另一个’；与英语 alter、alteration、alter ego、alternate 同源；核心意象：把原来的样子变成另一个。",
        "why": "altérer 就是把东西 alter 成另一个样子，可能变坏。"
      }
    },
    "examples": [
      {"fr": "Le chaleur peut altérer la saveur du vin.", "en": "Heat can alter the flavor of the wine.", "target": "altérer"},
      {"fr": "On a accusé le journaliste d'altérer les faits.", "en": "The journalist was accused of distorting the facts.", "target": "altérer"}
    ],
    "formF": "",
    "cog": "alter",
    "cogWarn": []
  },
  {
    "id": "7932",
    "fr": "cinéphile",
    "pos": "noun",
    "en": "film buff, cinephile, movie lover",
    "ipa": "/si.ne.fil/",
    "zh": "电影爱好者；影迷",
    "etym": {
      "from": "gr.",
      "text": "Du grec <em>kinēma</em>, « mouvement », et <em>philos</em>, « qui aime ».",
      "hook": {
        "roots": "源自希腊语 kinēma‘运动’与 philos‘爱’；与英语 cinema、cinematic、philosophy、philanthropy 同源；核心意象：爱电影爱到痴迷的人。",
        "why": "cinéphile 就是爱 cinema 像爱哲学一样深的人。"
      }
    },
    "examples": [
      {"fr": "Le cinéphile connaît par cœur les films des années soixante.", "en": "The cinephile knows the films of the sixties by heart.", "target": "cinéphile"},
      {"fr": "Ce festival réunit des cinéphiles du monde entier.", "en": "This festival brings together film buffs from around the world.", "target": "cinéphiles"}
    ],
    "formF": "",
    "cog": "cinephile",
    "cogWarn": []
  },
  {
    "id": "7933",
    "fr": "bananier",
    "pos": "noun",
    "en": "banana tree; banana plant",
    "ipa": "/ba.na.nje/",
    "zh": "香蕉树；芭蕉树",
    "etym": {
      "from": "esp.",
      "text": "De l'espagnol <em>banana</em>, fruit venu d'Afrique de l'Ouest, avec le suffixe -ier.",
      "hook": {
        "roots": "源自西班牙语 banana‘香蕉’（更早来自西非语言），加上 -ier 表‘树/植物’；与英语 banana、plantain 同源；核心意象：挂满香蕉的树。",
        "why": "bananier 就是长满 banana 的大树，叶子宽大。"
      }
    },
    "examples": [
      {"fr": "Un bananier majestueux ombrage la terrasse.", "en": "A majestic banana tree shades the terrace.", "target": "bananier"},
      {"fr": "Les bananiers prospèrent dans le climat tropical de l'île.", "en": "The banana trees thrive in the island's tropical climate.", "target": "bananiers"}
    ],
    "formF": "",
    "cog": "banana",
    "cogWarn": []
  },
  {
    "id": "7934",
    "fr": "débrouillard",
    "pos": "adj",
    "en": "resourceful, self-reliant, canny (colloquial)",
    "ipa": "/de.bʁu.jaʁ/",
    "zh": "有办法的；机灵的；能随机应变的",
    "etym": {
      "from": "dériv.",
      "text": "Dérivé de <em>se débrouiller</em>, « se sortir d'une situation confuse », avec le suffixe -ard.",
      "hook": {
        "roots": "源自法语 brouiller‘搅混、使混乱’，débrouiller‘理清混乱’，-ard 表‘具有…特征的人’；与英语 embroil、broil、disentangle 同源；核心意象：能从混乱中找到出路。",
        "why": "débrouillard 就是擅长把 embroil 的乱局 disentangle 的人。"
      }
    },
    "examples": [
      {"fr": "Cette débrouillarde a réparé la voiture avec un simple trombone.", "en": "This resourceful woman fixed the car with a simple paper clip.", "target": "débrouillarde"},
      {"fr": "Les étudiants débrouillards trouvent toujours une solution.", "en": "Resourceful students always find a solution.", "target": "débrouillards"}
    ],
    "formF": "débrouillarde",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7935",
    "fr": "rapatriement",
    "pos": "noun",
    "en": "repatriation; return home",
    "ipa": "/ʁa.pa.tʁi.mɑ̃/",
    "zh": "遣返；归国；回国",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>repatriare</em>, « retourner dans son pays ».",
      "hook": {
        "roots": "源自拉丁语 re-‘回’与 patria‘祖国、父邦’；与英语 repatriate、repatriation、patriot、paternal 同源；核心意象：回到祖国。",
        "why": "rapatriement 就是 re- 回到 patria 祖国。"
      }
    },
    "examples": [
      {"fr": "Le rapatriement des touristes bloqués dura plusieurs jours.", "en": "The repatriation of the stranded tourists lasted several days.", "target": "rapatriement"},
      {"fr": "Des associations réclament le rapatriement des œuvres spoliées.", "en": "Associations are demanding the repatriation of the looted artworks.", "target": "rapatriement"}
    ],
    "formF": "",
    "cog": "repatriation",
    "cogWarn": []
  },
  {
    "id": "7936",
    "fr": "whisky",
    "pos": "noun",
    "en": "whiskey; whisky",
    "ipa": "/wis.ki/",
    "zh": "威士忌；威士忌酒",
    "etym": {
      "from": "angl.",
      "text": "De l'anglais <em>whisky</em>, emprunté au gaélique écossais <em>uisge beatha</em>, « eau de vie ».",
      "hook": {
        "roots": "来自英语 whisky，借自苏格兰盖尔语 uisge beatha‘生命之水’；与英语 whiskey、whisky、usquebaugh 同源；核心意象：琥珀色的烈酒。",
        "why": "whisky 在盖尔语里是‘生命之水’，喝了上头。"
      }
    },
    "examples": [
      {"fr": "Il commanda un whisky sec au comptoir du bar.", "en": "He ordered a straight whiskey at the bar counter.", "target": "whisky"},
      {"fr": "L'Écossais préfère le whisky sans glace.", "en": "The Scot prefers whisky without ice.", "target": "whisky"}
    ],
    "formF": "",
    "cog": "whiskey",
    "cogWarn": []
  },
  {
    "id": "7937",
    "fr": "music-hall",
    "pos": "noun",
    "en": "music hall, variety theater",
    "ipa": "/my.zik ɔl/",
    "zh": "音乐厅；杂耍歌舞剧场；综艺剧院",
    "etym": {
      "from": "angl.",
      "text": "De l'anglais <em>music hall</em>, « salle de spectacles variétés ».",
      "hook": {
        "roots": "来自英语 music hall（music‘音乐’+ hall‘大厅’）；与英语 music、hall、musical、hallway 同源；核心意象：有歌舞杂耍的剧场。",
        "why": "music-hall 就是 music + hall，听音乐看杂耍的地方。"
      }
    },
    "examples": [
      {"fr": "La revue se produisait chaque soir au music-hall.", "en": "The revue performed every evening at the music hall.", "target": "music-hall"},
      {"fr": "Ce music-hall parisien accueillait les plus grandes stars.", "en": "This Parisian music hall hosted the biggest stars.", "target": "music-hall"}
    ],
    "formF": "",
    "cog": "music hall",
    "cogWarn": []
  },
  {
    "id": "7938",
    "fr": "moderniste",
    "pos": "adj",
    "en": "modernist",
    "ipa": "/mɔ.dɛʁ.nist/",
    "zh": "现代主义的；现代派的",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>modernus</em>, « d'aujourd'hui », avec le suffixe -iste.",
      "hook": {
        "roots": "源自拉丁语 modernus‘现今的’，加上 -iste‘支持者/从业者’；与英语 modernist、modern、modernity、modernism 同源；核心意象：追随现代潮流。",
        "why": "moderniste 就是坚持 modern 风格的人。"
      }
    },
    "examples": [
      {"fr": "L'architecte moderniste rompt avec les ornements traditionnels.", "en": "The modernist architect breaks with traditional ornamentation.", "target": "moderniste"},
      {"fr": "Sa musique moderniste divise le public.", "en": "His modernist music divides the audience.", "target": "moderniste"}
    ],
    "formF": "",
    "cog": "modernist",
    "cogWarn": []
  },
  {
    "id": "7939",
    "fr": "feuilletoniste",
    "pos": "noun",
    "en": "serial writer, soap-opera writer",
    "ipa": "/fœj.tɔ.nist/",
    "zh": "连载小说作家；肥皂剧编剧",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>folium</em>, « feuille », passé par <em>feuilleton</em>, « partie d'un journal ».",
      "hook": {
        "roots": "源自拉丁语 folium‘叶子/纸张’，演变为 feuilleton‘报刊连载小品’，加上 -iste‘从业者’；与英语 folio、foliage、foliar、feuilleton 同源；核心意象：在报纸连载故事里写字的人。",
        "why": "feuilletoniste 就是把故事写在 folium 一样的报纸连载版上的人。"
      }
    },
    "examples": [
      {"fr": "Le feuilletoniste publiait un nouvel épisode chaque semaine.", "en": "The serial writer published a new episode every week.", "target": "feuilletoniste"},
      {"fr": "Cette feuilletoniste crée des intrigues qui captivent des millions de lectrices.", "en": "This serial writer creates plots that captivate millions of readers.", "target": "feuilletoniste"}
    ],
    "formF": "",
    "cog": "feuilleton",
    "cogWarn": []
  },
  {
    "id": "7940",
    "fr": "gifle",
    "pos": "noun",
    "en": "slap, smack",
    "ipa": "/ʒifl/",
    "zh": "耳光；巴掌",
    "etym": {
      "from": "onom.",
      "text": "D'origine onomatopéique ou de l'ancien français <em>gife</em>, « joue ».",
      "hook": {
        "roots": "源自拟声词 gif-‘啪’，或古法语 gife‘脸颊’；与英语 slap、smack、cuff（近义拟声）同源；核心意象：手掌打在脸上的脆响。",
        "why": "gifle 就是脸上‘啪’的一声 slap。"
      }
    },
    "examples": [
      {"fr": "Il reçut une gifle cinglante avant de comprendre son erreur.", "en": "He received a stinging slap before understanding his mistake.", "target": "gifle"},
      {"fr": "Sa mère lui donna une gifle après l'insulte.", "en": "His mother gave him a slap after the insult.", "target": "gifle"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7941",
    "fr": "remarquablement",
    "pos": "adv",
    "en": "remarkably, notably, outstandingly",
    "ipa": "/ʁə.maʁ.ka.blə.mɑ̃/",
    "zh": "显著地；出色地；异常地",
    "etym": {
      "from": "lat. vulg.",
      "text": "Du latin vulgaire <em>marcāre</em>, « marquer », avec le préfixe re- et les suffixes -able et -ment.",
      "hook": {
        "roots": "源自通俗拉丁语 marcare‘做标记’，re-‘再次’，-able/-ment 构成副词；与英语 remark、remarkable、mark、margin 同源；核心意象：值得重新标记出来。",
        "why": "remarquablement 就是出色到要 re-mark 一遍。"
      }
    },
    "examples": [
      {"fr": "L'orchestre interpréta la symphonie remarquablement.", "en": "The orchestra performed the symphony remarkably.", "target": "remarquablement"},
      {"fr": "Cette solution fonctionne remarquablement bien sous pression.", "en": "This solution works remarkably well under pressure.", "target": "remarquablement"}
    ],
    "formF": "",
    "cog": "remarkably",
    "cogWarn": []
  },
  {
    "id": "7942",
    "fr": "éperdument",
    "pos": "adv",
    "en": "desperately, madly, wildly",
    "ipa": "/e.pɛʁ.dy.mɑ̃/",
    "zh": "疯狂地；绝望地；极度地",
    "etym": {
      "from": "lat.",
      "text": "Du latin <em>perditus</em>, « perdu, abandonné », avec le préfixe ex- et le suffixe -ment.",
      "hook": {
        "roots": "源自拉丁语 perditus‘迷失的、堕落的’，ex-‘彻底’，-ment 副词后缀；与英语 desperate、perdition、despair 同源；核心意象：像彻底迷失一样不顾一切。",
        "why": "éperdument 就是像 perdition 里走出来的人，什么都不顾。"
      }
    },
    "examples": [
      {"fr": "Il l'aimait éperdument malgré les difficultés.", "en": "He loved her madly despite the difficulties.", "target": "éperdument"},
      {"fr": "Elle courait éperdument pour ne pas manquer le train.", "en": "She ran desperately so as not to miss the train.", "target": "éperdument"}
    ],
    "formF": "",
    "cog": "",
    "cogWarn": []
  },
  {
    "id": "7943",
    "fr": "fantaisiste",
    "pos": "adj",
    "en": "whimsical, fanciful, fantastic (in the imaginative sense)",
    "ipa": "/fɑ̃.tɛ.zist/",
    "zh": "异想天开的；奇幻的；随心所欲的",
    "etym": {
      "from": "gr.",
      "text": "Du grec <em>phantasia</em>, « apparition, imagination », avec le suffixe -iste.",
      "hook": {
        "roots": "源自希腊语 phantasia‘想象、幻象’；与英语 fantastic、fantasy、phantasm、fancy 同源；核心意象：脑子里充满奇幻想像。",
        "why": "fantaisiste 就是脑子里装满 fantasy 的点子，不按常理出牌。"
      }
    },
    "examples": [
      {"fr": "Son projet fantaisiste manque de fondements réalistes.", "en": "His whimsical project lacks realistic foundations.", "target": "fantaisiste"},
      {"fr": "Le décor fantaisiste mêlait champignons géants et horloges molles.", "en": "The fanciful decor mixed giant mushrooms and melting clocks.", "target": "fantaisiste"}
    ],
    "formF": "",
    "cog": "fantasist",
    "cogWarn": ["fantaisiste 不等于 fantastic（极好的、了不起的），更接近 whimsical/fanciful"]
  },
  {
    "id": "7944",
    "fr": "greffier",
    "pos": "noun",
    "en": "court clerk, registrar",
    "ipa": "/ɡʁe.fje/",
    "zh": "法院书记员；登记员；文书",
    "etym": {
      "from": "lat.",
      "text": "Du latin tardif <em>graphium</em>, « style pour écrire », passé par <em>greffe</em>, « registre ».",
      "hook": {
        "roots": "源自晚期拉丁语 graphium‘书写用的尖笔’，演变为 greffe‘登记簿’，-ier 表从业者；与英语 graphic、graphite、graft、graffito 同源；核心意象：用笔在登记簿上记录。",
        "why": "greffier 就是拿着 graphite 笔在 greffe 上记录的官员。"
      }
    },
    "examples": [
      {"fr": "Le greffier lut l'arrêt à voix haute.", "en": "The court clerk read the verdict aloud.", "target": "greffier"},
      {"fr": "Devenu greffier, il consignait chaque déposition avec rigueur.", "en": "Having become a court clerk, he recorded every deposition rigorously.", "target": "greffier"}
    ],
    "formF": "greffière",
    "cog": "",
    "cogWarn": []
  }
]

out_path = "/Users/wangsijie/Develop/projects/french/vocabulary/coverage/enrich_stage/enr_batch_4.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(data)} entries to {out_path}")
