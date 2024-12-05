$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/fix_redirects.py

$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py redirect br -delete -always -site:wikipedia -lang:hyw -sdtemplate:"{{Ջնջել|կոտրված վերահղում}}"
$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py redirect double -always -site:wikipedia -lang:hyw
