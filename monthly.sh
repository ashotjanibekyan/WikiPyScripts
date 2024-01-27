toolforge jobs run potd-move --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/potd" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run dead-people-without-image.py --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/dead_people_without_image.py" --image python3.11 --emails onfailure --wait 7200
toolforge jobs run math-project-views --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/math_project_views" --image python3.11 --emails onfailure --wait 7200
toolforge jobs run short-articles --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/short_articles" --image python3.11 --emails onfailure --wait 7200
toolforge jobs run vital-subject --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/vital_subject" --image python3.11 --emails onfailure --wait 7200
