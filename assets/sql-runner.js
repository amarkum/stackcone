(function () {
  var SQLJS_VERSION = '1.10.3';
  var SQLJS_BASE = 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/' + SQLJS_VERSION + '/';

  // The lesson database. Every Run starts from this snapshot, so a DELETE in one
  // snippet never surprises the next one. Tables are declared once here and used
  // for both the seed SQL and the sample-data panel, so the two cannot drift.
  var TABLES = [
    {
      name: 'customers',
      ddl: 'CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT, ' +
        'age INTEGER, email TEXT UNIQUE, phone TEXT)',
      columns: ['id', 'name', 'country', 'age', 'email', 'phone'],
      rows: [
        [1, 'Ada', 'UK', 36, 'ada@example.com', '+44 20 7946 0958'],
        [2, 'Linus', 'FI', 28, 'linus@example.com', null],
        [3, 'Grace', 'US', 45, 'grace@example.com', '+1 202 555 0143']
      ],
      open: true
    },
    {
      name: 'orders',
      ddl: 'CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), ' +
        'total REAL, status TEXT)',
      columns: ['id', 'customer_id', 'total', 'status'],
      rows: [
        [10, 1, 120.0, 'paid'],
        [11, 1, 35.5, 'paid'],
        [12, 3, 80.0, 'refunded']
      ],
      open: true
    },
    {
      name: 'people',
      ddl: 'CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)',
      columns: ['id', 'name', 'age'],
      rows: [[1, 'Ada', 36], [2, 'Linus', 28], [3, 'Zed', null]]
    },
    {
      name: 'employees',
      ddl: 'CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, manager_id INTEGER REFERENCES employees(id), ' +
        'department TEXT, salary INTEGER, hire_date TEXT)',
      columns: ['id', 'name', 'manager_id', 'department', 'salary', 'hire_date'],
      rows: [
        [1, 'Grace', null, 'Engineering', 190000, '2015-03-02'],
        [2, 'Ada', 1, 'Engineering', 150000, '2017-06-15'],
        [3, 'Linus', 1, 'Engineering', 120000, '2019-01-07'],
        [4, 'Margaret', null, 'Design', 140000, '2016-11-20'],
        [5, 'Alan', 4, 'Design', 110000, '2018-04-03'],
        [6, 'Barbara', 4, 'Design', 110000, '2020-09-14']
      ]
    },
    {
      name: 'transactions',
      ddl: 'CREATE TABLE transactions (id INTEGER PRIMARY KEY, country TEXT, state TEXT, amount INTEGER, trans_date TEXT)',
      columns: ['id', 'country', 'state', 'amount', 'trans_date'],
      rows: [
        [121, 'US', 'approved', 1000, '2018-12-18'],
        [122, 'US', 'declined', 2000, '2018-12-19'],
        [123, 'US', 'approved', 2000, '2019-01-01'],
        [124, 'DE', 'approved', 2000, '2019-01-07'],
        [125, 'DE', 'declined', 500, '2019-01-22']
      ]
    },
    {
      name: 'weather',
      ddl: 'CREATE TABLE weather (id INTEGER PRIMARY KEY, record_date TEXT, temperature INTEGER)',
      columns: ['id', 'record_date', 'temperature'],
      rows: [
        [1, '2015-01-01', 10],
        [2, '2015-01-02', 25],
        [3, '2015-01-03', 20],
        [4, '2015-01-04', 30]
      ]
    },
    {
      name: 'activity',
      ddl: 'CREATE TABLE activity (player_id INTEGER, device_id INTEGER, event_date TEXT, games_played INTEGER, ' +
        'PRIMARY KEY (player_id, event_date))',
      columns: ['player_id', 'device_id', 'event_date', 'games_played'],
      rows: [
        [1, 2, '2016-03-01', 5],
        [1, 2, '2016-03-02', 6],
        [2, 3, '2016-03-01', 1],
        [3, 1, '2016-03-02', 0],
        [3, 4, '2018-07-03', 5]
      ]
    },
    {
      name: 'tree',
      ddl: 'CREATE TABLE tree (id INTEGER PRIMARY KEY, p_id INTEGER)',
      columns: ['id', 'p_id'],
      rows: [[1, null], [2, 1], [3, 1], [4, 2], [5, 2]]
    },
    {
      name: 'visits',
      ddl: 'CREATE TABLE visits (visit_id INTEGER PRIMARY KEY, customer_id INTEGER)',
      columns: ['visit_id', 'customer_id'],
      rows: [[1, 23], [2, 9], [4, 30], [5, 54], [6, 96], [7, 54], [8, 54]]
    },
    {
      name: 'purchases',
      ddl: 'CREATE TABLE purchases (purchase_id INTEGER PRIMARY KEY, visit_id INTEGER REFERENCES visits(visit_id), amount INTEGER)',
      columns: ['purchase_id', 'visit_id', 'amount'],
      rows: [[12, 1, 910], [13, 2, 970], [14, 6, 221], [15, 7, 190]]
    },
    {
      name: 'person',
      ddl: 'CREATE TABLE person (id INTEGER PRIMARY KEY, email TEXT)',
      columns: ['id', 'email'],
      rows: [
        [1, 'ada@example.com'],
        [2, 'linus@example.com'],
        [3, 'ada@example.com'],
        [4, 'GRACE@example.com ']
      ]
    },
    {
      name: 'products',
      ddl: 'CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)',
      columns: ['id', 'name', 'price', 'stock'],
      rows: [[1, 'Keyboard', 49.0, 12], [2, 'Monitor', 180.0, 4], [3, 'Cable', 9.5, 120]]
    },
    {
      name: 'accounts',
      ddl: 'CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance REAL)',
      columns: ['id', 'owner', 'balance'],
      rows: [[1, 'Ada', 100], [2, 'Linus', 20]]
    },
    {
      name: 'users',
      ddl: 'CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT)',
      columns: ['id', 'email', 'name'],
      rows: [
        [1, 'ada@example.com', 'Ada'],
        [2, 'linus@example.com', 'Linus'],
        [3, 'grace@example.com', 'Grace']
      ]
    }
  ];

  function literal(v) {
    if (v === null || v === undefined) return 'NULL';
    if (typeof v === 'number') return String(v);
    return "'" + String(v).replace(/'/g, "''") + "'";
  }

  function buildSeed() {
    var out = ['PRAGMA foreign_keys = ON;'];
    TABLES.forEach(function (t) {
      out.push(t.ddl + ';');
      var values = t.rows.map(function (row) {
        return '(' + row.map(literal).join(',') + ')';
      });
      out.push('INSERT INTO ' + t.name + ' VALUES ' + values.join(',') + ';');
    });
    return out.join('\n');
  }

  var SEED = buildSeed();

  function loadSqlJsScript() {
    return new Promise(function (resolve, reject) {
      if (typeof window.initSqlJs === 'function') {
        resolve(window.initSqlJs);
        return;
      }
      var existing = document.querySelector('script[data-sqljs]');
      if (existing) {
        existing.addEventListener('load', function () { resolve(window.initSqlJs); });
        existing.addEventListener('error', reject);
        return;
      }
      var script = document.createElement('script');
      script.src = SQLJS_BASE + 'sql-wasm.js';
      script.setAttribute('data-sqljs', 'true');
      script.onload = function () { resolve(window.initSqlJs); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function getSql() {
    if (!window.__stackconeSqlJsPromise) {
      window.__stackconeSqlJsPromise = loadSqlJsScript().then(function (initSqlJs) {
        return initSqlJs({ locateFile: function (file) { return SQLJS_BASE + file; } });
      });
    }
    return window.__stackconeSqlJsPromise;
  }

  // Lessons that teach CREATE TABLE / ALTER TABLE redefine things the seed already
  // has. Clear those out first so the snippet's own definition is the one that runs.
  function clearRedefined(db, code) {
    var re = /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"[]?([A-Za-z_][\w$]*)[`"\]]?/gi;
    var names = [];
    var m;
    while ((m = re.exec(code))) names.push(m[1]);
    if (names.length) {
      // Seed tables reference each other, so a drop in the wrong order trips a
      // foreign key. Order does not matter with the checks off.
      db.run('PRAGMA foreign_keys = OFF;');
      names.forEach(function (name) {
        try { db.run('DROP TABLE IF EXISTS "' + name + '";'); } catch (e) { /* keep going */ }
      });
      db.run('PRAGMA foreign_keys = ON;');
    }

    var alter = /ALTER\s+TABLE\s+[`"[]?([A-Za-z_][\w$]*)[`"\]]?\s+ADD\s+(?:COLUMN\s+)?[`"[]?([A-Za-z_][\w$]*)/gi;
    while ((m = alter.exec(code))) {
      try { db.run('ALTER TABLE "' + m[1] + '" DROP COLUMN "' + m[2] + '";'); } catch (e) { /* column not there */ }
    }
  }

  // sqlite3_changes() covers only the last statement, so count real writes with
  // total_changes() on either side.
  function totalChanges(db) {
    try {
      var r = db.exec('SELECT total_changes();');
      return r.length ? r[0].values[0][0] : 0;
    } catch (e) {
      return 0;
    }
  }

  // Split on semicolons that are not inside a string, an identifier or a comment,
  // so each statement can be echoed above its own output.
  function splitStatements(code) {
    var out = [];
    var buf = '';
    var i = 0;
    while (i < code.length) {
      var ch = code.charAt(i);
      var next = code.charAt(i + 1);
      if (ch === '-' && next === '-') {
        var nl = code.indexOf('\n', i);
        if (nl === -1) nl = code.length;
        buf += code.slice(i, nl);
        i = nl;
        continue;
      }
      if (ch === '/' && next === '*') {
        var end = code.indexOf('*/', i + 2);
        end = end === -1 ? code.length : end + 2;
        buf += code.slice(i, end);
        i = end;
        continue;
      }
      if (ch === "'" || ch === '"' || ch === '`') {
        var close = i + 1;
        while (close < code.length) {
          if (code.charAt(close) === ch) {
            if (code.charAt(close + 1) === ch) { close += 2; continue; }
            break;
          }
          close++;
        }
        buf += code.slice(i, close + 1);
        i = close + 1;
        continue;
      }
      if (ch === ';') {
        i++;
        // A comment trailing the semicolon on the same line belongs to the
        // statement that just ended, not to the next one.
        var rest = code.slice(i);
        var trailing = rest.match(/^[ \t]*--[^\n]*/);
        if (trailing) {
          buf += ';' + trailing[0];
          i += trailing[0].length;
          out.push(buf.replace(/;(?=[ \t]*--)/, ''));
        } else {
          out.push(buf);
        }
        buf = '';
        continue;
      }
      buf += ch;
      i++;
    }
    out.push(buf);
    return out.filter(function (s) {
      // Drop fragments that are only whitespace or comments.
      return s.replace(/--[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '').trim().length > 0;
    }).map(function (s) { return s.trim(); });
  }

  function cellText(v) {
    if (v === null || v === undefined) return 'NULL';
    if (v instanceof Uint8Array) return '<blob>';
    return String(v);
  }

  // sqlite3's default output: columns padded and separated by ' | ', with a rule
  // of dashes under the header.
  function asciiTable(columns, values) {
    var widths = columns.map(function (c) { return String(c).length; });
    var rows = values.map(function (row) {
      return row.map(function (cell, i) {
        var text = cellText(cell);
        if (text.length > widths[i]) widths[i] = text.length;
        return text;
      });
    });

    function pad(text, i) {
      return text + new Array(widths[i] - text.length + 1).join(' ');
    }

    var lines = [];
    lines.push(columns.map(function (c, i) { return pad(String(c), i); }).join(' | ').replace(/\s+$/, ''));
    lines.push(widths.map(function (w) { return new Array(w + 2).join('-'); }).join('+'));
    rows.forEach(function (row) {
      lines.push(row.map(pad).join(' | ').replace(/\s+$/, ''));
    });
    return lines.join('\n');
  }

  // Put the semicolon where sqlite would print it: after the statement itself,
  // not after a comment that trails it on the same line.
  function leadingKeyword(stmt) {
    var m = stmt.replace(/^(?:\s|--[^\n]*\n|\/\*[\s\S]*?\*\/)*/, '').match(/^[A-Za-z]+/);
    return m ? m[0].toUpperCase() : '';
  }

  function isRead(stmt) {
    var kw = leadingKeyword(stmt);
    return kw === 'SELECT' || kw === 'WITH' || kw === 'EXPLAIN' || kw === 'PRAGMA' || kw === 'VALUES';
  }

  function isWrite(stmt) {
    return /^\s*(?:--[^\n]*\n|\/\*[\s\S]*?\*\/|\s)*(INSERT|UPDATE|DELETE|REPLACE)\b/i.test(stmt);
  }

  function echoText(stmt) {
    var m = stmt.match(/^([\s\S]*?)(\s*--[^\n]*)$/);
    return m ? m[1].replace(/\s+$/, '') + ';' + m[2] : stmt + ';';
  }

  // Echoed statements get the same highlighting as the editor above them.
  function colorize(text) {
    if (!window.monaco || !window.monaco.editor || !window.monaco.editor.colorize) {
      return Promise.resolve(null);
    }
    try {
      return Promise.resolve(window.monaco.editor.colorize(text, 'sql', {})).catch(function () {
        return null;
      });
    } catch (e) {
      return Promise.resolve(null);
    }
  }

  // EXPLAIN QUERY PLAN returns id/parent/notused alongside the plan text. Those
  // first three are internal bookkeeping (one is literally called "notused" and
  // its value differs between SQLite builds), so print the plan alone.
  function planOnly(result) {
    var cols = result.columns;
    if (cols.length === 4 && cols[0] === 'id' && cols[1] === 'parent' && cols[3] === 'detail') {
      return {
        columns: ['detail'],
        values: result.values.map(function (row) { return [row[3]]; })
      };
    }
    return result;
  }

  function runSql(code, outputEl, runBtn) {
    if (!code || !code.trim()) {
      outputEl.textContent = '(no SQL to run)';
      outputEl.hidden = false;
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    outputEl.hidden = false;
    outputEl.classList.remove('is-error');
    outputEl.classList.add('learn-code-output--sql');
    outputEl.textContent = 'Loading SQLite…';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.classList.add('is-loading');
    }

    return getSql()
      .then(function (SQL) {
        var db = new SQL.Database();
        db.run(SEED);
        clearRedefined(db, code);

        var statements = splitStatements(code);
        // With one statement the echo would just repeat the editor above it.
        var echo = statements.length > 1;
        var steps = [];
        var failed = false;

        for (var i = 0; i < statements.length; i++) {
          var stmt = statements[i];
          var step = { sql: echoText(stmt), text: '', error: false };
          var before = totalChanges(db);
          try {
            var results = db.exec(stmt);
            var printed = [];
            results.forEach(function (result) {
              if (result.columns && result.columns.length) {
                var shaped = planOnly(result);
                printed.push(asciiTable(shaped.columns, shaped.values));
              }
            });
            if (printed.length) {
              step.text = printed.join('\n\n');
            } else {
              var changes = totalChanges(db) - before;
              // A DELETE that matched nothing is worth saying out loud; a CREATE
              // or BEGIN has no row count to report.
              // A query that matched nothing returns no columns at all in sql.js.
              step.text = isRead(stmt) ? '(no rows)'
                : changes === 1 ? '1 row affected.'
                : changes > 0 || isWrite(stmt) ? changes + ' rows affected.'
                : 'OK';
            }
          } catch (err) {
            step.text = 'Error: ' + (err && err.message ? err.message : String(err));
            step.error = true;
            failed = true;
            steps.push(step);
            break;
          }
          steps.push(step);
        }

        db.close();
        outputEl.classList.toggle('is-error', failed && !echo);

        if (!echo) {
          outputEl.classList.remove('learn-code-output--steps');
          outputEl.textContent = steps.length ? steps[0].text : 'OK';
          return;
        }

        return Promise.all(steps.map(function (step) { return colorize(step.sql); }))
          .then(function (html) {
            outputEl.textContent = '';
            outputEl.classList.add('learn-code-output--steps');
            steps.forEach(function (step, i) {
              var wrap = document.createElement('div');
              wrap.className = 'sql-step';

              var sql = document.createElement('div');
              sql.className = 'sql-step-sql';
              if (html[i]) sql.innerHTML = html[i];
              else sql.textContent = step.sql;
              wrap.appendChild(sql);

              var out = document.createElement('pre');
              out.className = 'sql-step-out';
              if (step.error) out.classList.add('is-error');
              out.textContent = step.text;
              wrap.appendChild(out);

              outputEl.appendChild(wrap);
            });
          });
      })
      .catch(function (err) {
        outputEl.textContent = 'Failed to load SQLite: ' + (err.message || err);
        outputEl.classList.add('is-error');
      })
      .finally(function () {
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.classList.remove('is-loading');
        }
      });
  }

  // A reference card of the data every Run starts from, so learners can read a
  // query without scrolling back to lesson 1.
  function buildSchemaPanel() {
    var card = document.createElement('section');
    card.className = 'sql-seed-card';

    var head = document.createElement('div');
    head.className = 'sql-seed-head';
    var title = document.createElement('h2');
    title.className = 'sql-seed-title';
    title.textContent = 'The lesson database';
    var sub = document.createElement('p');
    sub.className = 'sql-seed-sub';
    sub.textContent = 'Every Run starts from this data, so you can edit any snippet and re-run it freely.';
    head.appendChild(title);
    head.appendChild(sub);
    card.appendChild(head);

    TABLES.forEach(function (t) {
      var details = document.createElement('details');
      details.className = 'sql-seed-table';
      if (t.open) details.open = true;

      var summary = document.createElement('summary');
      var name = document.createElement('span');
      name.className = 'sql-seed-name';
      name.textContent = t.name;
      var count = document.createElement('span');
      count.className = 'sql-seed-count';
      count.textContent = t.rows.length === 1 ? '1 row' : t.rows.length + ' rows';
      summary.appendChild(name);
      summary.appendChild(count);
      details.appendChild(summary);

      var pre = document.createElement('pre');
      pre.className = 'sql-seed-pre';
      pre.textContent = asciiTable(t.columns, t.rows);
      details.appendChild(pre);

      card.appendChild(details);
    });

    return card;
  }

  function insertSchemaPanel() {
    if (!/\/sql\//.test(location.pathname || '')) return;
    var article = document.querySelector('article.learn-lesson');
    if (!article || article.querySelector('.sql-seed-card')) return;

    // Sit above the lesson's first real section, below the objectives block.
    var anchor = null;
    // Only a top-level h2 starts a lesson section; the ones inside the objectives
    // and progress widgets are nested.
    var heads = article.children;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].tagName === 'H2') {
        anchor = heads[i];
        break;
      }
    }
    var panel = buildSchemaPanel();
    if (anchor) anchor.parentNode.insertBefore(panel, anchor);
    else article.appendChild(panel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertSchemaPanel);
  } else {
    insertSchemaPanel();
  }

  window.stackconeRunSql = runSql;
  window.stackconeSqlSeed = SEED;
})();
