/**
 * stackcone.com contact form → hello@stackcone.com
 *
 * Google Apps Script web app that receives the /contact/ form POST and emails
 * it to the inbox from the Google Workspace account that deploys it.
 * Not published with the site (scripts/ is stripped in prepare-pages.sh).
 *
 * Setup (signed in as hello@stackcone.com):
 *   1. https://script.google.com → New project → paste this file into Code.gs → Save.
 *   2. Deploy → New deployment → type "Web app".
 *        Execute as:     Me (hello@stackcone.com)
 *        Who has access: Anyone
 *   3. Authorize when prompted, then copy the Web app URL (ends in /exec).
 *   4. Put that URL in the form's action attribute in contact/index.html.
 *
 * After editing this script: Deploy → Manage deployments → Edit → Version: New version.
 * (Keeps the same /exec URL, so the site does not need to change.)
 */

const TO = 'hello@stackcone.com';

function doPost(e) {
  const p = (e && e.parameter) || {};

  // Honeypot filled in → bot. Pretend success so it doesn't retry.
  if (p._gotcha) return json({ ok: true });

  const name = clean(p.name, 200);
  const email = clean(p.email, 320);
  const company = clean(p.company, 200);
  const projectType = clean(p.project_type, 100) || 'Other';
  const message = clean(p.message, 10000);

  if (!name || !message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: 'Please fill in your name, a valid email and a message.' });
  }

  const body = [
    'New enquiry from stackcone.com/contact',
    '',
    'Name:         ' + name,
    'Email:        ' + email,
    'Company:      ' + (company || '—'),
    'Project type: ' + projectType,
    '',
    'Message:',
    message,
    '',
    '—',
    'Reply to this email to respond to ' + name + ' directly.',
  ].join('\n');

  try {
    MailApp.sendEmail({
      to: TO,
      replyTo: email,
      name: 'stackcone website',
      subject: 'New enquiry: ' + name + (company ? ' (' + company + ')' : '') + ' — ' + projectType,
      body: body,
    });
  } catch (err) {
    console.error(err);
    return json({ ok: false, error: 'Could not send your message. Please email hello@stackcone.com directly.' });
  }

  return json({ ok: true });
}

// Lets you open the /exec URL in a browser to check the deployment is live.
function doGet() {
  return json({ ok: true, service: 'stackcone contact form' });
}

function clean(value, max) {
  return String(value || '').trim().slice(0, max);
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
