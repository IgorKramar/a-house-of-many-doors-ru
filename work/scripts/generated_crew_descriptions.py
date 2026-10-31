"""Build exact visible crew descriptions from translated, source-attested pieces.

Descriptions are concatenated before reaching the text renderer. Translating
only the individual pieces therefore leaves wounded/low-sanity variants in English.
Never generate a description until every nonempty component is translated.
"""
import re,json,itertools

def add_crew_descriptions(mapping,work):
    report={}
    for path in sorted((work/'source/CodeEntries').glob('gml_Script_*Dialogue.gml')):
        source=path.read_text(encoding='utf-8-sig')
        if 'CharacterDescription = SpecificDescription + WoundDescription + SanityDescription;' not in source:continue
        pieces={}
        for variable in ['SpecificDescription','WoundDescription','SanityDescription']:
            literals=re.findall(r'\b'+variable+r'''\s*=\s*("[^"]*"|'[^']*')\s*;''',source)
            pieces[variable]=list(dict.fromkeys(x[1:-1] for x in literals))
        if not all(pieces.values()):continue
        if any(s and s not in mapping for values in pieces.values() for s in values):continue
        count=0
        for values in itertools.product(*pieces.values()):
            mapping[''.join(values)]=''.join(mapping[s] if s else '' for s in values)
            count+=1
        report[path.stem]=count
    (work/'build/crew-description-coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
