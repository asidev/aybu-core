<%def name="css()">
	${parent.css()}
	${self.css_link('/css/form.css')}
	${self.css_link('/css/contacts.css')}
</%def>

<%def name="js()">
	${parent.js()}
	${self.js_link('/js/lib/jquery/jquery.validate.js')}

	% if c.settings.debug == True:
	${self.js_link('/js/contacts.js')}
	${self.js_link('/js/lib/jquery/jquery.validate-message_it.js')}
	% else:
	${self.js_link('/js/contacts.min.js')}
	${self.js_link('/js/lib/jquery/jquery.validate-message_it.min.js')}
	% endif
</%def>

<%inherit file="/inner_layout.mako"/>


<div id="editable_content">
	${h.literal(c.translation.content)}
</div>
<div>
	%if c.result_message :
	%if c.success :
	<h4 class="success">
	%else:
	<h4 class="error">
	%endif
		${c.result_message}
	</h4>
	%endif

	<form id="form" method="post" action="${request.environ.get('PATH_INFO')}">
		<fieldset>
			<label for="name">${_(u'Nome')}: </label>
			<input id="name" name="name" type="text"
				% if c.name and not c.success:
					value="${c.name}"
				% endif
				/>
			% if c.error['name']:
			<label for="name" class="error" generated="true">${c.error['name']}</label>
			% endif

			<label for="surname">${_(u'Cognome')}: </label>
			<input id="surname" name="surname" type="text"
				% if c.surname and not c.success:
					value="${c.surname}"
				% endif
				/>
			% if c.error['surname']:
			<label for="surname" class="error" generated="true">${c.error['surname']}</label>
			% endif

			<label for="phone">${_(u'Telefono')}: </label>
			<input id="phone" name="phone" type="text"
				% if c.phone and not c.success:
					value="${c.phone}"
				% endif
				/>
			% if c.error['phone']:
			<label for="phone" class="error" generated="true">${c.error['phone']}</label>
			% endif

			<label for="email">${_(u'E-mail')}: </label>
			<input id="email" name="email" type="text"
				% if c.email and not c.success:
					value="${c.email}"
				% endif
				/>
			% if c.error['email']:
			<label for="email" class="error" generated="true">${c.error['email']}</label>
			% endif

			<label for="message">${_(u'Messaggio')}: </label>
			% if c.message and not c.success:
			<textarea id="message" name="message" cols="2" rows="2">${c.message}</textarea>
			% else:
			<textarea id="message" name="message" cols="2" rows="2"></textarea>
			% endif

			% if c.error['message']:
			<label for="message" class="error" generated="true">${c.error['message']}</label>
			% endif

			<div id="privacy_policy">
				<p>
					${h.literal(_(u"%s informa i visitatori del proprio sito di provvedere alla tutela dei dati personali nel rispetto ed in conformit&agrave; alle vigenti norme sulla privacy (Codice in materia di protezione dei dati personali - D.Lgs. n.196/2003)." % (c.settings['site_title'])))}
				</p>
				<p>
					${h.literal(_(u"Quando l'utente visita il sito, la sua presenza &egrave; anonima. Le informazioni personali, quali il nome o l'indirizzo e-mail, non vengono raccolte mentre si visita il medesimo."))}
				</p>
				<p>
					${h.literal(_(u"I dati personali dell'utente vengono dallo stesso forniti sul sito soltanto tramite la compilazione di form per l'accesso a servizi specifici."))}
				</p>
				<p>
					${h.literal(_(u"In tal caso i dati personali forniti sono raccolti e trattati in modo cartaceo ed elettronico solo nel caso in cui l'utente fornisca il proprio consenso ed al solo fine dell'erogazione del servizio in oggetto."))}
				</p>
				<p>
					${h.literal(_(u"All'interessato che fornisce i propri dati personali per le finalit&agrave; anzidette &egrave; assicurato il rispetto dei diritti riconosciutigli dall'art.7 del D.Lgs. n.196/2003."))}
				</p>
				<p>
					${h.literal(_(u"%s ha identificato il proprio responsabile del trattamento dei dati ai sensi dell'art.29 del citato Codice in materia di protezione dei dati personali (D.Lgs. n.196/2003)." % (c.settings['site_title'])))}
				</p>
			</div>

			<div class="agreement">
				<label for="agreement">${_(u'Accetto i termini di Privacy')}</label>
				<input id="agreement" name="agreement" type="checkbox" />
				% if c.error['agreement']:
				<label for="agreement" class="error" generated="true">${c.error['agreement']}</label>
				% endif
				<div class="reset">&nbsp;</div>
			</div>

			<label for="captcha">
				${_(u"Inserisci il testo che vedi nell'immagine sottostante rispettando maiuscole e minuscole:")}
			</label>
			${h.captcha()}
			<input id="captcha" name="captcha" type="text" />
			% if c.error['captcha']:
			<label for="captcha" class="error" generated="true">${c.error['captcha']}</label>
			% endif

			<input class="submit" id="submit" value="${_(u'Invia')}"
				title="${_(u'Invia il messaggio')}" type="submit" />
		</fieldset>
	</form>
</div>
