def extract_emoji(txt):

	msg = ""
	for emo in txt:
		if emo in emoji:
			msg += emo

	tokens = txt.split(' ')
	print(tokens)
	print(smileys.keys())
	for smiley in tokens:
		if smiley in smileys.keys():
			msg += smileys[smiley]

	return msg

print(extract_emoji(":D"))