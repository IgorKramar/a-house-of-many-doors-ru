import pathlib,re,json,hashlib
root=pathlib.Path(__file__).resolve().parents[2]/'work'
atom=r'''(?:"[^"]*"|'[^']*')'''
chain=re.compile(atom+r'(?:\s*\+\s*'+atom+r')*')
single=re.compile(atom)
groups={
'help':['gml_Object_oTutorial_Draw_64'],
'arrival':['gml_Script_CityOfKeysBeforeFirstScreenEvent','gml_Script_WalkingKeysStreetsFirstTime'],
'city':['gml_Object_oCityOfKeysDialogueBox_Draw_64'],
'ui':['gml_Script_CargoTab','gml_Script_LogbookTab','gml_Script_EngineTab','gml_Script_ShopsTab','gml_Script_SavingAndLeaving'],
'inventory':['gml_Object_oInventories_Create_0'],
'press':['gml_Script_'+s for s in [
    'HollowTrumpetLetterEvent','KeyDetailsLetterEvent','PioneerLetterEvent',
    'HollowTrumpetPositionEvent','KeyDetailsPositionEvent','PioneerPositionEvent',
    'HollowTrumpetFirstAssignmentEvent','KeyDetailsFirstAssignmentEvent','PioneerFirstAssignmentEvent',
    'CompletedHollowTrumpetAssignmentEvent','CompletedKeyDetailsAssignmentEvent','CompletedPioneerAssignmentEvent',
    'DecidingNewspaperWhenFreelanceEvent','FreelanceReportEvent',
    'SubmittingToHollowTrumpetEvent','SubmittingToKeyDetailsEvent','SubmittingToPioneerEvent',
    'SubmittingToHollowTrumpetPostFreelanceEvent','SubmittingToKeyDetailsPostFreelanceEvent','SubmittingToPioneerPostFreelanceEvent',
    'SubmittingToKeyDetailsPostEditorEvent','HollowTrumpetOffice','KeyDetailsOffice','KeyDetailsOffice2','PioneerOffice',
    'NewAssignmentKeyDetails',
]],
'citylife':['gml_Script_'+s for s in [
    'DwellingsEvent','DwellingsEvent2','TakingAMonthOffEvent',
    'CityOfKeysSanityRecoveryEvent','HullRepairEvent','TryingToLeaveCityButOverweight',
    'AdvertisingForCrewEvent','NewspaperAdvertEvent','PosterAdvertEvent',
    'HostingGuestsEvent','EntertainGuestEvent','CityOfKeysNewsEvent',
    'VisitBlackMarketEvent','BlackMarketPartnersEvent','BlackMarketBuyEvent','BlackMarketBuyEvent2',
    'BlackMarketBuyEvent3','BlackMarketSellEvent','BlackMarketSellEvent2','BlackMarketSellOptions','BlackMarketSellOptions2',
    'StashEvent','StashAdd','StashRemove',
]],
'keyquest':['gml_Script_'+s for s in [
    'KeyDetailsQuestMill','KeyDetailsQuestOldHallow','KeyDetailsQuestKeys','KeyDetailsQuestKennedy',
]],
'trumpetquest':['gml_Script_'+s for s in [
    'TrumpetQuestKeys','TrumpetQuestMill','TrumpetQuestKennedy','TrumpetQuestKeys2',
]],
'pioneerquest':['gml_Script_'+s for s in [
    'PioneerQuestKeys','PioneerQuestMasks','PioneerQuestGravespite','PioneerQuestPannachak','PioneerQuestCrumpett',
]],
'howling':['gml_Script_HowlingPitsEvent'+s for s in ['', '2','3','4','5','6','7']],
'institutions':['gml_Script_'+s for s in ['WitheringStreetEvent','ChurchLetterEvent','CollegeLetterEvent1','CollegeLetterEvent2','UnnamedSocietyCityOfKeysEvent']],
'museum':['gml_Script_'+s for s in ['MuseumQuestKeys','MuseumQuestKeys2','MuseumQuestProfit']],
'glassquest':['gml_Script_GlassQuestKeys','gml_Script_GlassQuestStar'],
'society':['gml_Script_'+s for s in ['UnnamedSocietyEvent','UnnamedSocietyHallowEvent','UnnamedSocietyGhoulwatchEvent','UnnamedSocietyFoundersFireEvent','UnnamedSocietyBridgesEvent']],
'mill':['gml_Object_oClaytonsMillDialogueBox_Draw_64','gml_Script_RecollectionClaytonsMillEvent'],
'hallow':['gml_Object_oTheOldHallowDialogueBox_Draw_64','gml_Script_OldHallowDrinks'],
'hallowcrew':['gml_Script_'+s for s in ['BanjoOldHallowEvent','PenpusherOldHallowEvent','PenpusherOldHallowEvent2','JudithOldHallowEvent','JudithOldHallowEvent2','ViolanteOldHallowEvent','TybaltOldHallowEvent']],
'wakers':['gml_Object_oWakersRespiteDialogueBox_Draw_64','gml_Script_ViolanteWakersRespiteEvent','gml_Script_ViolanteWakersRespiteEvent2'],
'nicholas':['gml_Script_'+s for s in ['NicholasClaytonsMillEvent','NicholasClaytonsMillEvent2','NicholasCityOfKeysEvent','NicholasCityOfKeysEvent2','NicholasCityOfKeysEvent3','NicholasCityOfKeysEvent4','NicholasByssusEvent']],
'nicholasdialogue':['gml_Script_NicholasDialogue'],
'fargyle':['gml_Object_oFargyleKeepDialogueBox_Draw_64','gml_Script_RansackFargyleKeepEvent','gml_Script_FargylePhobetorQuinnEvent'],
'fargylecrew':['gml_Script_'+s for s in ['CromlechFargyleKeepEvent','TybaltFargyleKeepEvent','FionaFargyleKeepEvent','JudithFargyleKeepEvent','JudithFargyleKeepEvent2','JudithFargyleKeepEvent3','BradleyFargyleKeepEvent']],
'startertalk':['gml_Script_'+s for s in ['BradleyDialogue','RotherfordDialogue','BanjoDialogue']],
'hallowtalk':['gml_Script_'+s for s in ['PenpusherDialogue','JudithDialogue','TybaltDialogue','ViolanteDialogue']],
'fargyletalk':['gml_Script_'+s for s in ['FionaDialogue','RansackDialogue','CromlechDialogue']],
'morecrew':['gml_Script_'+s for s in ['TeraDialogue','ViolaDialogue','SandyDialogue','FinneganDialogue','PanoramaDialogue','OttoDialogue','GilesDialogue','GustaveDialogue']],
'midcrew':['gml_Script_'+s for s in ['HarmonyDialogue','ValeriaDialogue','AugustusDialogue','PeterDialogue']],
'lorecrew':['gml_Script_'+s for s in ['AbbasDialogue','JackDialogue']],
'vanchtalk':['gml_Script_VanchDialogue'],
'elegantcrew':['gml_Script_GladysDialogue','gml_Script_GenevieveDialogue'],
'strangecrew':['gml_Script_LucettaDialogue','gml_Script_JhangBaShoDialogue'],
'ashentalk':['gml_Script_AshenDialogue'],
'bishoptalk':['gml_Script_BishopDialogue'],
'delgadotalk':['gml_Script_DrDelgadoDialogue'],
'chartalk':['gml_Script_CharDialogue'],
'spiretalk':['gml_Script_SpireDialogue'],
'ashenevents':['gml_Script_'+s for s in ['AshenBuzzardsOmenEvent','AshenCityOfBridgesEvent','AshenCityOfBridgesEvent2','AshenPhobetorQuinnEvent','AshenFightOptions']]+['gml_Object_oConsortiumKinetopedeDialogueBox_Draw_64'],
'bishopevents':['gml_Script_BishopNewFrontierEvent','gml_Object_oBishopScorpiopedeDialogueBox_Draw_64'],
'delgadoevents':['gml_Script_'+s for s in ['DelgadoEnginesEvent','DelgadoEnginesEvent2','DelgadoEnginesEvent3']]+['gml_Object_oDelgado'+s+'DialogueBox_Draw_64' for s in ['Orb','Kinetopede','Gigantopede']],
'spireevents':['gml_Script_Spire'+s+'Event' for s in ['Keys','Byssus','CityOfAngels','EldAbrathat','Ghoulwatch','Hextall','Misericord','Threshold']],
'charevents':['gml_Script_Char'+s+'Event' for s in ['CityOfBridges','CityOfKnives','CityOfMasks','PhobetorQuinn','Vex']]+['gml_Script_CharCityOfKnivesEvent2','gml_Script_CharPhobetorQuinnEvent2'],
'rotherfordevents':['gml_Script_RotherfordKeysEvent','gml_Script_RotherfordMasksEvent'],
'bradleyevents':['gml_Script_Bradley'+s+'Event' for s in ['Keys','Glitterberg','MistyFalls','PhobetorQuinn','Vex','Star']],
'banjoevents':['gml_Script_Banjo'+s+'Event' for s in ['Arozim','CityOfKnives','CityOfBridges','Carapas','BuzzardsOmen','FrogbitSmut','ScarsOfSheng','WasteDisposal']],
'penpusherevents':['gml_Script_PenpusherKelpFortressEvent','gml_Script_PenpusherKelpFortressEvent2','gml_Script_PenpusherFoundersFireEvent'],
'judithevents':['gml_Script_JudithCityOfMasksEvent','gml_Script_JudithCityOfMasksEvent2'],
'tybaltevents':['gml_Script_TybaltQuestKeys','gml_Script_TybaltVictoryEvent','gml_Object_oTybaltScorpiopedeDialogueBox_Draw_64'],
'violanteevents':['gml_Script_Violante'+s+'Event' for s in ['Skimmerskard','Pannachak','IcicleSpine','Calaram']],
'interface':['gml_Object_'+s+'_Draw_64' for s in ['oStartMenu','oPauseMenu','oCombatPauseMenu','oDialoguePauseMenu','oCredits']]+['gml_Script_'+s for s in ['DrawButtonsAtTheBottom','DrawCombatLog','DrawCombatPauseButton','DrawGauge','DrawHeartlightGUI','DrawLowerCrew','DrawPlayerPortrait','DrawCrewPortraits','DrawStats','WriteMemoirs','InputPlayerName','InputLowerCrewName','DrawMap','MapTab','CombatEndsPlayerFlees','CombatEndsPlayerDies','CombatEndsEnemyFlees','CombatEndsEnemyDies']],
}
for group,names in groups.items():
    if group=='interface':
        names += ['gml_Script_'+s for s in ['DrawMovementButtons','DrawWeaponButtons','DrawEnemyGauge','DrawFuelBar','DrawSanityBar','DrawEnemyWillBar','DrawMoney','LoadScreen','SaveSlotRectangleButtonPressed','TwitterButtonPressed','DrawNoctoscope','DrawTricksterItems','DrawMainQuestDreamBubble']]
        names += ['gml_Object_'+s for s in ['oCombat_Step_0','oCombat_Draw_0','oPausableCombat_Draw_64','oPausableCombat_Draw_0','oPausableGame_Draw_64']]
    entries={}
    for name in names:
        path=root/'source/CodeEntries'/(name+'.gml')
        if not path.exists():raise FileNotFoundError(f'{group}: missing source script {name}')
        source=path.read_text(encoding='utf-8-sig')
        for m in chain.finditer(source):
            t=''.join(a.group()[1:-1] for a in single.finditer(m.group()))
            if not re.search('[A-Za-z]',t) or len(t)<2:continue
            line=source.count('\n',0,m.start())+1
            if t not in entries:entries[t]={'id':group+'_'+str(len(entries)+1),'text':t,'code':name,'line':line}
    result=list(entries.values())
    (root/'source'/f'{group}_batch.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(group,len(result),sum(len(x['text'].split()) for x in result))
