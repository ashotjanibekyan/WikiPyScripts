toolforge jobs run admin-stats --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/adminstats" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run almost-uncat-atricles --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/almost_uncat_atricles" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run col-2-ver --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py replace -fix:col2ver -ns:0 -recentchanges -always" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run del-draft --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/del_draft" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run most-linked-missing-articles --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/most_linked_missing_articles" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run non-free-images --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/non_free_images" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run number-of --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/numberof" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run old-unsource --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/old_unsource" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run only-red-categories --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/only_red_categories" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run orphaned-talk --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/orphaned_talk" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run probably-dead-people --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/probably_dead_people" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run translated-from-unsource --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/translated_from_unsource" --image python3.11 --emails onfailure --wait 1800
toolforge jobs run userpage-cats --command "$HOME/pwbvenv/bin/python3 $HOME/pywikibot-core/pwb.py $HOME/WikiPyScripts/userpage_cats" --image python3.11 --emails onfailure --wait 1800