import re

import pywikibot
import mwparserfromhell

from WikiCheckers.WikiChecker import WikiChecker


class FixCiteTemplates(WikiChecker):

    def __init__(self, site: pywikibot.Site, cite_templates):
        super().__init__(site)

        cite_redirects = []
        for tt in cite_templates:
            t = pywikibot.Page(self.site, 'Template:' + tt)
            redirects = t.backlinks(filter_redirects=True)
            for r in redirects:
                cite_redirects.append(r.title(with_ns=False))

        self.cite_templates = set(cite_templates + cite_redirects)

    def check_url_status(self, template, summaries):
        param = None
        if template.has('deadlink'):
            param = template.get('deadlink')
        if template.has('dead-url'):
            param = template.get('dead-url')
        if template.has('dead-link'):
            param = template.get('dead-link')
        if template.has('deadurl'):
            param = template.get('deadurl')
        if not param:
            return

        if param.value.strip().lower() == 'no' or param.value.strip().lower() == 'no':
            template.remove(param)
            template.add('url-status', 'live')
            summaries.append('-' + str(param) + ', +' + str(template.get('url-status')))
        elif param.value.strip().lower() == 'yes' or param.value.strip().lower() == '404':
            template.remove(param)
            template.add('url-status', 'dead')
            summaries.append('-' + str(param) + ', +' + str(template.get('url-status')))
        elif param.value.strip().lower() == '':
            template.remove(param)
            summaries.append('-' + str(param))

    @staticmethod
    def merge_month_year(template: mwparserfromhell.wikicode.Template, sms):
        if template.has('month') and template.has('year') and not template.has('date'):
            month = template.get('month')
            year = template.get('year')
            template.remove(month)
            template.remove(year)
            template.add('date', f'{str(month.value).strip()} {str(year.value).strip()}')
            sms.append(f'-{month} {year}, +{template.get("date")}')

    def replace_param(self, template, to_name, from_name, sms):
        if template.has(from_name):
            param = template.get(from_name)
            self._replace_param(template, param, to_name, sms)

    @staticmethod
    def _replace_param(template, param, to, sms):
        template.remove(param)
        if template.has(to):
            sms.append('-' + str(param).strip() + ', քանի որ կա ' + str(template.get(to)).strip())
        else:
            template.add(to, param.value.strip())
            sms.append('-' + str(param).strip() + ', +' + str(template.get(to)).strip())

    @staticmethod
    def fix_coauthors(template: mwparserfromhell.wikicode.Template, sms):
        coauthors = None
        if template.has('coauthors'):
            coauthors = template.get('coauthors')
        if template.has('coauthor'):
            coauthors = template.get('coauthor')
        if not coauthors:
            return

        last_index = 0
        if template.has('author') or template.has('last') or template.has('first') or \
                template.has('author1') or template.has('last1') or template.has('first1'):
            last_index = 1
        while template.has(f'author{last_index+1}') or template.has(f'last{last_index+1}') or template.has(f'first{last_index+1}'):
            last_index += 1
        template.add(f'author{last_index+1}', str(coauthors.value).strip())
        template.remove(coauthors)
        sms.append(f"-{coauthors} +{template.get(f'author{last_index+1}')}")

    @staticmethod
    def remove_param(template, name, sms):
        if template.has(name):
            param = template.get(name)
            template.remove(param)
            sms.append(f'-{str(param).strip()}')


    @staticmethod
    def remove_external_link(template, name, sms):
        if template.has(name):
            param = template.get(name)
            if not re.match(r"^https?://([^/]+)/?$", str(param.value).strip()):
                return
            old = str(param)
            val = re.sub(r"^https?://([^/]+)/?$", r"\1", str(param.value).strip())
            param.value = val
            sms.append('-' + old + ' +' + str(param))

    def execute(self, text: str, parsed: mwparserfromhell.wikicode) -> (str, str):
        summaries = []
        for template in parsed.filter_templates(recursive=True):
            template: mwparserfromhell.wikicode.Template
            for temp in self.cite_templates:
                if not template.name.matches(temp):
                    continue
                self.replace_param(template, 'access-date', 'aCCESSDATE', summaries)
                self.replace_param(template, 'access-date', 'accesdsate', summaries)
                self.replace_param(template, 'access-date', 'accesso', summaries)
                self.replace_param(template, 'access-date', 'accesssdate', summaries)
                self.replace_param(template, 'access-date', 'accssdate', summaries)
                self.replace_param(template, 'access-date', 'aessdate', summaries)
                self.replace_param(template, 'access-date', 'data dostępu', summaries)
                self.replace_param(template, 'access-date', 'fechaacceso', summaries)
                self.replace_param(template, 'access-date', 'hämtdatum', summaries)
                self.replace_param(template, 'agency', 'opublikowany', summaries)
                self.replace_param(template, 'archive-date', 'arkivdatum', summaries)
                self.replace_param(template, 'archive-url', 'arkivurl', summaries)
                self.replace_param(template, 'archive-url', 'urlarchivo', summaries)
                self.replace_param(template, 'archivedate', 'zarchiwizowano', summaries)
                self.replace_param(template, 'archiveurl', 'archiwum', summaries)
                self.replace_param(template, 'author1', 'auteur1', summaries)
                self.replace_param(template, 'author2', 'auteur2', summaries)
                self.replace_param(template, 'author3', 'auteur3', summaries)
                self.replace_param(template, 'author4', 'auteur4', summaries)
                self.replace_param(template, 'author5', 'auteur5', summaries)
                self.replace_param(template, 'author', 'Author', summaries)
                self.replace_param(template, 'author', 'auteur', summaries)
                self.replace_param(template, 'author', 'автор', summaries)
                self.replace_param(template, 'author', 'autor', summaries)
                self.replace_param(template, 'author', 'հեղինակ', summaries)
                self.replace_param(template, 'chapter-url', 'chapterurl', summaries)
                self.replace_param(template, 'date', 'data', summaries)
                self.replace_param(template, 'date', 'datepublished', summaries)
                self.replace_param(template, 'date', 'fecha', summaries)
                self.replace_param(template, 'date', 'ամսաթիվ', summaries)
                self.replace_param(template, 'editor', 'editore', summaries)
                self.replace_param(template, 'editor', 'éditeur', summaries)
                self.replace_param(template, 'editor-link', 'editorlink', summaries)
                self.replace_param(template, 'editor-link1', 'editorlink1', summaries)
                self.replace_param(template, 'editor-link2', 'editorlink2', summaries)
                self.replace_param(template, 'editor-link3', 'editorlink3', summaries)
                self.replace_param(template, 'episode-link', 'episodelink', summaries)
                self.replace_param(template, 'first', 'first name', summaries)
                self.replace_param(template, 'format', 'Формат', summaries)
                self.replace_param(template, 'lang', 'lingua', summaries)
                self.replace_param(template, 'lang', 'язык', summaries)
                self.replace_param(template, 'lang', 'lingua2', summaries)
                self.replace_param(template, 'language', 'idioma', summaries)
                self.replace_param(template, 'language', 'langue', summaries)
                self.replace_param(template, 'last', 'last name', summaries)
                self.replace_param(template, 'last1', 'nom1', summaries)
                self.replace_param(template, 'last2', 'nom2', summaries)
                self.replace_param(template, 'last3', 'nom3', summaries)
                self.replace_param(template, 'last4', 'nom4', summaries)
                self.replace_param(template, 'location', 'lieu', summaries)
                self.replace_param(template, 'month', 'mois', summaries)
                self.replace_param(template, 'pages', 'passage', summaries)
                self.replace_param(template, 'pages', 'էջեր', summaries)
                self.replace_param(template, 'pages', 'Էջեր', summaries)
                self.replace_param(template, 'publisher', 'Publisher', summaries)
                self.replace_param(template, 'publisher', 'piblisher', summaries)
                self.replace_param(template, 'publisher', 'pubisher', summaries)
                self.replace_param(template, 'publisher', 'publesher', summaries)
                self.replace_param(template, 'publisher', 'publicación', summaries)
                self.replace_param(template, 'publisher', 'publidher', summaries)
                self.replace_param(template, 'publisher', 'publiher', summaries)
                self.replace_param(template, 'publisher', 'publishe', summaries)
                self.replace_param(template, 'publisher', 'հրատարակիչ', summaries)
                self.replace_param(template, 'series-link', 'serieslink', summaries)
                self.replace_param(template, 'subject-link', 'subjectlink', summaries)
                self.replace_param(template, 'subject-link1', 'subjectlink1', summaries)
                self.replace_param(template, 'subject-link2', 'subjectlink2', summaries)
                self.replace_param(template, 'subject-link3', 'subjectlink3', summaries)
                self.replace_param(template, 'title', 'name', summaries)
                self.replace_param(template, 'title', 'nimeke', summaries)
                self.replace_param(template, 'title', 'titel', summaries)
                self.replace_param(template, 'title', 'titel', summaries)
                self.replace_param(template, 'title', 'titolo', summaries)
                self.replace_param(template, 'title', 'titre', summaries)
                self.replace_param(template, 'title', 'titulo', summaries)
                self.replace_param(template, 'title', 'tytuł', summaries)
                self.replace_param(template, 'title', 'título', summaries)
                self.replace_param(template, 'title', 'Անվանում', summaries)
                self.replace_param(template, 'title', 'Վերնագիր', summaries)
                self.replace_param(template, 'title', 'աերնագիր', summaries)
                self.replace_param(template, 'title', 'վերնագիր', summaries)
                self.replace_param(template, 'trans-title', 'trans_title', summaries)
                self.replace_param(template, 'website', 'site', summaries)
                self.replace_param(template, 'website', 'sitio web', summaries)
                self.replace_param(template, 'website', 'sitioweb', summaries)
                self.replace_param(template, 'website', 'կայք', summaries)
                self.replace_param(template, 'website', 'վեբկայք', summaries)
                self.replace_param(template, 'work', 'obra', summaries)
                self.replace_param(template, 'year', 'année', summaries)

                self.remove_external_link(template, 'website', summaries)
                self.remove_external_link(template, 'work', summaries)

                self.remove_param(template, 'subtitle', summaries)
                self.remove_param(template, 'présentation en ligne', summaries)

                self.check_url_status(template, summaries)
                self.merge_month_year(template, summaries)
                self.fix_coauthors(template, summaries)

        return str(parsed), ', '.join(list(set(summaries)))
