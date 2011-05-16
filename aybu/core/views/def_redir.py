import locale
import logging
from babel import Locale
from pyramid.httpexceptions import HTTPMovedPermanently

from aybu.core.model.entities import Page
import aybu.core.lib.helpers as helpers
from . utils import setup_template_context


def default_redirect(context, request):
    setup_template_context(None, request)
    available_locales = []
    log = logging.getLogger('{0}.default_redirect'.format(__name__))
    for language in request.tmpl_context.languages:
        try:
            loc = helpers.locale_from_language(language)
            available_locales.append(str(loc))
        except:
            pass

        try:
            loc = helpers.locale_from_language(language, language_only=True)
            l = str(loc)
            if l not in available_locales:
                available_locales.append(l)
        except Exception:
            pass

    preferred_languages = []
    for lang in request.languages:
        sep = '_'
        if lang > 2:
            if lang.find('-') != -1:
                sep = '-'
        try:
            loc = Locale.parse(lang, sep)
            preferred_languages.append(str(loc))
        except Exception as e:
            log.debug('Unable to parse %s locale : %s', lang, e)


    # The previous cycle could be (but in this case there is no control)
    # substituted by
    # preferred_languages = request.languages

    log.debug('Preferred languages %s', preferred_languages)
    negotiated = Locale.negotiate(preferred_languages, available_locales)

    if not negotiated:
        # No match beetween requested and available.
        # First try to search if we have a language preferred by the
        # client that has the same country as one of those that are
        # available i.e. we have en_GB and client requested en_US,
        # no match, but we can serve en_GB
        for lang in preferred_languages:
            for avail in available_locales:
                if lang[0:2] == avail[0:2]:
                    negotiated = avail
                    break

    log.debug('Negotiated language is %s', negotiated)

    if not negotiated:
        # No match, again.
        # Using the firt language on DB
        log.debug('Getting the first availble on DB')
        db_lang = request.tmpl_context.languages_proxy[0]
        # FIX ME: This can fail
        negotiated = helpers.locale_from_language(db_lang)

    else:
        lan = str(negotiated)
        if len(lan) > 2:
            lang = lan[0:2]
            country = lan[3:5]
        else:
            lang = lan
            country = lan

        try:
            db_lang = request.tmpl_context.\
                        languages_proxy.get_by(lang[0:2], country)
        except:
            log.exception("Error")
            db_lang = request.tmpl_context.languages_proxy[0]

    lan = str(negotiated)
    request.set_language(lan)

    try:
        l = '%s.UTF8' % (lan)
        log.debug('Setting locale to %s', l)
        locale.setlocale(locale.LC_ALL, l)
    except Exception as e:
        log.exception('Error setting locale %s', l)

    try:
        root = request.tmpl_context.menus[0]
        return HTTPMovedPermanently(location=root.pages[0][db_lang].url)
    except IndexError:
        return HTTPMovedPermanently(location=Page.query.first()[db_lang].url)
    except:
        log.exception("Unkown error")
        return HTTPMovedPermanently(location=Page.query.first()[db_lang].url)

