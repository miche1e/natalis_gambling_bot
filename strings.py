# main strings
ngb_main_startMessage = "Ciao!\nCongratulazioni per essere arrivato nella chat con me!" \
                        "\nInizia subito a creare un tavolo con il comando /newtable o usa il comando /help per " \
                        "scoprire tutti i comandi! "
ngb_main_help = "Comandi:\n" \
                "\n/newtable - crea una partita <b>*</b>" \
                "\n/abort - annulla la creazione <b>*</b>" \
                "\n/revoke - revoca l'iscrizione della partita citata" \
                "\n/ban [reason] - propone il ban del giocatore citato" \
                "\n/help - invia la lista dei comandi" \
                "\n\n<b>*</b> <i>comando valido solo in chat privata</i>"

# ban strings
ngb_ban_groupChatWarn = "Puoi utilizzare questo comando solo in un gruppo."
ngb_ban_instruction = "โฉ๏ธ Rispondi al messaggio di un membro del gruppo per proporne l'allontanamento."
ngb_ban_adminPromotion = "Per utilizzare questo comando devo prima essere promosso ad amministratore del gruppo."
ngb_ban_adminBanAttemptText = "{0} vuole bannare un amministratore."
ngb_ban_adminBanAttemptInsult = "Fai ancora il figo coglione"
ngb_ban_adminBanAdminAttempt = "Lol ๐ท"
ngb_ban_noReason = "Nessun motivo"
ngb_ban_button = "๐จโโ Ban tro'"
ngb_ban_recapMessage = "{0} vuole bannare {1}." \
                       "\nMotivazione: <b>{2}</b>." \
                       "\nApprovazioni: {3} / {4}"
ngb_ban_proposalExpired = "<i>proposta di ban scaduta</i>"
ngb_ban_somethingWentWrong = "<i>qualcosa รจ andato storto</i>"

# new_table strings
ngb_newtable_invalidData = "๐ฎ Dati non validi"
ngb_newtable_nullRevoke = "โฉ๏ธ Rispondi al messaggio della partita per revocarene l'iscrizione."
ngb_rewtable_revokeTableNotFound = "๐ป Tavolo non trovato."
ngb_newtable_goToPrivateMessage = "Questo comando funziona solo in <a href=\"tg://user?id={0}\">privato</a>."
ngb_newtable_privateMessage = "๐บ Fai squillare le trombe! ๐ฏ\nInvia il comando /newtable per iniziare la creazione " \
                              "di un tavolo."
ngb_newtable_abort = "๐ฆ๐ฟDai amici organiziaml!๐ฆ๐ฟ\n\n๐ถ Invia il comando /abort per annullare."
ngb_newtable_locationText = "๐ Dove lo vuoi organizzare?"
ngb_newtable_locationPlaceholder = "Location dell'evento"
ngb_newtable_dateText = "๐ Che giorno?\nRispetta il formato GG/MM/AAAA"
ngb_newtable_datePlaceholder = "GG/MM/AAAA"
ngb_newtable_timeText = "๐๏ธ Che ora?\nRispetta il formato HH:MM"
ngb_newtable_timePlaceholder = "HH:MM"
ngb_newtable_formatText = "๐ฒ Che formato vuoi giocare?"
ngb_newtable_formatPlaceholder = "Cash Game o torneo?"
ngb_newtable_playersText = "๐ฅ Inviami il numero di playerz.\nScegli un numero compreso tra "
ngb_newtable_playersNumberTexts = ["2 e 9", "2 e 100"]
ngb_newtable_playersNumberPlaceholders = ["2 - 9", "2 - 100"]
ngb_newtable_buyInText = "๐ธ Qual รจ il buy-in?"
ngb_newtable_buyInPlaceholder = "Scegli il buy-in"
ngb_newtable_registrationMessage = "๐ท Vuoi prendere parte alla partita?"
ngb_newtable_registrationPlaceholder = "Si / No"
ngb_newtable_recapTitle = "<b>Recap:</b>\n"
ngb_newtable_openRegistration = "๐บ <b>ISCRIZIONI APERTE</b> ๐ฏ\nร stato inviato il modulo d' iscrizione nel gruppo " \
                                "della N.G.H.! "
ngb_newtable_registrationButton = "๐ Iscriviaml!  {0} / {1}"
ngb_newtable_registrationRecap = "Host: {0}" \
                                 "\n๐ Presso {1}" \
                                 "\n๐ il {2} alle {3}" \
                                 "\n๐ฒ {4}" \
                                 "\n๐ฅ {5} max" \
                                 "\n๐ธ {6}" \
                                 "{7}" \
                                 "{8}" \
                                 "{9}"
ngb_newtable_registrationOpenLabel = "\n\n๐บ <b>ISCRIZIONI APERTE</b> ๐ฏ"
ngb_newtable_registrationClosedLabel = "\n\n๐ซ <b>ISCRIZIONI CHIUSE</b> ๐ซ"
ngb_newtable_playersLable = "\nPlayers: {0}"
ngb_newtable_listBulletPoint = "\n-{0}"
ngb_newtable_revokeRegistrationInfo = "\n\nโน <i>cita questo messaggio inviando il comando /revoke per revocare " \
                                      "l'iscrizione</i> "
ngb_newtable_tableExpired = "<i>tavolo scaduto</i>"
ngb_newtable_abortInsults = [
    'Coglione.',
    'Hai fatto bene, avresti solo perso soldi.',
    'Perdente.',
    'Figa mi sembri una rata...',
    'Vai in mona!',
    'Dai che mi fai smenare CPU per un cazzo!',
    'Dio cane, appena il mio padrone mi mette amministratore del gruppo ti banno a vita.',
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
    "Tรฒ dit argota de mal? Tรฒ apรณ dit che gรฒ quater piante de dat embecile, ve a tรถle no?! Eh casso perรฒ figa.",
    "C'รจ uno sbirro tra di noi..."
]
