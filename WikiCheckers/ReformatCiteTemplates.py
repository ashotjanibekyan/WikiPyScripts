import mwparserfromhell
import pywikibot
import pywikibot.data.api as api

from WikiCheckers.WikiChecker import WikiChecker


class ReformatCiteTemplates(WikiChecker):
    def __init__(self, site: pywikibot.Site):
        super().__init__(site)
        self.temps = ['Cite web', 'Cite book', 'Cite journal', 'Cite news']
        self.DATA = {}
        for cite_name in self.temps:
            self.DATA[cite_name] = self.get_cite_data(cite_name)

    def get_cite_data(self, name):
        req = api.Request(site=self.site, parameters={
            "action": "templatedata",
            "format": "json",
            "titles": "Template:" + name,
            "formatversion": "2"
        })

        r = req.submit()
        id = next(iter(r['pages']))
        cite_order = r['pages'][id]['paramOrder']
        cite_aliases = {}
        params = r['pages'][id]['params']
        for param in params:
            if 'aliases' in params[param]:
                cite_aliases[param] = params[param]['aliases']
            else:
                cite_aliases[param] = []
        return cite_order, cite_aliases

    def format_template(self, temp: mwparserfromhell.wikicode.Template, ordered_params, aliases, name):
        old_str = str(temp)
        temp.name = name + " "
        params = {}
        all_params = list(temp.params)
        for param in all_params:
            name = str(param.name).strip()
            val = str(param.value).strip()
            if val:
                params[name] = val
            temp.remove(param)

        for param in ordered_params:
            if param in params and params[param]:
                temp.add(param, params[param] + ' ', preserve_spacing=False)
                params.pop(param, None)
            for al in aliases[param]:
                if al in params and params[al]:
                    temp.add(al, params[al] + ' ', preserve_spacing=False)
                    params.pop(al, None)
        keys = sorted(set(params.keys()))
        for param in keys:
            temp.add(param, params[param] + ' ', preserve_spacing=False)
            params.pop(param, None)
        if len(temp.params) == 0:
            return False
        temp.params[-1].value = str(temp.params[-1].value).strip()
        new_str = str(temp)
        return old_str != new_str

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        changed_temps = []
        for t in parsed.filter_templates():
            t: mwparserfromhell.wikicode.Template
            for temp in self.temps:
                if t.name.matches(temp):
                    if self.format_template(t, self.DATA[temp][0], self.DATA[temp][1], temp):
                        changed_temps.append(temp)
        changed_temps = list(set(changed_temps))
        if len(changed_temps) == 1:
            return str(parsed), changed_temps[0] + ' կաղապարի ձևաչափի ուղղում'
        elif len(changed_temps) > 1:
            return str(parsed), ', '.join(changed_temps[:-1]) + ' և ' + changed_temps[-1] + ' կաղապարների ձևաչափի ուղղում'
        return None, None
