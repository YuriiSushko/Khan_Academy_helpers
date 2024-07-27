import polib


pot_file_path = 'learn.math.algebra-basics.articles-uk.po'
pot = polib.pofile(pot_file_path)

for entry in pot:
    print(f'Msgid: {entry.msgid}')
    print(f'Msgstr: {entry.msgstr}')

