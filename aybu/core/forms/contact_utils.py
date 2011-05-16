#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging
import re

from aybu.cms.model.entities import Setting
import makako.validator as v
from pymailer.mail import Mail

log = logging.getLogger(__name__)


def validate_name(request, value, field):
    ctx = request.tmpl_context
    _ = request.translate
    pattern = "[(0-9@*(\)[\]+.,/?:;\"`~\\#$%^&<>)+]"
    compiled = re.compile(pattern)
    if compiled.search(value) is None:
        if len(value) < 2:
            ctx.error[field] = _(u"Inserisci almeno 2 caratteri.")
            ctx.success = False
    else:
        ctx.error[field] = _(u"Numeri o caratteri speciali non sono ammessi.")
        ctx.success = False


def validate_message(request, message):
    ctx = request.tmpl_context
    _ = request.translate
    if len(ctx.message) < 10:
        ctx.error['message'] = _(u"Inserisci almeno 10 caratteri.")
        ctx.success = False


def validate_captcha(request, value):
    ctx = request.tmpl_context
    try:
        if value != request.session['captcha']:
            raise Exception()
    except:
        ctx.error['captcha'] = request.translate(
                               u"Il testo da lei inserito non corrisponde con "
                                 "quello visualizzato nell'immagine. "
                                 "La preghiamo di riprovare.")
        ctx.success = False


def contact(request):
    log.debug("Building contacts form")
    ctx = request.tmpl_context
    _ = request.translate
    ctx.error = {}
    ctx.name = request.params.get('name', '').title()
    ctx.error['name'] = ''
    ctx.surname = request.params.get('surname', '').title()
    ctx.error['surname'] = ''
    ctx.email = request.params.get('email', '')
    ctx.error['email'] = ''
    ctx.phone = request.params.get('phone', '')
    ctx.error['phone'] = ''
    agreement = request.params.get('agreement', '')
    ctx.error['agreement'] = ''
    ctx.message = request.params.get('message', '')
    ctx.error['message'] = ''
    captcha = request.params.get('captcha', '')
    ctx.error['captcha'] = ''
    ctx.vars = {}

    ctx.result_message = None
    ctx.success = True

    # FIXME: why old "submit" value is not submitted by the form?
    #if request.params.get('submit', False):
    if len(request.params):
        log.debug("Form has been submitter, validating fields")
        validate_name(request, ctx.name, 'name')
        validate_name(request, ctx.surname, 'surname')

        if not v.validate_email_address(ctx.email):
            ctx.error['email'] = _(u"Inserisci un indirizzo email valido.")
            ctx.success = False

        if not v.validate_phone_number(ctx.phone):
            ctx.error['phone'] = _(u"Inserisci un numero di telefono valido.")
            ctx.success = False

        validate_message(request, ctx.message)

        if not agreement == 'on':
            ctx.error['agreement'] = _(u"Devi accettare i termini di Privacy")
            ctx.success = False

        validate_captcha(request, captcha)

        emails = Setting.query\
                 .filter(Setting.name.like(u'contact_dst_email_%')).all()

        for email in emails:
            log.debug("Adding recipient '<%s>'", email.value)
            mail = Mail()
            mail.setSubject(u"Nuovo messaggio dal form di contatto web")

            mail.setRecipient(email.value)

            mail.setSender(request.POST['email'])
            message = u"Nome : %s \n" % (ctx.name)
            message = u"%sCognome : %s \n" % (message, ctx.surname)
            message = u"%sTelefono : %s \n\n" % (message, ctx.phone)

            for key, value in request.params.iteritems():
                if key not in ('name', 'surname', 'email', 'phone',
                                 'agreement', 'message', 'captcha',
                                 'submit'):
                    p = key.decode('utf8')
                    message = u"%s%s : %s \n" % (message, p.title(), value)
                    ctx.vars[key] = value

            message = u"%sMessaggio : \n%s\n" % (message, ctx.message)
            mail.attachTextMessage(message)

        if ctx.success:
            log.debug('Form is valid, sending emails')
            try:
                mail.send()
                ctx.result_message = _(u"Grazie per averci contattato. " +\
                                     u"Le risponderemo al più presto.")
            except  Exception as e:
                log.exception("Errore nell'invio del messaggio. \n%s", e)
                ctx.result_message = _(u"Errore nell'invio del messaggio. " +\
                                     u"Si prega di riprovare più tardi.")
                ctx.success = False
        else:
            ctx.result_message = _(u"Errore nell'invio del form. "
                                 "Ricontrollare i campi e riprovare.")
