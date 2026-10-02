/**
 * stackcone.com contact form → hello@stackcone.com
 *
 * Google Apps Script web app that receives the /contact/ form POST and emails
 * it (plus any attached files) to the inbox from the Google Workspace account
 * that deploys it.
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
const SENDER_NAME = 'Stackcone Inquiry';
const LOGO_URL = 'https://stackcone.com/logo/stackcone.png'; // 559×118, shown at 150×32
const TIME_ZONE = 'Asia/Kolkata';

// Attachments — keep in sync with contact/contact-form.js.
const MAX_FILES = 3;
const MAX_TOTAL_BYTES = 10 * 1024 * 1024;
const ALLOWED_EXT = /\.(pdf|docx?|pptx?|xlsx?|csv|txt|md|rtf|png|jpe?g|gif|webp|heic|zip)$/i;

// The email is quoted back to the visitor when you hit Reply, so everything in it
// is written to read well for them too (no internal notes).
const FONT = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;";

function doPost(e) {
  const p = (e && e.parameter) || {};

  // Honeypot filled in → bot. Pretend success so it doesn't retry.
  if (p._gotcha) return json({ ok: true });

  const inquiry = {
    name: oneLine(p.name, 200),
    email: oneLine(p.email, 320),
    company: oneLine(p.company, 200),
    projectType: oneLine(p.project_type, 100) || 'Other',
    message: String(p.message || '').replace(/\r\n?/g, '\n').trim().slice(0, 10000),
    receivedAt: Utilities.formatDate(new Date(), TIME_ZONE, "EEE, d MMM yyyy 'at' h:mm a 'IST'"),
  };

  if (!inquiry.name || !inquiry.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inquiry.email)) {
    return json({ ok: false, error: 'Please fill in your name, a valid email and a message.' });
  }

  const attachments = parseAttachments(p.attachments);
  if (attachments.error) return json({ ok: false, error: attachments.error });
  inquiry.attachments = attachments.files;

  try {
    MailApp.sendEmail({
      to: TO,
      replyTo: inquiry.email,
      name: SENDER_NAME,
      subject: 'Inquiry from ' + inquiry.name + (inquiry.company ? ' (' + inquiry.company + ')' : '') + ' — ' + inquiry.projectType,
      body: renderText(inquiry),
      htmlBody: renderHtml(inquiry),
      attachments: inquiry.attachments.map((f) => f.blob),
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

// `raw` is a JSON array of { name, type, data (base64) } sent by contact-form.js.
function parseAttachments(raw) {
  if (!raw) return { files: [] };

  let list;
  try {
    list = JSON.parse(raw);
  } catch (err) {
    return { error: 'Could not read your attachments. Please try again.' };
  }
  if (!Array.isArray(list)) return { error: 'Could not read your attachments. Please try again.' };
  if (list.length > MAX_FILES) return { error: 'Please attach up to ' + MAX_FILES + ' files.' };

  const files = [];
  let total = 0;
  for (const item of list) {
    const name = oneLine(item && item.name, 120).replace(/[\\/:*?"<>|]/g, '_');
    if (!ALLOWED_EXT.test(name) || typeof item.data !== 'string') {
      return { error: '“' + (name || 'A file') + '” isn’t a supported file type.' };
    }
    const bytes = Utilities.base64Decode(item.data);
    total += bytes.length;
    if (total > MAX_TOTAL_BYTES) return { error: 'Attachments must be 10 MB or less in total.' };
    const type = oneLine(item.type, 100) || 'application/octet-stream';
    files.push({ name: name, size: bytes.length, blob: Utilities.newBlob(bytes, type, name) });
  }
  return { files: files };
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return Math.max(1, Math.round(bytes / 1024)) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function renderText(q) {
  const files = q.attachments.map((f) => f.name + ' (' + formatSize(f.size) + ')');
  return [
    'New inquiry from ' + q.name,
    q.receivedAt,
    '',
    'Name: ' + q.name,
    'Email: ' + q.email,
    'Company: ' + (q.company || '—'),
    'Project type: ' + q.projectType,
    '',
    'Message:',
    q.message,
    '',
  ].concat(files.length ? ['Attachments: ' + files.join(', '), ''] : []).concat([
    '--',
    'stackcone · https://stackcone.com · hello@stackcone.com',
  ]).join('\n');
}

function renderHtml(q) {
  const row = (label, valueHtml, last) =>
    '<tr>' +
      '<td valign="top" style="' + FONT + 'width:120px;padding:12px 0;font-size:13px;line-height:20px;color:#6b6b6b;' + (last ? '' : 'border-bottom:1px solid #f0f0f0;') + '">' + label + '</td>' +
      '<td valign="top" style="' + FONT + 'padding:12px 0;font-size:15px;line-height:20px;color:#1a1a1a;word-break:break-word;' + (last ? '' : 'border-bottom:1px solid #f0f0f0;') + '">' + valueHtml + '</td>' +
    '</tr>';

  const email = esc(q.email);
  const details =
    row('Name', '<strong>' + esc(q.name) + '</strong>') +
    row('Email', '<a href="mailto:' + email + '" style="color:#1a1a1a;text-decoration:underline;">' + email + '</a>') +
    row('Company', q.company ? esc(q.company) : '<span style="color:#9a9a9a;">—</span>') +
    row('Project type',
      '<span style="display:inline-block;padding:3px 10px;border-radius:999px;background:#1a1a1a;color:#ffffff;font-size:12px;line-height:18px;font-weight:600;">' + esc(q.projectType) + '</span>',
      true);

  return '<!doctype html><html><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light"></head>' +
    '<body style="margin:0;padding:0;background:#f4f4f4;">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f4f4f4;">' +
    '<tr><td align="center" style="padding:32px 16px;">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#ffffff;border:1px solid #e5e5e5;border-radius:12px;border-collapse:separate;">' +

      // Header: logo + label
      '<tr><td style="padding:24px 32px;border-bottom:1px solid #ebebeb;">' +
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>' +
          '<td valign="middle"><a href="https://stackcone.com/" style="text-decoration:none;">' +
            '<img src="' + LOGO_URL + '" width="150" height="32" alt="stackcone" style="display:block;border:0;outline:none;height:32px;width:150px;"></a></td>' +
          '<td valign="middle" align="right" style="' + FONT + 'font-size:11px;line-height:16px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#6b6b6b;">Project inquiry</td>' +
        '</tr></table>' +
      '</td></tr>' +

      // Title
      '<tr><td style="padding:28px 32px 4px;">' +
        '<h1 style="' + FONT + 'margin:0 0 6px;font-size:22px;line-height:30px;font-weight:700;color:#1a1a1a;">New inquiry from ' + esc(q.name) + '</h1>' +
        '<p style="' + FONT + 'margin:0;font-size:13px;line-height:20px;color:#6b6b6b;">' + esc(q.receivedAt) + '</p>' +
      '</td></tr>' +

      // Details
      '<tr><td style="padding:16px 32px 0;">' +
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">' + details + '</table>' +
      '</td></tr>' +

      // Message
      '<tr><td style="padding:24px 32px 32px;">' +
        '<p style="' + FONT + 'margin:0 0 10px;font-size:13px;line-height:20px;color:#6b6b6b;">Message</p>' +
        '<div style="' + FONT + 'background:#f7f7f7;border:1px solid #ebebeb;border-radius:8px;padding:16px 18px;font-size:15px;line-height:24px;color:#1a1a1a;word-break:break-word;">' +
          esc(q.message).replace(/\n/g, '<br>') +
        '</div>' +
      '</td></tr>' +

      // Attachments (files themselves are attached to the email)
      (q.attachments.length
        ? '<tr><td style="padding:0 32px 32px;">' +
            '<p style="' + FONT + 'margin:0 0 10px;font-size:13px;line-height:20px;color:#6b6b6b;">Attachments (' + q.attachments.length + ')</p>' +
            q.attachments.map((f) =>
              '<div style="' + FONT + 'margin:0 0 8px;padding:10px 14px;border:1px solid #ebebeb;border-radius:8px;font-size:14px;line-height:20px;color:#1a1a1a;word-break:break-word;">' +
                '📎 <strong>' + esc(f.name) + '</strong> <span style="color:#6b6b6b;">· ' + formatSize(f.size) + '</span>' +
              '</div>').join('') +
          '</td></tr>'
        : '') +

      // Footer
      '<tr><td style="' + FONT + 'padding:18px 32px;background:#fafafa;border-top:1px solid #ebebeb;border-radius:0 0 12px 12px;font-size:12px;line-height:19px;color:#6b6b6b;">' +
        '<strong style="color:#1a1a1a;">stackcone</strong> · Production RAG chatbots, AI agents &amp; full-stack software<br>' +
        '<a href="https://stackcone.com/" style="color:#404040;text-decoration:none;">stackcone.com</a> · ' +
        '<a href="mailto:hello@stackcone.com" style="color:#404040;text-decoration:none;">hello@stackcone.com</a>' +
      '</td></tr>' +

    '</table></td></tr></table></body></html>';
}

// Single-line field: collapse whitespace/newlines (also keeps the subject line clean).
function oneLine(value, max) {
  return String(value || '').replace(/\s+/g, ' ').trim().slice(0, max);
}

function esc(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
