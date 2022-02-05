BOT_TOKEN = "TOKEN"
NGH_CHAT_ID = -1001605460175  # -1001780891949  # -1001605460175
LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_CASH_GAME, ENTRIES_TOURNAMENT, STAKE = range(7)
MIN_BAN_APPROVERS = 5
TABLE_ID_PREFIX = "T"
BAN_PROPOSAL_ID_PREFIX = "B"
STAKES = ["2€", "5€", "10€", "20€", "50€"]
GAME_FORMATS = ['Cash Game', 'Torneo']
REGEXES = dict(
    date=r"^([1-9]|0[1-9]|1\d|2\d|3[01])\/([1-9]|0[1-9]|1[0-2])\/(((20)\d{2})|(\d{2}))$",
    time=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
    game_formats=r"^(Cash Game|Torneo)$",
    number_of_cash_game_players=r"^[2-9]$",
    number_of_tournament_players=r"^(?:[2-9]|(?:[1-9][0-9])|100)$",
    stakes=r"^(2€|5€|10€|20€|50€)$"
)
INSULTS = [
    'Coglione.',
    'Hai fatto bene, avresti solo perso soldi.',
    'Perdente.',
    'Figa mi sembri una rata...',
    'Vai in mona!',
    'Dai che mi fai smenare CPU per un cazzo!',
    'Dio cane, appena il mio padrone mi mette amministratore del gruppo di banno a vita.',
    'Ti freezo il conto.',
    'Hai rotto il cazzo.',
    'Pezzente morto di fame.',
    "Strippacazzi.",
    "Annusaculi.",
    "Bidonaro.",
    "Rimettiti i soldi nel culo, coglione!",
    "Fumacazzi.",
    "Sapevo che il tuo sport era ciucciare i feltrini delle sedie di un' osteria di Leno",
    "Dai amici banniaml!",
    "Sei meno uomo di me.",
    "Sei un bot a pedali.",
    "Hahahahahah pezzo di merda figlio di puttana.",
    "Scrotocefalo.",
    "Rembambit ensiminit da le marijuane.",
    "Tò dit argota de mal? Tò apó dit che gò quater piante de dat embecile, ve a töle no?! Eh casso però figa.",
    "C'è uno sbirro tra di noi..."
]
