import mwparserfromhell
import pywikibot
import pywikibot.data.api as api

from WikiCheckers.WikiChecker import WikiChecker


class ReformatTemplates(WikiChecker):
    def __init__(self, site: pywikibot.Site, reformat_data):
        super().__init__(site)
        self.temps = list(reformat_data.keys())
        self.DATA = {}
        self.redirect_map = {}

        for tt in self.temps:
            t = pywikibot.Page(self.site, 'Template:' + tt)
            redirects = t.backlinks(filter_redirects=True)
            for r in redirects:
                self.redirect_map[r.title(with_ns=False)] = tt

        for cite_name in reformat_data:
            self.DATA[cite_name] = self.get_cite_data(cite_name)
            self.DATA[cite_name].append(reformat_data[cite_name] == 'inline')

    def resolve_temp_name(self, name: str):
        name = name.strip()
        name = name[0].upper() + name[1:]
        if name in self.temps:
            return name
        if name in self.redirect_map:
            return self.redirect_map[name]
        return None

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
        return [cite_order, cite_aliases]

    def format_template(self, temp: mwparserfromhell.wikicode.Template, ordered_params, aliases, name, is_inline):
        old_str = str(temp)
        after = ' ' if is_inline else '\n'
        before = '' if is_inline else ' '
        temp.name = name + after
        params = {}
        all_params = list(temp.params)
        for param in all_params:
            name = str(param.name).strip()
            val = str(param.value).strip()
            if val or not is_inline:
                params[name] = val
            temp.remove(param)

        for param in ordered_params:
            if param in params:
                temp.add(before + param + before, before + params[param] + after, preserve_spacing=False)
                params.pop(param, None)
            for al in aliases[param]:
                if al in params:
                    temp.add(before + al + before, before + params[al] + after, preserve_spacing=False)
                    params.pop(al, None)
        keys = sorted(set(params.keys()))
        for param in keys:
            temp.add(before + param + before, before + params[param] + after, preserve_spacing=False)
            params.pop(param, None)
        if len(temp.params) == 0:
            temp.name = name
        if is_inline and len(temp.params) > 0:
            temp.params[-1].value = str(temp.params[-1].value).strip()
        new_str = str(temp)
        return old_str != new_str

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        changed_temps = []
        for t in parsed.filter_templates():
            t: mwparserfromhell.wikicode.Template
            name = self.resolve_temp_name(str(t.name))
            if name:
                if self.format_template(t, self.DATA[name][0], self.DATA[name][1], name, self.DATA[name][2]):
                    changed_temps.append(name)

        changed_temps = list(set(changed_temps))
        if len(changed_temps) == 1:
            return str(parsed), changed_temps[0] + ' կաղապարի ձևաչափի ուղղում'
        elif len(changed_temps) > 1:
            return str(parsed), ', '.join(changed_temps[:-1]) + ' և ' + changed_temps[-1] + ' կաղապարների ձևաչափի ուղղում'
        return None, None
